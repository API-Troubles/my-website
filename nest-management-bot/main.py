import asyncio
import atexit
import math
from functools import partial
import logging
import os

from websockets.asyncio.server import serve

from slack_bolt.async_app import AsyncApp as App
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler

from dotenv import load_dotenv

import database
import views
import modals
import server_utils as utils
from server import ws_server


load_dotenv()
logging.basicConfig(level=logging.INFO)

# Initialize bot with token and signing secret
app = App(
    token=os.environ["NEST_MANAGEMENT_BOT_TOKEN"],
    signing_secret=os.environ["NEST_MANAGEMENT_SIGNING_SECRET"]
)

# Open database for account management
db = database.Database({
    "dbname": "felixgao_nest_management",
    "user": "felixgao",
    "password": os.environ['DB_PASSWORD'],
    "host": "hackclub.app",
    "port": "5432"
})

status_emojis = {
    "running": "🏃",
    "sleeping": "😴",
    "zombie": "🧟",
    "stopped": "⏹️",
    "disk-sleep": "💽"
}

me = os.environ['MY_SLACK_ID']
pagination_page_size: int = 15 # Arbitrary number set cause i needed one, pretty safe to change whenever :D


@app.event("app_home_opened")
async def update_home_tab(client, event, logger):
    user_id = event['user']
    logger.info(f"{user_id} opened the home tab")

    try: # todo: Catch any errors and display a error home tab
        user = db.get_user(slack_id=user_id)

        if user_id != me: # Testing check, blocks others from using D:
            await views.dashboard.generate_unauthorized(client, user_id)
            logger.warning(f"{user_id} is not authorized to use this bot")
            return

        if not user: # User not registered, signup!
            await views.dashboard.generate_setup_token(client, user_id)
            logger.info(f"{user_id} has started the setup process")
            return

        if not utils.clients.get(user[0]):
            await views.dashboard.generate_not_connected(client, user_id)
            return

        logger.info(f"{user_id} has opened the dashboard")
        await views.dashboard.generate_dashboard(client, user_id, utils.get_global_resources())

    except Exception as e:
        logger.error(f"Error updating home tab: {e}")
        return


@app.action("generate-dashboard")
async def handle_some_action(ack, body, client, logger):
    user_id = body['user']['id']
    await views.dashboard.generate_dashboard(client, user_id, utils.get_global_resources())

    await ack()


@app.action("setup-get-client-token")
async def setup_user(ack, body, client, logger):
    user_id = body['user']['id']
    logger.info(f"{user_id} opened the client-token modal")

    user = db.get_user(slack_id=user_id)
    if user:
        user_token = user[0]
        await client.views_open(trigger_id=body["trigger_id"], view=modals.manage_token_wizard_modal(user_token))
        logger.info(f"Obtained existing token for {user_id}")
    else:
        user_token = utils.generate_token()
        db.add_user(user_id, user_token)
        await views.dashboard.generate_dashboard(client, user_id, utils.get_global_resources()) # TODO: Replace with model for step 2
        await client.views_open(trigger_id=body["trigger_id"], view=modals.setup_token_wizard_modal(user_token))
        logger.info(f"Created token for {user_id}")

    await ack()


@app.action("setup-new-client-token")
async def setup_user(ack, body, client, logger):
    user_id = body['user']['id']
    logger.info(f"{user_id} has chosen to get a new token")

    if not db.get_user(slack_id=user_id):
        logger.warning(f"{user_id} doesn't exist and thus can't get a new token :skull:")
        return

    user_token = utils.generate_token()
    db.update_token(user_id, user_token)
    await client.views_update(view_id=body["view"]["id"], view=modals.setup_token_wizard_modal(user_token))
    # TODO: step 2 app home, websocket setup
    logger.info(f"Created new token for {user_id}")
    await ack()


async def send_paginated_result(client, user_id, user_token, page: int):
    result = await utils.send_command("obtain_all_process_info", user_token)

    page_contents = result["payload"][page*pagination_page_size:page*pagination_page_size+pagination_page_size]
    total_pages = math.ceil(len(result["payload"])/pagination_page_size)
    await views.processes_list_page(client, user_id, page_contents, page, total_pages)


@app.action("menu-process-usage")
async def menu_process_usage(ack, body, client, logger):
    user_id = body['user']['id']
    user_token = db.get_user(slack_id=user_id)[0]

    await send_paginated_result(client, user_id, user_token, page=0)
    await ack()


@app.action("processes-change-page-prev")
@app.action("processes-change-page-next")
async def processes_change_page(ack, body, client, logger):
    user_id = body['user']['id']
    page = int(body['actions'][0]['value'])

    user_token = db.get_user(slack_id=user_id)[0]

    await send_paginated_result(client, user_id, user_token, page)
    await ack()


@app.action("menu-systemd-services")
async def menu_systemd_services(ack, body, logger):
    user_id = body['user']['id']
    logger.info(body)

    await ack()


@app.action("manage-process")
async def menu_manage_process(ack, body, logger):
    user_id = body['user']['id']
    pid = body['actions'][0]['value']
    logger.info(body)

    user_token = db.get_user(slack_id=user_id)[0]
    await utils.send_command("obtain_process_info", user_token, payload={"pid": int(pid)})

    await ack()


ws_handler = partial(ws_server, db=db)
async def ws_main():
    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #ssl_context.load_cert_chain("cert.pem", "private_key.pem")

    async with serve(ws_handler, "localhost", 8989):#, ssl=ssl_context):
        print("server running...")
        await asyncio.get_running_loop().create_future()  # run forever


async def slack_bot_main():
    slack_bot = AsyncSocketModeHandler(app, os.environ["NEST_MANAGEMENT_APP_TOKEN"])
    await slack_bot.start_async()


async def real_main():
    await asyncio.gather(slack_bot_main(), ws_main())

# Close the database on code end
atexit.register(lambda: db.close())


if __name__ == "__main__":
    asyncio.run(real_main())