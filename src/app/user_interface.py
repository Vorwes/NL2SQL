import os

import chainlit as cl
import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")


@cl.on_chat_start
async def start():
    settings = cl.ChatSettings(
        [
            cl.input_widget.TextInput(
                id="db_uri",
                label="PostgreSQL URI",
                initial="",
                placeholder="postgresql://user:password@localhost:5432/db_name",
            )
        ]
    )
    await settings.send()

    await cl.Message(
        content="Welcome to the **NL2SQL Interface**. \n\nPlease open the **Settings** panel on the left to connect your database before querying."
    ).send()


@cl.on_settings_update
async def setup_agent(settings):
    db_uri = settings["db_uri"]

    if not db_uri:
        await cl.Message(content="⚠️ Please provide a valid Database URI.").send()
        return

    msg = cl.Message(content="⏳ Connecting to database and building vector schema...")
    await msg.send()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/connect",
                json={"db_uri": db_uri, "db_name": "dynamic_db"},
                timeout=300.0,
            )
            response.raise_for_status()

            msg.content = "✅ **Successfully connected!** \nThe system is now ready for your queries."
            await msg.update()

            cl.user_session.set("connected", True)

        except Exception as e:
            msg.content = f"❌ **Failed to connect:** {str(e)}"
            await msg.update()


@cl.on_message
async def main(message: cl.Message):
    if not cl.user_session.get("connected"):
        await cl.Message(
            content="⚠️ Please configure your database connection in the Settings panel first."
        ).send()
        return

    msg = cl.Message(content="")

    async with cl.Step(name="Generate SQL", type="run") as step:
        step.content = "Retrieving schema tables and processing..."

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{API_URL}/generate_sql",
                    json={"query": message.content},
                    timeout=120.0,
                ) as response:
                    response.raise_for_status()

                    step.content = "Streaming response..."

                    async for chunk in response.aiter_text():
                        await msg.stream_token(chunk)

            except Exception as e:
                await msg.stream_token(f"\n❌ **Error during generation:** {str(e)}")
                step.status = "error"
                return

        step.status = "success"

    await msg.update()
