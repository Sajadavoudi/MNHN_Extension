import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")  # Replace with your actual key

# OpenAI Prompt Template
PROMPT_TEMPLATE = """
You are a biology and taxonomy expert working with historical museum records.

Your task is to determine if the paragraph below explicitly mentions one or more biological specimens from the MNHN collection (Muséum National d’Histoire Naturelle in Paris).

🔎 Specifically:

1. Only consider the specimen(s) if they are explicitly linked to the MNHN collection.
   - This can include: collection codes (e.g., MNHN.F.12345), phrases like "in the MNHN collection", or specimen accession details.

2. Ignore:
   - Mentions of MNHN as an institution (e.g., employment, authorship)
   - Mentions of other collections (e.g., MNHNL, AMNH, NHMUK, ZFMK, or any other)
   - Cases where the species is discussed but not tied to MNHN
   - People, affiliations, or vague geographic mentions

3. Return the scientific names (e.g., *Genus species*) of the specimens clearly associated with MNHN.

4. If no such specimens are found, return: None

💬 Paragraph:
\"\"\"
{paragraph}
\"\"\"

Output (only scientific names separated by commas or "None"):
"""


def query_mnhn_model(paragraph):
    """
    Sends a paragraph to OpenAI GPT to determine if it mentions MNHN specimens and extracts the scientific names.
    """
    try:
        prompt = PROMPT_TEMPLATE.format(paragraph=paragraph)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during OpenAI query: {e}")
        return None

def process_json_file(input_file, output_file):
    """
    Reads paragraphs from a JSON file, queries the OpenAI model, and stores results in a new JSON file.
    Excludes documents where no specimen is mentioned.
    """
    try:
        print(f"Reading input file: {input_file}")
        with open(input_file, "r", encoding="utf-8") as infile:
            data = json.load(infile)

        if not isinstance(data, list):
            print("Error: Input JSON should be a list of documents.")
            return

        first_Layer_data = []

        for document in data:
            print(f"Processing document: {document.get('title', 'Untitled')}")
            paragraphs = document.get("paragraphs", [])

            if not isinstance(paragraphs, list):
                print("Warning: 'paragraphs' should be a list. Skipping document.")
                continue

            specimen_names = []

            for paragraph in paragraphs:
                response = query_mnhn_model(paragraph)
                if response and response != "None":
                    print(f"Valid Response Found: {response}")
                    if isinstance(response, str):
                        specimen_names.extend(response.split(", "))

            if specimen_names:
                print(f"Adding specimen names to document: {specimen_names}")
                document["specimen_names"] = specimen_names
                first_Layer_data.append(document)

        if not first_Layer_data:
            print("No valid data to write to the output file.")
        else:
            print(f"Writing filtered data to {output_file}")
            with open(output_file, "w", encoding="utf-8") as outfile:
                json.dump(first_Layer_data, outfile, ensure_ascii=False, indent=4)
                print(f"Filtered data has been saved to {output_file}.")

    except json.JSONDecodeError as jde:
        print(f"JSON decoding error: {jde}")
    except FileNotFoundError as fnfe:
        print(f"File not found: {fnfe}")
    except Exception as e:
        print(f"Unexpected error: {e}")
