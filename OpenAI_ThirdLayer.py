import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace with your actual key

# Predefined categories and subcategories
CATEGORY_SUBCATEGORY_MAPPING = {
    "Géologie": ["Minéralogie", "Météorites", "Roches océaniques"],
    "Paléontologie": [],
    "Botanique": [],
    "Invertébrés non arthropodes terrestres": [
        "Mollusques", "Crustacés", "Cnidaires", "Briozoaires/Brachiopodes", "Porifera",
        "Echinodermes", "Vers", "Polychètes", "Meiofaune", "Protistes"
    ],
    "Arthropodes terrestres": [
        "Coléoptères", "Lépidoptères", "Arachnides", "Hémiptères", "Hyménoptères", "Diptères", "Odonates"
    ],
    "Vertébrés": ["Mammifères", "Oiseaux", "Reptiles et amphibiens", "Ichtyologie"],
    "Préhistoire": [],
    "Ressources biologiques": [
        "Cyanobactéries et microalgues eucaryotes", "Souches fongiques", "Eucaryotes unicellulaires",
        "Tissus et cellules de vertébrés", "Chimiothèque"
    ],
    "Animaux vivants": ["PZP", "Ménagerie"],
    "Végétaux vivants": [],
    "Anthropologie": []
}

# OpenAI Prompt Template
PROMPT_TEMPLATE = """
You are a taxonomy and biology expert. Verify the provided specimen name, category, and subcategory. If the specimen aligns with the given category and subcategory, confirm it by giving the same thing out. If not, provide the corrected category and subcategory.

Categories and subcategories:
{categories}

Input:
Specimen Name: {name}
Category: {category}
Subcategory: {subcategory}

Output:
[Specimen Name], [Category], [Subcategory]
"""

def validate_specimen(specimen_name, category, subcategory):
    """
    Validates the category and subcategory of a specimen using OpenAI.
    """
    try:
        formatted_categories = "\n".join(
            [f"- {cat}: {', '.join(subcats) if subcats else 'None'}" for cat, subcats in CATEGORY_SUBCATEGORY_MAPPING.items()]
        )

        prompt = PROMPT_TEMPLATE.format(
            categories=formatted_categories,
            name=specimen_name,
            category=category,
            subcategory=subcategory or "None"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result = response.choices[0].message.content.strip()

        if result.count(",") == 2:
            return result.split(",")
        return None
    except Exception as e:
        print(f"Error validating specimen: {e}")
        return None

def process_specimen_validation(input_file, output_file):
    """
    Processes a JSON file to validate specimen names and their category/subcategory.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        validated_data = []

        for article in data:
            specimen_names = article.get("specimen_names", [])
            specimen_categories = article.get("First_category", [])

            clean_specimens = []

            for name, category in zip(specimen_names, specimen_categories):
                subcategory = category.split(",")[-1].strip() if "," in category else "None"
                main_category = category.split(",")[0].strip()

                validation_result = validate_specimen(name, main_category, subcategory)
                if validation_result:
                    clean_specimens.append({
                        "name": validation_result[0].strip(),
                        "category": validation_result[1].strip(),
                        "subcategory": validation_result[2].strip()
                    })

            if clean_specimens:
                article["validated_specimens"] = clean_specimens
                validated_data.append(article)

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(validated_data, file, ensure_ascii=False, indent=4)

        print(f"Validated data saved to '{output_file}'.")
    except Exception as e:
        print(f"Error processing validation: {e}")
