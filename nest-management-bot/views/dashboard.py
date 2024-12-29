async def generate_dashboard(client, user_id, data: dict):
    """
    Generates the default dashboard
    :param client:
    :param user_id:
    :param data: The data to display on the dashboard
    :return:
    """
    await client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Welcome Back!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "View your Nest stats quickly below!\nDEVELOPMENT - attempting real data :pf:"
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
                        "text": f"*CPU:* {data["cpu"]}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*MEM:* {data["mem"]}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Storage:* {data["storage"]}"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "My Usage Menu",
                                "emoji": True
                            },
                            "action_id": "menu-user-usages"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Processes Menu",
                                "emoji": True
                            },
                            "action_id": "menu-process-usage"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Systemd Services Menu",
                                "emoji": True
                            },
                            "action_id": "menu-systemd-services"
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


async def generate_unauthorized(client, user_id):
    """
    Woah there! You're not allowed here :/ Generates unauthorized view
    :param client:
    :param user_id:
    :return:
    """
    await client.views_publish(
        user_id=user_id,
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


async def generate_setup_token(client, user_id):
    """
    (setup) Generate step 1; the token setup step
    :param client:
    :param user_id:
    :return:
    """
    await client.views_publish(
        user_id=user_id,
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


async def generate_setup_websocket(client, user_id):
    """
    (setup) Generate step 2; the websocket setup step
    :param client:
    :param user_id:
    :return:
    """
    await client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Awesome! On to step 2 :D",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "This bot relies on a websocket, a standard used for communication. In this case, a websocket is run from your Nest user to a server I (@Felix Gao) run. This allows the bot to send and receive messages from your Nest user. There is an element of trust here, I promise to not touch your Nest stuff (too lazy anyways :p).",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "With that out of the way, let's get setup! To start, run this command. It simply adds a bash script. That bash script handles the setup for the websocket and runs it. You can find it at the repo below, 100% open source :D! This prompt will remain open until you run the command, so come back if you need it again :).",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "```command_here --felix_pls_fix```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_Make with 100% open-source love, find the repo here: https://github.com/felixgao-0/my-website _"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Forgot to yoink that token? I got you :D =>"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Get Token",
                            "emoji": True
                        },
                        "action_id": "setup-get-client-token"
                    }
                }
            ]
        }
    )


async def generate_not_connected(client, user_id):
    """
    Generate an error page when the websocket isn't connected :(
    :param client:
    :param user_id:
    :return:
    """
    await client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":warn: Your websocket is not connected :roo-oh-no: ",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*What went wrong?*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "This bot relies on the websocket to function. Check that the websocket script is running (`systemctl --user status nest-msg-bot.service`). Try starting it with `systemctl --user start nest-msg-bot.service`. For support, ask in #nest-management-bot."
                    }
                }
            ]
        }
    )