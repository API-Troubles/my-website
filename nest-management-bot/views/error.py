async def generate_error(client, user_id, error: str):
    await client.views_publish(
        user_id=user_id,
        view={}
    )