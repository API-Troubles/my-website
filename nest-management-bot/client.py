import asyncio
import dbus
import humanize
import json
import logging
import os
from datetime import datetime

import psutil
import re
import ssl
import signal
import subprocess
from typing import Literal
from websockets.asyncio.client import connect

from dotenv import load_dotenv

logging.basicConfig( # Set up logging for the guaranteed errors >:(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]:\t%(message)s',
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



def list_systemd_services() -> list:
    """
    List all services which exist to the user
    :return: List of services
    """
    units = systemd_manager.ListUnits()
    services = []
    for unit in units:
        if unit[0].endswith('.service'):
            service_name = unit[0]

            # All this chaos just to get the filepath of the file... thanks chatgpt for the help :pf:
            service_unit = systemd_manager.GetUnit(service_name)
            service_object = session_bus.get_object('org.freedesktop.systemd1', service_unit)
            service_interface = dbus.Interface(service_object, 'org.freedesktop.DBus.Properties')
            unit_path = service_interface.Get('org.freedesktop.systemd1.Unit', 'FragmentPath')

            # Check if the service file is in ~/.config/systemd/user
            if unit_path.startswith(os.path.expanduser('~/.config/systemd/user')):
                services.append(service_name)

    return services


def get_service_info(service_name: str) -> dict:
    """
    Get information on a specific service
    :return: List of services
    """
    if not service_name.endswith(".service"): # Append with .service if i was stupid and hadn't alr
        service_name += ".service"

    service_unit = systemd_manager.GetUnit(service_name)
    service_object = session_bus.get_object('org.freedesktop.systemd1', service_unit)
    service_interface = dbus.Interface(service_object, 'org.freedesktop.DBus.Properties')

    unit_path = service_interface.Get('org.freedesktop.systemd1.Unit', 'FragmentPath')
    main_pid = service_interface.Get('org.freedesktop.systemd1.Service', 'MainPID')
    start_timestamp = int(service_interface.Get('org.freedesktop.systemd1.Service', 'ExecMainStartTimestamp')) / 1_000_000

    uptime = None
    time_ago = None
    if main_pid > 0 and start_timestamp > 0:
        time_dt_object = datetime.fromtimestamp(start_timestamp)
        uptime = time_dt_object.strftime("%a %Y-%m-%d %H:%M:%S %Z")
        time_ago = humanize.naturaltime(time_dt_object)

    if uptime and time_ago:
        formatted_uptime = f"{uptime}; {time_ago}"
    else:
        formatted_uptime = "Unable to calculate :("

    return {
        'name': service_name,
        'description': service_interface.Get('org.freedesktop.systemd1.Unit', 'Description'),
        'active_state': service_interface.Get('org.freedesktop.systemd1.Unit', 'ActiveState'),
        'sub_state': service_interface.Get('org.freedesktop.systemd1.Unit', 'SubState'),
        'file_location': unit_path,
        'uptime': formatted_uptime,
        'pid': main_pid
    }


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
            raise ValueError(f"Server sent error, we did a goof: {server_response_json.get('message')}")

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
    if message == "obtain_user_usages":
        """
        Obtains the usage data for the user
        """
        result = subprocess.run(
            ["nest", "resources"],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("Sending usage data...")
        return {
            "status": "command_response",
            "payload": {
                "resources": result.stdout,
                "storage": get_storage()
            }
        }
    elif message == "obtain_all_process_info":
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
                    "swap": process_mem_info.swap
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
            if payload.get('method') == "SIGKILL": # the not so kind killing
                process.kill()
            elif payload.get('method') == "SIGTERM":  # nicely end a life
                process.terminate()
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

    elif message == "pause_process":
        try:
            try:
                process = psutil.Process(payload.get('pid'))
            except psutil.NoSuchProcess:
                logging.error(f"Could not find process with PID - {payload.get('pid')}")
                return {
                    "status": "command_response_error",
                    "message": "Could not pause process, it no longer exists :( You can safely close this error window and continue life as normal. (sry for the scare lol)",
                    "payload": {
                        "pid": payload.get('pid')
                    }
                }
            process.suspend()

            logging.info(f"Paused process with PID: {payload['pid']}")
            return {
                "status": "command_response",
                "message": "Poor process didn't even get a choice, it was just forced to SIGSTOP"
            }
        except Exception as error:
            logging.error(f"Process was not paused - error: {error}")
            return {
                "status": "command_response_error",
                "message": f"Process was not paused. Error: {error}"
            }

    elif message == "resume_process":
        try:
            try:
                process = psutil.Process(payload.get('pid'))
            except psutil.NoSuchProcess:
                logging.error(f"Could not find process with PID - {payload.get('pid')}")
                return {
                    "status": "command_response_error",
                    "message": "Could not resume process, it no longer exists :( You can safely close this error window and continue life as normal. (sry for the scare lol)",
                    "payload": {
                        "pid": payload.get('pid')
                    }
                }
            process.resume()

            logging.info(f"Resumed process with PID: {payload['pid']}")
            return {
                "status": "command_response",
                "message": "Keep going! The process is back in action (SIGCONT) :D"
            }
        except Exception as error:
            logging.error(f"Process was not resumed - error: {error}")
            return {
                "status": "command_response_error",
                "message": f"Process was not resumed. Error: {error}"
            }

    elif message == "list_services":
        logging.info("Listing all services...")
        return {
            "status": "command_response",
            "payload": list_systemd_services()
        }

    elif message == "obtain_service_info":
        logging.info(f"Getting info for service '{payload['service_name']}'")
        return {
            "status": "command_response",
            "payload": get_service_info(payload['service_name'])
        }

    elif message == "start_service":
        try:
            manage_systemd_service(payload['service_name'], "start")
            return {
                "status": "command_response",
                "message": "Started service, what a lovely day :D"
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not started - error: {error}")
            return {
                "status": "command_response_error",
                "payload": {
                    "error": f"Service was not started. Error: {repr(error)}"
                }
            }

    elif message == "stop_service":
        try:
            manage_systemd_service(payload['service_name'], "stop")
            return {
                "status": "command_response",
                "message": "Service stopped, what a sad day :("
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not stopped - error: {error}")
            return {
                "status": "command_response_error",
                "payload": {
                    "error": f"Service was not stopped. Error: {repr(error)}"
                }
            }

    elif message == "restart_service":
        try:
            manage_systemd_service(payload['service_name'], "restart")
            return {
                "status": "command_response",
                "message": "Service was given a bit of a mental restart ¯\_(ツ)_/¯",
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not restarted - error: {error}")
            return {
                "status": "command_response_error",
                "payload": {
                    "error": f"Service was not restarted. Error: {repr(error)}"
                }
            }

    elif message == "reload_service":
        try:
            manage_systemd_service(payload['service_name'], "reload")
            return {
                "status": "command_response",
                "message": f"Service was given a mental reload ¯\_(ツ)_/¯"
            }
        except dbus.DBusException as error:
            logging.error(f"Service was not reloaded - error: {error}")
            return {
                "status": "command_response_error",
                "payload": {
                    "error": f"Service was not reloaded. {repr(error)}"
                }
            }

    elif message == "get_port":
        result = subprocess.run(
            ["nest", "get_port"],
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "status": "command_response",
            "message": "Here's a port for you :D ~~stolen~~",
            "payload": result.stdout
        }

    else:
        raise ValueError(f"Server sent illegal command of type '{message}' and payload of '{payload}'")


if __name__ == "__main__":
    logging.info(f"Starting client websocket... version: {__version__}")
    asyncio.run(client())
