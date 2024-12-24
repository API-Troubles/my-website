def confirm_prompt(action: str, consequence: str):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Are you sure?",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Yup!",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Nuh uh Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Are you sure to want to `{action}`?"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_Reminder: {consequence if consequence else "Be careful with what you do :pf:"}_"
                }
            }
        ]
    }