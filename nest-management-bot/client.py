import asyncio
import json
import os
import ssl
import subprocess
from typing import Literal

#import dbus
import psutil
from websockets.asyncio.client import connect

from dotenv import load_dotenv

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

    print("Attempting to connect to server...")
    async for websocket in connect(uri):#, ssl=ssl_context):
        print("Connected to server...")
        #atexit.register(await websocket.close()) # Register exit handler

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
            server_response = await asyncio.wait_for(websocket.recv(), timeout=60)
        except asyncio.TimeoutError:
            raise Exception("Server did not respond in time") from None

        if server_response.get('status') == 'error':
            raise Exception(f"errors make code sad :( - {server_response.get('message')}")

        async for message_json in websocket:
            try:
                message = json.loads(message_json)
            except json.decoder.JSONDecodeError:
                raise Exception('Broke the server code prob lol') # TODO: Replace w/ better handling

            msg_status = message.get('status')
            msg_data = message.get('message')
            if msg_status == 'command':
                websocket.send(json.dumps(command_handler(msg_status, msg_data.get('payload'))))
            elif msg_status == 'error':
                print(f'ERROR: {msg_data}')
            elif msg_status == 'info':
                print(f'MESSAGE: {msg_data}')
            else:
                print(f'Message of unknown "{msg_status}" type: {msg_data}')


def command_handler(status: str, payload: dict) -> dict:
    if status == "obtain_all_process_info":
        """
        Lists running processes and associated systemd data if it exists 
        """
        process_data = []
        for process in psutil.process_iter():
            process_data.append({
                "pid": process.pid,
                "name": process.name(),
            })

        return {
            "status": "command_response",
            "payload": process_data
        }

    elif status == "obtain_process_info":
        """
        Provides information about a specific process
        """
        # Get process
        process = psutil.Process(payload.get('pid'))
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
                "status": process.status()
            }
        }

    elif status == "kill_process":
        try:
            process = psutil.Process(payload['pid'])
            process.kill()
        except Exception as error:
            return {
                "status": "command_response_error",
                "message": f"Process was not killed. Error: {error}"
            }

    elif status == "start_service":
        try:
            manage_systemd_service(payload['service_name'], "start")
            return {
                "status": "command_response",
                "message": "response_start_service"
            }
        except dbus.DBusException as error:
            return {
                "status": "command_response_error",
                "message": "response_start_service",
                "payload": {
                    "error": f"Service was not started. Error: {error}"
                }
            }

    elif status == "stop_service":
        try:
            manage_systemd_service(payload['service_name'], "stop")
            return {
                "status": "command_response",
                "message": "response_stop_service"
            }
        except dbus.DBusException as error:
            return {
                "status": "command_response_error",
                "message": "response_stop_service",
                "payload": {
                    "error": f"Service was not stopped. Error: {error}"
                }
            }

    elif status == "restart_service":
        try:
            manage_systemd_service(payload['service_name'], "restart")
            return {
                "status": "command_response",
                "message": "response_restart_service",
            }
        except dbus.DBusException as error:
            return {
                "status": "command_response_error",
                "message": "response_restart_service",
                "payload": {
                    "error": f"Service was not restarted. Error: {error}"
                }
            }
    elif status == "reload_service":
        try:
            manage_systemd_service(payload['service_name'], "reload")
            return {
                "status": "command_response",
                "message": f"response_reload_service"
            }
        except dbus.DBusException as error:
            return {
                "status": "command_response_error",
                "message": "response_reload_service",
                "payload": {
                    "error": f"Service was not reloaded. Error: {error}"
                }
            }
    elif status == "exec_command":
        ... # uhhh, unused for now lol (idk weather this will exist)



if __name__ == "__main__":
    print(f"Starting client websocket... version: {__version__}")
    asyncio.run(client())
