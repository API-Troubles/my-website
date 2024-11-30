"""
All the utilities used by server.py to make life easier lol
"""
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


async def send_command(message: str, user_uuid: str) -> Optional[dict]:
    """
    Send a command to the client
    :param message: The message to send
    :param user_uuid: The client to send a message to
    :return: The client's response to the command
    """
    await clients[user_uuid].send(json.dumps({'status': 'command', 'message': message}))
    response_json = await clients[user_uuid].recv()

    try:
        response = json.loads(response_json)
    except json.decoder.JSONDecodeError:
        await send_error(await clients[f'{user_uuid}'], 'Invalid Response', possible=False)
        return

    if response.get('status') == 'command_response':
        return response
    elif response.get('status') == 'error':
        raise ClientError(response.get('message'))
    else:
        await send_error(await clients[f'{user_uuid}'], 'Invalid Response type', possible=False)


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


"""
Wip; not using rn, might later
def ident_request(local_port, remote_port) -> str:
    with socket.create_connection(('localhost', 113), timeout=10) as sock:
        query = f"{local_port}, {remote_port}\r\n"
        sock.sendall(query.encode())

        response = sock.recv(1024).decode().strip()
        return response
"""


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


def get_services():
    """
    Get a list of systemd processes which the user has
    :return: A list of services
    """
    units = manager.ListUnits()

if __name__ == "__main__":
    print(generate_token())