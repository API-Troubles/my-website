import asyncio
import json
import ssl


from websockets.asyncio.server import serve
import websockets

import server_utils as utils
from server_utils import clients


async def server(websocket):
    try:
        # Client info validation
        try:
            first_message_json = await asyncio.wait_for(websocket.recv(), timeout=60)
        except asyncio.TimeoutError:
            await websocket.send(json.dumps({
                'message': 'The client did not send a response to the server.',
                'status': 'error'
            }))
            return

        try:
            first_message = json.loads(first_message_json)
        except json.decoder.JSONDecodeError:
            await websocket.send(json.dumps({
                'message': 'The client sent malformed data which isn\'t JSON.',
                'status': 'error'
            }))
            return

        # not ideal location but for some reason intellij ONLY WANTS IT *HERE*
        db_client_tokens = ["trust_me_bro", "hello_world"] # TODO ASAP: get db connected to validate this
        if first_message.get('status') != "let_me_in_pls":
            await websocket.send(json.dumps({
                'message': 'The client sent malformed data with the incorrect type.',
                'status': 'error'
            }))
            return

        elif first_message.get('payload').get('client_token') not in db_client_tokens:
            await websocket.send(json.dumps({
                'message': 'Invalid client token or the client sent malformed data.',
                'status': 'error'
            }))
            return

        elif first_message.get('payload').get('version') != "0.1.0a":
            await websocket.send(json.dumps({
                'message': 'Your version is out of date or the client sent malformed data.',
                'status': 'error'
            }))
            return

        # User authenticated yay
        await websocket.send(json.dumps({'status': 'info', 'message': 'Authenticated :D'}))

        # Add client to list to use for sending messages later
        clients[f'{websocket.id}']: websocket = websocket
        print("ACTIVE CLIENTS:", clients.keys())


        async for message in websocket:
            print(f"RANDOM MESSAGE: {message}")
            if message == "close":
                await websocket.close()
                return

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    finally:
        if clients.get(websocket.id):
            clients.pop(f'{websocket.id}')
        print("ACTIVE CLIENTS:", clients.keys())


async def main():
    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #ssl_context.load_cert_chain("cert.pem", "private_key.pem")

    async with serve(server, "localhost", 8989):#, ssl=ssl_context):
        print("server running...")
        await asyncio.get_running_loop().create_future()  # run forever


"""
try:
    cmd_response = await asyncio.wait_for(
        utils.send_command('download raid shadow legends!', f'{websocket.id}'),
        5
    )
except asyncio.TimeoutError:
    await utils.send_error(websocket, 'Did not receive a response in time', possible=False)
    return

print(f"RESPONSE: {cmd_response}")
"""

if __name__ == "__main__":
    asyncio.run(main())