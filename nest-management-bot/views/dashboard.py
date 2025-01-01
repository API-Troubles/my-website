async def generate_dashboard(client, user_id, data: dict, mem_info: str, storage_info: str):
    """
    Generates the default dashboard
    :param client:
    :param user_id:
    :param data: The data to display on the dashboard
    :param mem_info: The memory info to display
    :param storage_info: The storage info to display
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
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": ":gear: Settings",
                                "emoji": True
                            },
                            "action_id": "generate-settings"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": ":arrows_clockwise: Reload",
                                "emoji": True
                            },
                            "action_id": "generate-dashboard"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "View your Nest stats quickly below!\nPUBLIC BETA: Real Data, report problems to #nest-management-bot"
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
                        "text": f"*CPU:* {data['cpu']['percent']}%"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*MEM:* {mem_info}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Storage:* {storage_info}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Nest has been up since `{data['uptime']}`! :yay:"
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
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Get a Port",
                                "emoji": True
                            },
                            "action_id": "menu-get-port"
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
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "Feature suggestions? Ping me in #nest-management-bot :D. Contributions? Make a PR to the nest-management-bot folder at https://github.com/felixgao-0/my-website."
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
                        "text": "I guess you've been banned? What on earth did you do lol"
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
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_Protip: Make sure you set a gitignore for `.env.*` which includes the token's env file._"
                    }
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
                        "text": "With that out of the way, let's get setup! Read the canvas link below:",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "https://hackclub.slack.com/docs/T0266FRGM/F07UDKPC3RV"
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
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_P.S. This bot has settings! Check it out here >_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":gear: Settings",
                            "emoji": True
                        },
                        "action_id": "generate-settings"
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