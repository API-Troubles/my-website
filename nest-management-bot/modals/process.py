def process_list_modal(processes):
    return {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Running Processes",
            "emoji": True
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{processes}"
                }
            }
        ]
    }