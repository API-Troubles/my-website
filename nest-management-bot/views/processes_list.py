async def processes_list_page(client, user_id, processes, page, total_pages):
    base = {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Processes (Page {page+1}/{total_pages})", # +1 to account for zero-indexing
                    "emoji": True
                }
            },
            {
                "type": "divider"
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
                            "text": ":hq: Home",
                            "emoji": True
                        },
                        "action_id": "generate-dashboard"
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
                "text": f"`{item['name']}` - PID: {item['pid']}"
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

    if page > 0:
        base["blocks"][-1]["elements"].insert(0, {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": ":arrow_backward: Previous",
                "emoji": True
            },
            "value": f"{page-1}",
            "action_id": "processes-change-page-prev"
        })
    if page+1 != total_pages:
        base["blocks"][-1]["elements"].append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Next :arrow_forward:",
                "emoji": True
            },
            "value": f"{page+1}",
            "action_id": "processes-change-page-next"
        })

    await client.views_publish(
        user_id=user_id,
        view=base
    )