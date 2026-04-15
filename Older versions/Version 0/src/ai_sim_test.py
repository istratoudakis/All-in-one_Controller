import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Δημιουργία του Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

print("\n" + "="*50)
print("   ΔΙΑΘΕΣΙΜΑ ΜΟΝΤΕΛΑ ΓΙΑ ΤΟ API KEY ΣΟΥ")
print("="*50)

try:
    # Στο νέο SDK χρησιμοποιούμε client.models.list()
    for model in client.models.list():
        # Διορθωμένα attributes: .name και .supported_actions
        actions = ", ".join(model.supported_actions) if model.supported_actions else "None"
        print(f"ID: {model.name:<30} | Actions: {actions}")
except Exception as e:
    print(f"[ERROR]: {e}")

print("="*50 + "\n")