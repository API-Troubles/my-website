def get_port_modal(port: str):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Port Yoinker",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Thx for the port",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "What do you need a port for from a bot? Oh well here you go :yay:",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{port}```"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "Stolen 100% from `nest get_port`",
                    "emoji": True
                }
            }
        ]
    }