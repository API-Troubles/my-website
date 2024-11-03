import atexit
import os
import logging
import requests
import json

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler # Socket mode lol

from dotenv import load_dotenv

# Local environment BUGFIX: I can't figure out why but ig im missing some cert files lol
# might be unneeded for others
# TODO: REMOVE IN PROD, prob
import certifi

import database
import views.home as home
import modals

import server_utils as utils

os.environ['SSL_CERT_FILE'] = certifi.where()

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

me = os.environ['MY_SLACK_ID']

class LogWebhookHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record):
        log_entry = self.format(record)
        payload = {"text": f"[{record.levelname}] - {log_entry}"}

        response = requests.post(
            self.webhook_url, data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )

        print("Error emitted to slack channel")


# Create and add the Slack log handler
slack_handler = LogWebhookHandler(os.environ['NEST_MANAGEMENT_LOG_WEBHOOK'])
#logging.addHandler(slack_handler)


@app.event("app_home_opened")
def update_home_tab(client, event, logger):
    user_id = event['user']
    logger.info(f"{user_id} opened the home tab")

    if user_id != me: 
        # Testing check, blocks others from using D:
        home.generate_unauthorized(client, user_id)
        logger.warning(f"{user_id} is not authorized to use this bot")
        return

    if not db.get_user(slack_id=user_id):
        #User not registered, signup!
        home.generate_setup(client, user_id)
        logger.info(f"{user_id} has started the setup process")
        return

    logger.info(f"{user_id} has opened the dashboard")
    home.generate_dashboard(client, user_id)


@app.action("setup-get-client-token")
def setup_user(ack, body, client, logger):
    user_id = body['user']['id']
    logger.info(f"{user_id} opened the client-token modal")

    user = db.get_user(slack_id=user_id)

    if user:
        user_token = user[0]
        client.views_open(trigger_id=body["trigger_id"], view=modals.manage_token_wizard_modal(user_token))
        logger.info(f"Obtained existing token for {user_id}")
    else:
        user_token = utils.generate_token()
        db.add_user(user_id, user_token)
        home.generate_dashboard(client, user_id) # TODO: Replace with model for step 2
        client.views_open(trigger_id=body["trigger_id"], view=modals.setup_token_wizard_modal(user_token))
        logger.info(f"Created token for {user_id}")

    ack()


@app.action("setup-new-client-token")
def setup_user(ack, body, client, logger):
    user_id = body['user']['id']
    logger.info(f"{user_id} has chosen to get a new token")

    if not db.get_user(slack_id=user_id):
        logger.warning(f"{user_id} doesn't exist and thus can't get a new token :skull:")
        return

    user_token = utils.generate_token()
    db.update_token(user_id, user_token)
    client.view_update(trigger_id=body["trigger_id"], view=modals.setup_token_wizard_modal(user_token))
    # TODO: step 2 app home + new client modal and kick out websocket if connected
    logger.info(f"Created new token for {user_id}")

    ack()


@app.action("open-process-usage")
def handle_some_action(ack, body, logger):
    ack()
    logger.info(body)


# Close the database on code end
atexit.register(lambda: db.close())

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["NEST_MANAGEMENT_APP_TOKEN"]).start()
