from google import genai
import inspect

client = genai.Client(api_key="TEST")
try:
    print(inspect.signature(client.files.upload))
except Exception as e:
    print(f"Error inspecting signature: {e}")
    # Fallback: dir()
    print(dir(client.files))
