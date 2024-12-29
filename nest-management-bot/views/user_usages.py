async def user_usages_page(client, user_id, usage):
    await client.views_publish(
        user_id=user_id,
        view={
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Your Usages",
                    "emoji": True
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Memory & Total Storage Usage:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Might have been borrowed from `nest resources` :pf:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{usage['resources']}```"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Storage by Folder:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "\n".join([f"`{item[1]}`: {round(int(item[0]) / 10**9, 4)} GB" for item in usage['storage']])
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
                            "text": ":hq: Home",
                            "emoji": True
                        },
                        "action_id": "generate-dashboard"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":arrows_clockwise: Reload",
                            "emoji": True
                        },
                        "action_id": "menu-user-usages"
                    }
                ]
            }
        ]
    })