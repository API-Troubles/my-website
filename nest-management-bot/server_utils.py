"""
All the utilities used by server.py to make life easier lol
"""
import asyncio
import hashlib
import secrets
import json
import socket
from typing import Optional
#import dbus # Does not work cause well... my dev


# DBus bindings to systemd
"""
session_bus = dbus.SessionBus()
systemd = session_bus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
manager = dbus.Interface(systemd, 'org.freedesktop.systemd1.Manager')"""

clients = {}


class ClientError(Exception):
    pass


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

    if response.get('status') == 'command_response':
        return response
    elif response.get('status') == 'error':
        raise ClientError(response.get('message'))
    else:
        await send_error('Response did not have a valid status value.', user_uuid)


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
            'message': f'{error_msg}{' This shouldn\'t happen, send a message in #slack-management-bot for help.' if not possible else ''}',
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
    Get a list of systemd processes which the user has
    :return: A list of services
    """
    return {
        "cpu": "40%",
        "mem": "45/400MB",
        "storage": "42.234GB/100GB",
    }

if __name__ == "__main__":
    print(generate_token())