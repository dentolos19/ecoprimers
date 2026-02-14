import base64
import json
import mimetypes
import os

from flask import Flask
from openai import OpenAI

initialized: bool = False
agent: OpenAI | None = None


def _get_model_name(app: Flask) -> str:
    return app.config["OPENROUTER_MODEL"]


def _create_text_completion(prompt: str, return_json: bool = False) -> str:
    global agent

    from main import app

    response = agent.chat.completions.create(
        model=_get_model_name(app),
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"} if return_json else None,
    )

    message = response.choices[0].message
    return (message.content or "").strip()


def _create_image_completion(prompt: str, image_path: str, return_json: bool = False) -> str:
    global agent

    from main import app

    mime_type = mimetypes.guess_type(image_path)[0] or "image/jpeg"

    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    image_url = f"data:{mime_type};base64,{image_data}"

    response = agent.chat.completions.create(
        model=_get_model_name(app),
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        response_format={"type": "json_object"} if return_json else None,
    )

    message = response.choices[0].message
    return (message.content or "").strip()


def init(app: Flask):
    global initialized
    global agent

    # Skip if AI model is already initialized
    if initialized:
        return

    # Load environment variables
    app.config["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY")
    app.config["OPENROUTER_MODEL"] = os.environ.get("OPENROUTER_MODEL")
    app.config["OPENROUTER_SITE_URL"] = os.environ.get("OPENROUTER_SITE_URL")
    app.config["OPENROUTER_APP_NAME"] = os.environ.get("OPENROUTER_APP_NAME")

    headers: dict[str, str] = {}
    if app.config["OPENROUTER_SITE_URL"]:
        headers["HTTP-Referer"] = app.config["OPENROUTER_SITE_URL"]
    if app.config["OPENROUTER_APP_NAME"]:
        headers["X-Title"] = app.config["OPENROUTER_APP_NAME"]

    # Initialize the AI model
    agent = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=app.config["OPENROUTER_API_KEY"],
        default_headers=headers if headers else None,
    )

    initialized = True


def generate_text(prompt: str, return_json: bool = False):
    text = _create_text_completion(prompt, return_json=return_json)

    if return_json:
        return json.loads(text)
    return text


def generate_structured(prompt: str):
    return _create_text_completion(prompt, return_json=True)


def analyze_image(prompt: str, image_path: str, return_json: bool = False):
    text = _create_image_completion(prompt, image_path, return_json=return_json)

    if return_json:
        return json.loads(text)
    return text
