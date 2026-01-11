from google import genai
from config import GEMINI_API_KEY
import os

client = genai.Client(api_key=GEMINI_API_KEY)

try:
    print("Listing models...")
    # The new SDK might use user-friendly methods, let's try to find list_models equivalent or just try a generation
    # Actually, client.models.list() is likely
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(f"Error listing models: {e}")

try:
    print("\nAttempting generation with gemini-1.5-flash...")
    response = client.models.generate_content(model="gemini-1.5-flash", contents="Hello")
    print("Success with gemini-1.5-flash")
except Exception as e:
    print(f"Error with gemini-1.5-flash: {e}")

try:
    print("\nAttempting generation with gemini-1.5-flash-001...")
    response = client.models.generate_content(model="gemini-1.5-flash-001", contents="Hello")
    print("Success with gemini-1.5-flash-001")
except Exception as e:
    print(f"Error with gemini-1.5-flash-001: {e}")
