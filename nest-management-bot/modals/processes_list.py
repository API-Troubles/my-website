def processes_list_modal():
    base = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "Process Management",
            "emoji": True
        },
        "close": {
            "type": "plain_text",
            "text": "Bye Bye!",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*View your Processes:*"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "plain_text",
                        "text": "Made by Felix with open-source :sparkling_heart:",
                        "emoji": True
                    }
                ]
            }
        ]
    }
    # TODO: Replace with actual processes
    processes = []
    for item in processes:
        # TODO: Replace names with values below
        process_item = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "[NAME]"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Manage Process",
                    "emoji": True
                },
                "value": "[PID/ANY ID]",
                "action_id": "manage-process"
            }
        }
        base['blocks'].insert(-3, process_item)