import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("Listing models...")
for m in client.models.list():
    print(f"  {m.name:45s}  {m.display_name}")
