import json
from openai import OpenAI

# Initialize OpenAI client
openai.api_key="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"

# OpenAI Prompt Template
PROMPT_TEMPLATE = """
You are an expert in biology and museum collections. Given the specimen name below, classify it into one of these categories and subcategories:

1. Géologie:
    - Minéralogie
    - Météorites
    - Roches océaniques

2. Paléontologie

3. Botanique

4. Invertébrés non arthropodes terrestres:
    - Mollusques
    - Crustacés
    - Cnidaires
    - Briozoaires/Brachiopodes
    - Porifera
    - Echinodermes
    - Vers
    - Polychètes
    - Meiofaune
    - Protistes

5. Arthropodes terrestres:
    - Coléoptères
    - Lépidoptères
    - Arachnides
    - Hémiptères
    - Hyménoptères
    - Diptères
    - Odonates

6. Vertébrés:
    - Mammifères
    - Oiseaux
    - Reptiles et amphibiens
    - Ichtyologie

7. Préhistoire

8. Ressources biologiques:
    - Cyanobactéries et microalgues eucaryotes
    - Souches fongiques
    - Eucaryotes unicellulaires
    - Tissus et cellules de vertébrés
    - Chimiothèque

9. Animaux vivants:
    - PZP
    - Ménagerie

10. Végétaux vivants

11. Anthropologie

Task:
- If the input is a valid specimen name, return the best-matching category and subcategory (if applicable) in the format: "Category, Subcategory".
- If the input is not a valid specimen name, return "None".
- Do not provide explanations or additional text.

Specimen: {specimen}
"""

def classify_specimen(specimen_name):
    """
    Sends a specimen name to OpenAI GPT for classification into predefined categories and subcategories.
    """
    try:
        prompt = PROMPT_TEMPLATE.format(specimen=specimen_name)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during OpenAI classification: {e}")
        return None

def process_second_layer(input_json, output_json):
    """
    Processes a JSON file of documents to classify specimen names into categories and subcategories.
    """
    try:
        with open(input_json, "r", encoding="utf-8") as infile:
            data = json.load(infile)

        processed_data = []

        for article in data:
            specimen_names = article.get("specimen_names", [])
            specimen_categories = []

            for specimen in specimen_names:
                category_subcategory = classify_specimen(specimen)
                if category_subcategory and category_subcategory != "None":
                    specimen_categories.append(category_subcategory)

            if specimen_categories:
                article["First_category"] = specimen_categories
                processed_data.append(article)

        with open(output_json, "w", encoding="utf-8") as outfile:
            json.dump(processed_data, outfile, ensure_ascii=False, indent=4)

        print(f"Processed data saved to '{output_json}'.")
    except Exception as e:
        print(f"Error processing specimens: {e}")
