def setup_token_wizard_modal(user_token):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Setup Wizard",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Ok tysm!",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"This is your client token:\n`{user_token}`"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"To add the client key to your Nest user, run the following in Nest:\n```echo CLIENT_TOKEN={user_token} >> ~/.env.nest-management-bot```"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":siren-real::warning: *Do not share your token pwease* :thumbsup-dino:"
                }
            }
        ]
    }

def manage_token_wizard_modal(user_token):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "My App",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Ok tysm!",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"This is your client token:\n`{user_token}`"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"To add the client key to your Nest user, run the following in Nest:\n```echo CLIENT_TOKEN={user_token} ~/.env.nest-management-bot```"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Reset your token",
                            "emoji": True
                        },
                        "action_id": "setup-new-client-token"
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
                    "text": ":siren-real::warning: *Do not share your token pwease* :thumbsup-dino:"
                }
            }
        ]
    }