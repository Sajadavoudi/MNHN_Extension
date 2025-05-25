from pyzotero import zotero
import json

# Zotero API credentials
"""
ZOTERO_LIBRARY_ID = "15818985"  # Replace with your Zotero library ID
ZOTERO_API_KEY = "AJ7jW0HWRUufShR3FeO2717h"  # Replace with your Zotero API key
ZOTERO_LIBRARY_TYPE = "user"  # Use "group" if working with a Zotero group library
"""

# Initialize Zotero API
zot = zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, ZOTERO_API_KEY)

# Load JSON file
with open(input_json, "r", encoding="utf-8") as file:
    data = json.load(file)

# Type mapping for valid Zotero item types
type_mapping = {
    "research-article": "journalArticle",
    # Add other mappings if needed
}

# Iterate through articles
for article in data:
    title = article.get("title", "No Title")
    url = article.get("url", "No URL")
    tags = article.get("tags", [])
    validated_specimens = article.get("validated_specimens", [])

    # Extract validated specimens into tags
    for specimen in validated_specimens:
        name = specimen.get("name", "")
        category = specimen.get("category", "")
        subcategory = specimen.get("subcategory", "")
        
        # Remove unwanted words or phrases from specimen elements
        for element in [name, category, subcategory]:
            if element:
                element = (element
                           .replace("Correct", "")
                           .replace("Valid", "")
                           .replace("Confirmation", "")
                           .replace("\n", "")
                           .replace("Confirmed", "")
                           .replace("Correct:", "")
                           .replace("Valid:", "")
                           .replace("Confirmation:", "")
                           .replace("\n", "")
                           .replace("Confirmed:", "")
                           .strip())
        
        # Add cleaned elements to tags
        if name:
            tags.append(name)
        if category:
            tags.append(category)
        if subcategory and subcategory.lower() != "none":
            tags.append(subcategory)

    # Map type to valid Zotero item type
    item_type = type_mapping.get(article.get("type", ""), "journalArticle")
    date = "-".join(map(str, article.get("date", [])))  # Format date as YYYY-MM-DD
    doi = article.get("doi", "")
    language = article.get("language", "")
    journal_title = article.get("journal_title", "")
    issn = article.get("ISSN", "")

    # Prepare tags
    zotero_tags = [{"tag": tag} for tag in tags]

    # Create Zotero item
    item = {
        "itemType": item_type,
        "title": title,
        "url": url,
        "tags": zotero_tags,
        "collections": [],  # Specify collection ID if needed
        "date": date,
        "DOI": doi,
        "language": language,
        "publicationTitle": journal_title,
        "ISSN": issn,
    }

    # Add item to Zotero
    try:
        response = zot.create_items([item])
        if "successful" in response and response["successful"]:
            print(f"Added '{title}' to Zotero successfully!")
        else:
            print(f"Failed to add '{title}'. Response: {response}")
    except Exception as e:
        print(f"Error adding '{title}': {e}")
