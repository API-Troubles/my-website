import asyncio
import atexit
import math
from functools import partial
import logging
import os

from websockets.asyncio.server import serve

from slack_bolt import App
from slack_bolt.async_app import AsyncApp
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
app = AsyncApp(
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

        if db.get_setting(user_id, "tutorial")[2] == "stage_2":
            await views.dashboard.generate_setup_websocket(client, user_id)
            logger.info(f"{user_id} is back for the websocket setup process")
            return

        if not utils.clients.get(user[0]):
            await views.dashboard.generate_not_connected(client, user_id)
            logger.info(f"{user_id} is not connected to the websocket")
            return

        logger.info(f"{user_id} has opened the dashboard")

        all_info = utils.get_global_resources()

        unit = db.get_setting(user_id, "storage_unit_of_measurement")[2]
        mem_info = f"{utils.unit_converter(all_info['mem']['used'], unit, include_unit=False)}{utils.unit_converter(all_info['mem']['total'], unit)}"
        storage_info = f"{utils.unit_converter(all_info['storage']['used'], unit, include_unit=False)}{utils.unit_converter(all_info['storage']['total'], unit)}"
        await views.dashboard.generate_dashboard(client, user_id, all_info, mem_info, storage_info)

    except Exception as e:
        logger.error(f"Error updating home tab: {e}")
        return


@app.action("generate-dashboard")
async def generate_dashboard(ack, body, client, logger):
    user_id = body['user']['id']

    all_info = utils.get_global_resources()

    unit = db.get_setting(user_id, "storage_unit_of_measurement")[2]
    mem_info = f"{utils.unit_converter(all_info['mem']['used'], unit, include_unit=False)}{utils.unit_converter(all_info['mem']['total'], unit)}"
    storage_info = f"{utils.unit_converter(all_info['storage']['used'], unit, include_unit=False)}{utils.unit_converter(all_info['storage']['total'], unit)}"
    await views.dashboard.generate_dashboard(client, user_id, all_info, mem_info, storage_info)
    await ack()


@app.action("generate-settings")
async def generate_settings(ack, body, client, logger): # unused for now, gotta work out db stuff
    settings = db.get_setting(body['user']['id'])

    settings_dict = {}
    for setting in settings:
        settings_dict[setting[1]] = setting[2]

    await client.views_open(trigger_id=body["trigger_id"], view=modals.settings_modal(settings_dict))
    await ack()


@app.action("menu-user-usages")
async def menu_user_usages(ack, body, client, logger):
    user_id = body['user']['id']
    user_token = db.get_user(slack_id=user_id)[0]

    result = await utils.send_command("obtain_user_usages", user_token)
    await views.user_usages_page(client, user_id, result['payload'])

    await ack()


@app.action("setup-get-client-token")
async def setup_user(ack, body, client, logger):
    user_id = body['user']['id']
    logger.info(f"{user_id} opened the client-token modal")

    user = db.get_user(slack_id=user_id)
    if user:
        user_token = user[0]
        logger.info(f"Obtained existing token for {user_id}")
    else:
        user_token = utils.generate_token()
        db.add_user(user_id, user_token)
        db.add_setting(user_id, "tutorial", "stage_2")
        db.add_setting(user_id, "mem_vs_ram", "mem")
        db.add_setting(user_id, "storage_unit_of_measurement", "gb")
        await views.dashboard.generate_setup_websocket(client, user_id)
        logger.info(f"Created token for {user_id}, moving on to websocket setup")

    await client.views_open(trigger_id=body["trigger_id"], view=modals.setup_token_wizard_modal(user_token))
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
    logger.info(f"Created new token for {user_id}")
    await ack()


async def send_paginated_result_process(client, user_id, user_token, page: int):
    result = await utils.send_command("obtain_all_process_info", user_token)

    page_contents = result["payload"][page*pagination_page_size:page*pagination_page_size+pagination_page_size]
    total_pages = math.ceil(len(result["payload"])/pagination_page_size)
    await views.processes_list_page(client, user_id, page_contents, page, total_pages)


@app.action("menu-process-usage")
async def menu_process_usage(ack, body, client, logger):
    user_id = body['user']['id']
    user_token = db.get_user(slack_id=user_id)[0]

    await send_paginated_result_process(client, user_id, user_token, page=0)
    await ack()


@app.action("processes-change-page-prev")
@app.action("processes-change-page-next")
async def processes_change_page(ack, body, client, logger):
    user_id = body['user']['id']
    page = int(body['actions'][0]['value'])

    user_token = db.get_user(slack_id=user_id)[0]

    await send_paginated_result_process(client, user_id, user_token, page)
    await ack()


@app.action("manage-process")
async def menu_manage_process(ack, body, client, logger):
    user_id = body['user']['id']
    pid = body['actions'][0]['value'].split("-")

    user_token = db.get_user(slack_id=user_id)[0]
    result = await utils.send_command("obtain_process_info", user_token, payload={"pid": int(pid[0])})
    process_info = result['payload']

    mem_or_ram = db.get_setting(user_id, "mem_vs_ram")[2]
    mem_info = utils.unit_converter(process_info['memory']['rss'], db.get_setting(user_id, "storage_unit_of_measurement")[2])

    if pid[1] == "update":
        await client.views_update(view_id=body["view"]["id"], view=modals.process_info_modal(process_info, mem_or_ram, mem_info))
    else:
        await client.views_open(trigger_id=body["trigger_id"], view=modals.process_info_modal(process_info, mem_or_ram, mem_info))

    await ack()


@app.action("kill-process-1")
@app.action("kill-process-2") # Slack requires unique names, I have 2 buttons. They do the same thing so uhh lol
async def process_kill(ack, body, client, logger):
    user_id = body['user']['id']
    pid = body['actions'][0]['value'].split("-")
    logger.info(body)

    user_token = db.get_user(slack_id=user_id)[0]
    result = await utils.send_command("kill_process", user_token, payload={"pid": int(pid[0]), "method": pid[3]})

    if result['status'] == 'command_response_error':
        await client.views_update(
            view_id=body["view"]["id"],
            view=modals.error_modal(result['payload']['error'])
        )
    else:
        await client.views_update(
            view_id=body["view"]["id"],
            view=modals.process_kill_success_modal(pid)
        )
    await ack()


@app.action("pause-process")
async def process_pause(ack, body, client, logger):
    user_id = body['user']['id']
    pid = body['actions'][0]['value']

    user_token = db.get_user(slack_id=user_id)[0]
    result = await utils.send_command("pause_process", user_token, payload={"pid": int(pid)})

    if result['status'] == 'command_response_error':
        await client.views_update(
            view_id=body["view"]["id"],
            view=modals.error_modal(result['payload']['error'])
        )
    else:
        await client.views_update(
            view_id=body["view"]["id"],
            view=modals.process_action_success_modal("paus", pid)
        )
    await ack()


@app.action("resume-process")
async def process_resume(ack, body, client, logger):
    user_id = body['user']['id']
    pid = body['actions'][0]['value']

    user_token = db.get_user(slack_id=user_id)[0]
    result = await utils.send_command("resume_process", user_token, payload={"pid": int(pid)})

    if result['status'] == 'command_response_error':
        await client.views_update(
            view_id=body["view"]["id"],
            view=modals.error_modal(result['payload']['error'])
        )
    else:
        await client.views_update(
            view_id=body["view"]["id"],
            view=modals.process_action_success_modal("resum", pid)
        )
    await ack()


async def send_paginated_result_systemd(client, user_id, user_token, page: int):
    result = await utils.send_command("list_services", user_token)

    page_contents = result["payload"][page*pagination_page_size:page*pagination_page_size+pagination_page_size]
    total_pages = math.ceil(len(result["payload"])/pagination_page_size)
    await views.systemd_services_list_page(client, user_id, page_contents, page, total_pages)


@app.action("menu-systemd-services")
async def menu_systemd_services(ack, body, client, logger):
    user_id = body['user']['id']
    user_token = db.get_user(slack_id=user_id)[0]
    logger.info(body)

    await send_paginated_result_systemd(client, user_id, user_token, page=0)
    await ack()


@app.action("services-change-page-prev")
@app.action("services-change-page-next")
async def services_change_page(ack, body, client, logger):
    user_id = body['user']['id']
    page = int(body['actions'][0]['value'])

    user_token = db.get_user(slack_id=user_id)[0]

    await send_paginated_result_systemd(client, user_id, user_token, page)
    await ack()


@app.action("manage-service")
async def menu_manage_service(ack, body, client, logger):
    user_id = body['user']['id']
    service_name = body['actions'][0]['value'].split("-")

    user_token = db.get_user(slack_id=user_id)[0]
    result = await utils.send_command("obtain_service_info", user_token, payload={"service_name": service_name[0]})
    service_info = result['payload']

    if service_name[1] == "update":
        await client.views_update(view_id=body["view"]["id"], view=modals.service_info_modal(service_info))
    else:
        await client.views_open(trigger_id=body["trigger_id"], view=modals.service_info_modal(service_info))

    await ack()


@app.action("manage-service-action-1")
@app.action("manage-service-action-2")
@app.action("manage-service-action-3") # WHY SLACK DO THEY MUST BE UNIQUE? I just want my code to be readable is that too much to ask this Christmas?
async def service_action(ack, body, client, logger):
    user_id = body['user']['id']
    service_info = body['actions'][0]['value'].split("-")

    user_token = db.get_user(slack_id=user_id)[0]
    result = await utils.send_command(f"{service_info[1]}_service", user_token, payload={"service_name": service_info[0]})

    if result['status'] == 'command_response_error':
        await client.views_update(view_id=body["view"]["id"], view=modals.error_modal(result['payload']['error']))
    else:
        await client.views_update(view_id=body["view"]["id"], view=modals.service_action_modal(service_info[0], service_info[1]))

    await ack()


@app.action("menu-get-port")
async def menu_get_port(ack, body, client, logger):
    user_id = body['user']['id']
    user_token = db.get_user(slack_id=user_id)[0]

    result = await utils.send_command("get_port", user_token)
    modals.get_port_modal(result["payload"])

    await ack()


@app.action("settings-unit-data")
async def settings_unit_data(ack, body, logger):
    selection = body['actions'][0]['selected_option']['value']
    user_id = body['user']['id']

    db.edit_setting(user_id, "storage_unit_of_measurement", selection)

    await ack()


@app.action("settings-mem-vs-ram")
async def settings_mem_is_better(ack, body, client, logger):
    selection = body['actions'][0]['selected_option']['value']
    user_id = body['user']['id']

    db.edit_setting(user_id, "mem_vs_ram", selection)

    await ack()


async def ws_main(client):
    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #ssl_context.load_cert_chain("cert.pem", "private_key.pem")

    ws_handler = partial(ws_server, db=db, client=client)
    async with serve(ws_handler, "localhost", 8989):#, ssl=ssl_context):
        print("server running...")
        await asyncio.get_running_loop().create_future()  # run forever


async def real_main():
    slack_bot = AsyncSocketModeHandler(app, os.environ["NEST_MANAGEMENT_APP_TOKEN"])

    await asyncio.gather(slack_bot.start_async(), ws_main(slack_bot.client))

# Close the database on code end
atexit.register(lambda: db.close())


if __name__ == "__main__":
    asyncio.run(real_main())