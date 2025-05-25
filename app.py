from flask import Flask, request, jsonify
from flask_cors import CORS
from OpenAI_FirsLayer import query_mnhn_model
from OpenAI_SecondLayer import classify_specimen
from OpenAI_ThirdLayer import validate_specimen
from pyzotero import zotero

app = Flask(__name__)
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    paragraphs = data.get("paragraphs", [])
    title = data.get("title", "Untitled")
    url = data.get("url", "")
    openai_key = data.get("openai_key", "")

    validated_specimens = []

    # Layer 1: MNHN detection + name extraction
    all_names = []
    for paragraph in paragraphs:
        names = query_mnhn_model(paragraph)
        if names and names.lower() != "none":
            all_names.extend([n.strip() for n in names.split(",")])

    all_names = list(set(all_names))  # Remove duplicates

    # Layer 2 & 3: Categorization + Validation
    for name in all_names:
        category_subcat = classify_specimen(name)
        if category_subcat and category_subcat.lower() != "none":
            cat, subcat = (category_subcat.split(",") + ["None"])[:2]
            result = validate_specimen(name, cat.strip(), subcat.strip())
            if result:
                validated_specimens.append({
                    "name": result[0].strip(),
                    "category": result[1].strip(),
                    "subcategory": result[2].strip()
                })

    return jsonify(validated_specimens)


@app.route("/zotero", methods=["POST"])
def zotero_push():
    data = request.json

    try:
        zot = zotero.Zotero(
            data.get("zotero_library_id", ""),
            data.get("zotero_type", "user"),
            data.get("zotero_key", "")
        )

        tags = []
        for s in data.get("validated_specimens", []):
            for field in [s.get("name", ""), s.get("category", ""), s.get("subcategory", "")]:
                field = field.strip()
                if field and field.lower() != "none":
                    tags.append({"tag": field})

        item = {
            "itemType": "journalArticle",
            "title": data.get("title", "Untitled"),
            "url": data.get("url", "https://example.com"),
            "tags": tags,
            "collections": [],
            "DOI": data.get("doi", "n/a"),
            "language": data.get("language", "en"),
            "publicationTitle": data.get("journal_title", "Unknown"),
            "ISSN": data.get("ISSN", "0000-0000"),
            "date": data.get("date", "2025-01-01")
        }

        response = zot.create_items([item])
        return jsonify({"status": "success", "response": response})
    except Exception as e:
        print(f"❌ Error pushing to Zotero: {e}")  # Will show in Railway logs
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
