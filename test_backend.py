import requests

BACKEND_URL = "http://127.0.0.1:5000/analyze"  # local server

payload = {
    "paragraphs": [
        "The fossil specimen MNHN.F.12345 was identified as *Panthera leo* from the Muséum National d’Histoire Naturelle, Paris."
    ],
    "title": "Test Article",
    "url": "http://example.com",
    "openai_key": "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"  # 🔐 Replace with your actual OpenAI key
}

response = requests.post(BACKEND_URL, json=payload)

print("Status Code:", response.status_code)
print("Response JSON:")
print(response.json())
