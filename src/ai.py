import google.generativeai as genai

from environment import GEMINI_API_KEY

model: genai.GenerativeModel = None


def init():
    global model
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")