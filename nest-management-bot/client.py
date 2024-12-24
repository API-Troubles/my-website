import asyncio
#import dbus
import json
import logging
import os
import psutil
import ssl
import signal
import subprocess
from typing import Literal
from websockets.asyncio.client import connect

from dotenv import load_dotenv

logging.basicConfig( # Set up logging for the guaranteed errors >:(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]:\t %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# DBus bindings to systemd
session_bus = dbus.SessionBus()
systemd = session_bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
systemd_manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')

__version__ = "0.1.0a" # Use for later version checking

load_dotenv(dotenv_path='.env.nest-management-bot')


def manage_systemd_service(service_name: str, action: Literal["start", "stop", "restart", "reload"]) -> None:
    """
    Manage a user service
    :param service_name: The service to stop
    :param action:
    :return:
    """
    logging.info(f"{action}ing {service_name}...")
    actions = {
        "start": systemd_manager.StartUnit,
        "stop": systemd_manager.StopUnit,
        "restart": systemd_manager.RestartUnit,
        "reload": systemd_manager.ReloadUnit,
    }

    if action not in actions:
        raise ValueError(f"Invalid action '{action}'")

    if not service_name.endswith(".service"): # Append with .service if i was stupid and hadn't alr
        service_name += ".service"

    actions[action](service_name, 'replace')
    logging.info(f"{action}ed {service_name} successfully")


def get_storage() -> list:
    """
    Get the storage used by the user
    :return: Files, folders, etc. in a list
    """
    result = subprocess.run(
        ["du", "--max-depth=1", "-c", "-b", os.getcwd()],
        capture_output=True,
        text=True,
        check=True
    )
    new_result = []
    for file_path in result.stdout.splitlines():
        split = file_path.split("\t")
        new_result.append(split)

    return new_result


def get_max_memory() -> float:
    output = subprocess.run(
        ["quota"],
        capture_output=True,
        text=True,
        check=True
    )

    quota_line = next((line for line in output.splitlines() if "/dev/" in line), None)
    extracted_line = list(map(int, re.findall(r"\d+", quota_line)))
    total_limit = extracted_line[3]

    return round(total_limit * 4 / 10**9, 3) # 4KB blocks multiplied by 10^9 to get GB :D


async def client():
    uri = "ws://0e72-135-0-146-179.ngrok-free.app/"

    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #ssl_context.load_verify_locations("cert.pem")

    logging.info("Attempting to connect to server...")
    async for websocket in connect(uri):#, ssl=ssl_context):
        logging.info("Connected to server... :D")

        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, loop.create_task, websocket.close())

        logging.info("Sending client token to server...")
        await websocket.send(json.dumps(
            {
                'status': "let_me_in_pls",
                'payload': {
                    'version': __version__,
                    'client_token': os.environ['CLIENT_TOKEN']
                }
            }
        ))

        try:
            logging.info("Waiting for response from server...")
            server_response = await asyncio.wait_for(websocket.recv(), timeout=60)
        except asyncio.TimeoutError:
            raise Exception("Server did not respond in time") from None

        try:
            server_response_json = json.loads(server_response)
        except json.decoder.JSONDecodeError:
            raise Exception('Broke the server code prob lol') # TODO: Replace w/ better handling

        if server_response_json.get('status') == 'error':
            raise ValueError(f"Server sent error message, we did a goof: {server_response_json.get('message')}")

        logging.info("Authenticated :D")

        async for message_json in websocket:
            try:
                logging.debug("Decoding response into json...")
                message = json.loads(message_json)
            except json.decoder.JSONDecodeError:
                raise ValueError(f"Server sent message which couldn't be decoded into json: '{message_json}'")

            msg_status = message.get('status')
            msg_data = message.get('message')
            if msg_status == 'command':
                logging.debug("Received message of type 'command'")
                await websocket.send(json.dumps(command_handler(msg_data, message.get('payload'))))
            elif msg_status == 'error':
                raise Exception(f"Received error from server: {msg_data}")
            else:
                raise ValueError(f'Server sent illegal message of "{msg_status}" type with data {msg_data}')


def command_handler(message: str, payload: dict) -> dict:
    logging.debug(f"Command of type '{message}' received")
    if message == "obtain_all_process_info":
        """
        Lists running processes and associated systemd data if it exists 
        """
        logging.info("Obtaining all process info...")
        process_data = []
        for process in psutil.process_iter():
            logging.debug(f"Getting process info for PID - {process.pid}")
            process_data.append({
                "pid": process.pid,
                "name": process.name(),
            })

        logging.info("Sending all process info to server...")
        return {
            "status": "command_response",
            "payload": process_data
        }

    elif message == "obtain_process_info":
        """
        Provides information about a specific process
        """
        # Get process
        try:
            process = psutil.Process(payload.get('pid'))
        except psutil.NoSuchProcess:
            logging.error(f"Could not find process with PID - {payload.get('pid')}")
            return {
                "status": "command_response_error",
                "message": "Could not get process info, it no longer exists :( You can safely close this error window and continue life as normal. (sry for the scare lol)",
                "payload": {
                    "pid": payload.get('pid')
                }
            }
        process_mem_info = process.memory_full_info()

        safe_to_kill = True
        if process.pid == os.getpid(): # Let's not kill ourselves
            safe_to_kill = False
        elif process.name() == "dbus-daemon": # Critical to this whole code running :/
            safe_to_kill = False

        logging.info("Sending process info to server...")
        return {
            "status": "command_response",
            "payload": {
                "pid": process.pid,
                "name": process.name(),
                "cpu_usage": process.cpu_percent(),
                "cpu_time": {
                    "user": process.cpu_times().user,
                    "system": process.cpu_times().system
                },
                "status": process.status(),
                "memory": {
                    "rss": process_mem_info.rss,
                    "swap": process_mem_info.swap,
                    "max": get_max_memory()
                },
                "started": process.create_time(),
                "safe_kill": safe_to_kill
            }
        }

    elif message == "kill_process":
        try:
            try:
                process = psutil.Process(payload.get('pid'))
            except psutil.NoSuchProcess:
                logging.error(f"Could not find process with PID - {payload.get('pid')}")
                return {
                    "status": "command_response_error",
                    "message": "Could not kill process, it no longer exists :( You can safely close this error window and continue life as normal. (sry for the scare lol)",
                    "payload": {
                        "pid": payload.get('pid')
                    }
                }
            process = psutil.Process(payload['pid'])
            process.terminate() # SIGTERM
            logging.info(f"Killed process with PID: {payload['pid']}")
            return {
                "status": "command_response",
                "message": "You're a killer now... >:( (process was killed successfully)"
            }
        except Exception as error:
            logging.error(f"Process was not killed - error: {error}")
            return {
                "status": "command_response_error",
                "message": f"Process was not killed. Error: {error}"
            }

    elif message == "list_services":
        ...

    elif message == "start_service":
        try:
            manage_systemd_service(payload['service_name'], "start")
            return {
                "status": "command_response",
                "message": "response_start_service"
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not started - error: {error}")
            return {
                "status": "command_response_error",
                "message": "response_start_service",
                "payload": {
                    "error": f"Service was not started. Error: {error}"
                }
            }

    elif message == "stop_service":
        try:
            manage_systemd_service(payload['service_name'], "stop")
            return {
                "status": "command_response",
                "message": "response_stop_service"
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not stopped - error: {error}")
            return {
                "status": "command_response_error",
                "message": "response_stop_service",
                "payload": {
                    "error": f"Service was not stopped. Error: {error}"
                }
            }

    elif message == "restart_service":
        try:
            manage_systemd_service(payload['service_name'], "restart")
            return {
                "status": "command_response",
                "message": "response_restart_service",
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not restarted - error: {error}")
            return {
                "status": "command_response_error",
                "message": "response_restart_service",
                "payload": {
                    "error": f"Service was not restarted. Error: {error}"
                }
            }
    elif message == "reload_service":
        try:
            manage_systemd_service(payload['service_name'], "reload")
            return {
                "status": "command_response",
                "message": f"response_reload_service"
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not reloaded - error: {error}")
            return {
                "status": "command_response_error",
                "message": "response_reload_service",
                "payload": {
                    "error": error
                }
            }
    elif message == "exec_command":
        ... # uhhh, unused for now lol (idk weather this will exist)
    else:
        raise ValueError(f"Server sent illegal command of type '{message}' and payload of '{payload}'")



if __name__ == "__main__":
    logger.info(f"Starting client websocket... version: {__version__}")
    asyncio.run(client())
