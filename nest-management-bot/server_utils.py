"""
All the utilities used by server.py to make life easier lol
"""
import asyncio
import hashlib
import json

import humanize
import psutil
import secrets
#import socket
from typing import Optional



clients = {}


def get_uptime() -> str:
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return humanize.naturaltime(uptime_seconds)


async def send_message(message: str, user_uuid: str) -> None:
    """
    Send a message to the client
    :param message: The message to send
    :param user_uuid: The client to send a message to
    :return:
    """
    await clients[user_uuid].send(json.dumps({'status': 'info', 'message': message}))


async def send_command(message: str, user_uuid: str, *, payload: Optional[dict] = None) -> Optional[dict]:
    """
    Send a command to the client
    :param message: The message to send
    :param user_uuid: The client to send a message to
    :param payload: The payload to send (optional)
    :return: The client's response to the command
    """
    client = clients[user_uuid]
    command_to_send = {
        'status': 'command',
        'message': message
    }
    if payload:
        command_to_send["payload"] = payload
    await client.send(json.dumps(command_to_send))

    try:
        async with asyncio.timeout(1):
            response_json = await client.recv()
            print(response_json)
    except asyncio.TimeoutError:
        await send_error('Wheres my response? Did not receive a command_response.', user_uuid)
        return

    try:
        response = json.loads(response_json)
    except json.decoder.JSONDecodeError:
        await send_error('Response was not JSON.', user_uuid)
        return

    if response.get('status') in ['command_response', 'command_response_error']:
        return response
    else:
        raise ValueError(f"Response was not of valid type ({response.get('status', 'no status?!?')}), code is cashing out")


async def send_error(error_msg, user_uuid: str, *, possible=False, disconnect=True) -> None:
    """
    Send an error to the client
    :param error_msg: The error to send
    :param user_uuid: The client to send a message to
    :param possible: If this error is possible with a correct client
    :param disconnect: Disconnect the server after the error message is sent
    :return:
    """
    await clients[user_uuid].send(json.dumps(
        {
            'message': f"{error_msg}{' This shouldn\'t happen, send a message in #slack-management-bot for help.' if not possible else ''}",
            'status': 'error'
        }
    ))
    if disconnect:
        await clients[user_uuid].close()


def generate_token() -> str:
    """
    Generates a token to be used for authentication
    :return: A token
    """
    raw_token = secrets.token_hex(32)

    checksum = hashlib.sha256(raw_token.encode()).hexdigest()[:8]
    final_token = f"{raw_token}.{checksum}"

    # Sanity Check
    if verify_token_checksum(final_token):
        return final_token
    else:
        raise Exception("How on earth do you generate a token invalid? :heavysob:")


def verify_token_checksum(token: str) -> bool:
    """
    Verifies the checksum of a token
    :param token: The token to verify
    :return: Weather the checksum is valid
    """
    if len(token) != 73: # Token must be 73 chars long
        return False

    raw_token = token[:-9] # Obtain raw token, minus the seperator (.)
    checksum = token[-8:] # Obtain checksum

    expected_checksum = hashlib.sha256(raw_token.encode()).hexdigest()[:8]
    return expected_checksum == checksum


def get_global_resources():
    """
    Get resources and info for the entirety of Nest
    :return: A list of services
    """
    mem_info = psutil.virtual_memory()
    storage_info = psutil.disk_usage('/')
    return {
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.1),
            "cores": psutil.cpu_count(),
        "mem": {
            "total": mem_info.total,
            "used": mem_info.total - mem_info.available,
        },
        "storage": {
            "total": storage_info.total,
            "used": storage_info.used
        },
        "uptime": get_uptime()
    }


def unit_converter(value: float, unit: str) -> str:
    """
    Converts any value given in bytes to the specified unit
    :return: Converted value
    """
    if unit.lower() == "gb":
        return f"{round(value / 10**9, 3)} GB"
    elif unit.lower() == "gib":
        return f"{round(value / 1024**3, 3)} GiB"
    elif unit.lower() == "bytes":
        return f"{value} Bytes"
    else:
        raise ValueError(f"Invalid unit specified, what on earth is a {unit}?!?")

if __name__ == "__main__":
    print(generate_token())