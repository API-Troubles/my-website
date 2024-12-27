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
                    "text": "Might have been borrowed from `nest resources` :pf:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"```{usage}```"
                }
            },
            {
                "type": "divider"
            }
        ]
    })