import asyncio
import json
import ssl


from websockets.asyncio.server import serve
import websockets

import server_utils as utils
from server_utils import clients


async def ws_server(websocket, ws_clients, db):
    if not db:
        raise ValueError('Database not initialized/provided')
    try:
        # Client info validation
        try:
            first_message_json = await asyncio.wait_for(websocket.recv(), timeout=60)
        except asyncio.TimeoutError:
            await websocket.send(json.dumps({
                'message': 'The client did not send a response to the server.',
                'status': 'error'
            }))
            await websocket.close()
            return

        try:
            first_message = json.loads(first_message_json)
        except json.decoder.JSONDecodeError:
            await websocket.send(json.dumps({
                'message': 'The client sent malformed data which isn\'t JSON.',
                'status': 'error'
            }))
            await websocket.close()
            return

        # not ideal location but for some reason intellij ONLY WANTS IT *HERE*
        client_token_provided = first_message.get('payload', {}).get('client_token')
        if first_message.get('status') != "let_me_in_pls":
            await websocket.send(json.dumps({
                'message': 'The client sent malformed data of incorrect type. This shouldn\'t happen, ask in #nest-management-bot.',
                'status': 'error'
            }))
            await websocket.close()
            return

        elif not db.get_user(token=client_token_provided):
            await websocket.send(json.dumps({
                'message': f'Invalid client token "{client_token_provided}" or the client sent malformed data.',
                'status': 'error'
            }))
            print(first_message_json)
            await websocket.close()
            return

        elif client_token_provided in clients.keys():
            await websocket.send(json.dumps({
                'message': 'Already connected, if this is incorrect regenerate your token NOW.',
                'status': 'error'
            }))
            await websocket.close()
            return

        elif first_message.get('payload', {}).get('version') != "0.1.0a":
            await websocket.send(json.dumps({
                'message': 'Your version is out of date or the client sent malformed data.',
                'status': 'error'
            }))
            await websocket.close()
            return

        # User authenticated yay
        await websocket.send(json.dumps({'status': 'info', 'message': 'Authenticated :D'}))

        # Add client to list to use for sending messages later
        clients[client_token_provided]: websocket = websocket
        ws_clients[websocket.id]: str = client_token_provided
        print("ACTIVE CLIENTS:", clients.keys())

        # Update any existing home tabs :yay:
        #user_id = db.get_user(token=client_token_provided)[0] # 0 is the user_id col
        # TODO finish


        async for message in websocket:
            print(f"RANDOM MESSAGE: {message}")
            if message == "close":
                await websocket.close()
                return

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection suddenly closed: {e}")
    except asyncio.TimeoutError:
        print("Client disappeared, closing connection")
        await websocket.close()
    finally:
        client_id = ws_clients.get(websocket.id)
        if clients.get(client_id):
            clients.pop(client_id)
        print("ACTIVE CLIENTS:", clients.keys())