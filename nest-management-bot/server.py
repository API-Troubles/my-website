import asyncio
import json
import websockets

import server_utils as utils
from server_utils import clients
from views.dashboard import generate_not_connected, generate_dashboard

ws_clients = {} # Internal list used to manage connection states

async def ws_server(websocket, db, client, logger):
    if not db:
        raise ValueError('Database not initialized/provided')
    try:
        # Client info validation
        try:
            async with asyncio.timeout(1):
                first_message_json = await websocket.recv()
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

        elif not utils.verify_token_checksum(client_token_provided):
            await websocket.send(json.dumps({
                'message': f'"{client_token_provided}" is of incorrect format or the client sent malformed data.',
                'status': 'error'
            }))
            await websocket.close()
            return

        elif not db.get_user(token=client_token_provided):
            await websocket.send(json.dumps({
                'message': f'Invalid client token "{client_token_provided}" or the client sent malformed data.',
                'status': 'error'
            }))
            await websocket.close()
            return

        elif client_token_provided in clients.keys():
            await websocket.send(json.dumps({
                'message': 'Already connected, if this is incorrect regenerate your token :heavysob:.',
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

        user = db.get_user(token=client_token_provided)

        all_info = utils.get_global_resources()
        unit = db.get_setting(user[1], "storage_unit_of_measurement")[2]
        mem_info = f"{utils.unit_converter(all_info['mem']['used'], unit, include_unit=False)}/{utils.unit_converter(all_info['mem']['total'], unit)}"
        storage_info = f"{utils.unit_converter(all_info['storage']['used'], unit, include_unit=False)}/{utils.unit_converter(all_info['storage']['total'], unit)}"
        await generate_dashboard(client.web_client, user[1], all_info, mem_info, storage_info)

        if db.get_setting(user[1], 'tutorial')[2] == "stage_2": # stage 2 means the user has just connected :D
            db.edit_setting(user[1], 'tutorial', 'stage_3') # promote to stage 3, finished :D

        # Add client to list to use for sending messages later
        clients[client_token_provided]: websocket = websocket
        ws_clients[f"{websocket.id}"]: str = client_token_provided
        logger.info(f"Client connected: user_id = {user[1]}")
        #print("ACTIVE CLIENTS:", clients.keys())

        await websocket.wait_closed() # Hold the connection open until websocket disconnects, muhahaha

    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"Connection suddenly closed: {e}")
    except asyncio.TimeoutError:
        logger.error("Client disappeared, closing connection")
        await websocket.close()
    finally:
        client_id = ws_clients.get(f"{websocket.id}")

        if not client_id:
            logger.warning("client_id not found in ws_clients list")

        if clients.get(client_id):
            clients.pop(client_id)
        else:
            logger.warning("Client not be found in clients list")

        try:
            user = db.get_user(token=client_id)
            await generate_not_connected(client.web_client, user[1])
        except ValueError:
            logger.error("User not found in database, cannot generate not connected message")

        #print("CHANGE TO ACTIVE CLIENTS:", clients.keys())