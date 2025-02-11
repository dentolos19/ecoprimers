import os

from flask import Flask
from google import genai

initialized: bool = False
agent: genai.Client = None


def init(app: Flask):
    global initialized
    global agent

    # Skip if AI model is already initialized
    if initialized:
        return

    # Load environment variables
    app.config["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY")
    app.config["GEMINI_AI_MODEL"] = "gemini-1.5-flash"

    # Initialize the AI model
    agent = genai.Client(api_key=app.config["GEMINI_API_KEY"])

    initialized = True


def generate(prompt: str):
    global agent

    from main import app

    model = app.config["GEMINI_AI_MODEL"]
    response = agent.models.generate_content(model=model, contents=[prompt])

    return response.candidates[0].content.parts[0].text.strip()


def generate_structured(prompt: str):
    global agent

    from main import app

    model = app.config["GEMINI_AI_MODEL"]
    response = agent.models.generate_content(
        model=model,
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
        },
    )

    return response.candidates[0].content.parts[0].text.strip()