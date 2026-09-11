import base64
import json
import os

from flask import Flask

initialized: bool = False
agent = None


def _get_model_name(app: Flask) -> str:
    return app.config["OPENROUTER_MODEL"]


def _get_agent():
    global agent

    if agent is None:
        from openai import OpenAI

        headers: dict[str, str] = {}
        if os.environ.get("OPENROUTER_REFERER"):
            headers["HTTP-Referer"] = os.environ["OPENROUTER_REFERER"]
        if os.environ.get("OPENROUTER_TITLE"):
            headers["X-OpenRouter-Title"] = os.environ["OPENROUTER_TITLE"]

        agent = OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            default_headers=headers or None,
        )
    return agent


def _create_text_completion(prompt: str, return_json: bool = False) -> str:
    from openai import omit

    from main import app

    response = _get_agent().chat.completions.create(
        model=_get_model_name(app),
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"} if return_json else omit,
    )

    message = response.choices[0].message
    return (message.content or "").strip()


def _create_image_completion(
    prompt: str,
    image_data: bytes,
    mime_type: str,
    return_json: bool = False,
) -> str:
    from openai import omit

    from main import app

    image_url = f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"

    response = _get_agent().chat.completions.create(
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
        response_format={"type": "json_object"} if return_json else omit,
    )

    message = response.choices[0].message
    return (message.content or "").strip()


def init(app: Flask):
    global initialized

    # Skip if AI model is already initialized
    if initialized:
        return

    # Load environment variables
    app.config["OPENROUTER_API_KEY"] = os.environ.get("OPENROUTER_API_KEY")
    app.config["OPENROUTER_MODEL"] = os.environ.get("OPENROUTER_MODEL")
    app.config["OPENROUTER_REFERER"] = os.environ.get("OPENROUTER_REFERER")
    app.config["OPENROUTER_TITLE"] = os.environ.get("OPENROUTER_TITLE")

    initialized = True


def generate_text(prompt: str, return_json: bool = False):
    text = _create_text_completion(prompt, return_json=return_json)

    if return_json:
        return json.loads(text)
    return text


def generate_structured(prompt: str):
    return _create_text_completion(prompt, return_json=True)


def analyze_image(prompt: str, image_data: bytes, mime_type: str, return_json: bool = False):
    text = _create_image_completion(prompt, image_data, mime_type, return_json=return_json)

    if return_json:
        return json.loads(text)
    return text
