import os

import google.generativeai as genai
from flask import Flask

initialized: bool = False
agent: genai.GenerativeModel = None


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
    genai.configure(api_key=app.config["GEMINI_API_KEY"])
    agent = genai.GenerativeModel(app.config["GEMINI_AI_MODEL"])

    initialized = True