def processes_list_modal(processes):
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
    for item in processes:
        process_item = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{item['name']} - PID: {item['pid']}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Manage Process",
                    "emoji": True
                },
                "value": f"{item['pid']}",
                "action_id": "manage-process"
            }
        }
        base["blocks"].insert(-2, process_item)
    return base