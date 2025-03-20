import os

import PIL
import PIL.Image
import PIL.ImageFile
from flask import Flask, json
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
    app.config["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY")
    app.config["GOOGLE_AI_MODEL"] = os.environ.get("GOOGLE_AI_MODEL")

    # Initialize the AI model
    agent = genai.Client(api_key=app.config["GOOGLE_API_KEY"])

    initialized = True


def generate_text(prompt: str, return_json: bool = False):
    global agent

    from main import app

    model = app.config["GOOGLE_AI_MODEL"]
    response = agent.models.generate_content(
        model=model, contents=[prompt], config={"response_mime_type": "application/json"} if return_json else None
    )

    text = response.candidates[0].content.parts[0].text.strip()

    if return_json:
        return json.loads(text)
    return text


def generate_structured(prompt: str):
    global agent

    from main import app

    model = app.config["GOOGLE_AI_MODEL"]
    response = agent.models.generate_content(
        model=model,
        contents=[prompt],
        config={
            "response_mime_type": "application/json",
        },
    )

    return response.candidates[0].content.parts[0].text.strip()


def analyze_image(prompt: str, image_path: str, return_json: bool = False):
    global agent

    from main import app

    model = app.config["GOOGLE_AI_MODEL"]
    image = PIL.Image.open(image_path)
    response = agent.models.generate_content(
        model=model,
        contents=[prompt, image],
        config={"response_mime_type": "application/json"} if return_json else None,
    )

    text = response.candidates[0].content.parts[0].text.strip()

    if return_json:
        return json.loads(text)
    return text