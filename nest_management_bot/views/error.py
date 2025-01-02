async def generate_error(client, user_id, error: str):
    await client.views_publish(
        user_id=user_id,
        view={
            "type": "home",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "Mission control to blahaj, we have an error!",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "We have experienced an error and cannot continue (my code tried its best ok) :im-sobbing:",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{error}```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_Usually these don't mean much (I likely was too lazy to code a proper menu for error handling). If the error does not contain troubleshooting steps and the error sounds scary, take a screenshot of this error and send it in #nest-management-bot :heavysob: I'm sorry (Canadian Edition apology)_"
                    }
                },
                {
                    "type": "image",
                    "image_url": "https://media1.tenor.com/m/1BWouEztZM4AAAAd/troubleshooting-it.gif",
                    "alt_text": "GIF of a loading bar reaching 99% then showing an error prompt. A cat then throws a keyboard at the monitor. Text displays at the bottom 'if all else fails try percussive engineering!'"
                }
            ]
        }
    )