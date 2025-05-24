import requests

BACKEND_URL = "http://127.0.0.1:5000/zotero"

payload = {
    "title": "Test Article",
    "url": "http://example.com",
    "doi": "10.1234/test-doi",
    "language": "en",
    "journal": "Journal of Testing",
    "issn": "1234-5678",
    "date": "2025-05-24",
    "validated_specimens": [
        {
            "name": "Panthera leo",
            "category": "Vertébrés",
            "subcategory": "Mammifères"
        }
    ],
    "zotero_key": "AJ7jW0HWRUufShR3FeO2717h",         # 🔐 Replace this
    "zotero_library_id": "15818985",       # 🔐 Replace this
    "zotero_type": "user"                         # Or "group" if using a group library
}

response = requests.post(BACKEND_URL, json=payload)

print("Status Code:", response.status_code)
print("Response:")
print(response.json())
