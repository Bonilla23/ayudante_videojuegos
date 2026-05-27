import os
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
base_url = os.environ["AZURE_OPENAI_BASE_URL"]
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
api_key = os.environ["AZURE_OPENAI_API_KEY"]

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
    default_headers={"api-key": api_key},
)

resp = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Di hola en una frase."},
    ],
    max_tokens=50,
    temperature=0.2,
)

print(resp.choices[0].message.content)
print("USAGE:", resp.usage)  # <- tokens (prompt/completion/total)
