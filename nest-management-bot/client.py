import asyncio
import json
import os
import ssl
import subprocess

import psutil
from websockets.asyncio.client import connect

from dotenv import load_dotenv

__version__ = "0.1.0a" # Use for later version checking


status_emojis = {
    "running": "🏃",
    "sleeping": "😴",
    "zombie": "🧟",
    "stopped": "⏹️",
    "disk-sleep": "💽"
}

load_dotenv(dotenv_path='.env.nest-management-bot')


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
    uri = "ws://localhost:8989"

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
                    'token': os.environ['CLIENT_TOKEN']
                }
            }
        ))

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

        return process_data

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
        process = psutil.Process(payload.get('pid'))
        try:
            process.kill()
        except:
            return {
                "status": "error",
                "message": "Process was not killed"
            }
    elif status == "restart_process":
        ...
    elif status == "start_process":
        ...
    elif status == "exec_command":
        ... # uhhh



if __name__ == "__main__":
    print(f"Starting client websocket... version: {__version__}")
    asyncio.run(client())
