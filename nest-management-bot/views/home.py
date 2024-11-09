def generate_dashboard(client, user_id):
    """
    Generates the default dashboard
    :param client:
    :param user_id:
    :return:
    """
    client.views_publish(
        # the user that opened your app's app home
        user_id=user_id,
        # the view object that appears in the app home
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Heya!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "View your Nest stats quickly below!\nDEVELOPMENT - NOT REAL DATA YET"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Global Usages:*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*CPU:* 23%"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*MEM:* 0.53/2.00 GB"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Storage:* 2.34/10.00 GB"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Process Usage:*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Open Menu",
                                "emoji": True
                            },
                            "value": "open-process-usage",
                            "action_id": "open-process-usage"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Need to get/reset your token again? Click here =>"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Manage Token",
                            "emoji": True
                        },
                        "action_id": "setup-get-client-token"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "I am not liable for any misuse of this bot. I do not warranty this bot at all. use at your own risk. Please report any security vulns by pinging me a million times in DMs (@Felix Gao) /srs."
                        }
                    ]
                }
            ]
        }
    )

def generate_unauthorized(client, user_id):
    """
    Woah there! You're not allowed here :/ Generates unauthorized view
    :param client:
    :param user_id:
    :return:
    """
    client.views_publish(
        # the user that opened your app's app home
        user_id=user_id,
        # the view object that appears in the app home
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":siren-real: *You are not allowed to use this bot.*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Check back in soon! Bot is in active development"
                    }
                }
            ]
        }
    )

def generate_setup_token(client, user_id):
    """
    (setup) Generate step 1;the token setup step
    :param client:
    :param user_id:
    :return:
    """
    client.views_publish(
        # the user that opened your app's app home
        user_id=user_id,
        # the view object that appears in the app home
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome! :wave:",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "To get setup with this bot, read the setup guide <https://hackclub.slack.com/docs/T0266FRGM/F07UDKPC3RV|here>."
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This bot is provided without any guarantee of warranty. I am not responsible for misuse of this bot. Don't kill processes you don't understand. :)"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": ":point_down: Get your client token here"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Get Token",
                                "emoji": True
                            },
                            "action_id": "setup-get-client-token"
                        }
                    ]
                }
            ]
        }
    )


def generate_setup_websocket(client, user_id):
    """
    (setup) Generate step 2;the websocket setup step
    :param client:
    :param user_id:
    :return:
    """
    client.views_publish(
        # the user that opened your app's app home
        user_id=user_id,
        # the view object that appears in the app home
        view={}
    )