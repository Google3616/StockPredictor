import logging
import stanza

# Suppress Stanza logging
logging.getLogger("stanza").setLevel(logging.WARNING)

# Initialize the Stanza NLP pipeline
stanza.download('en')  # Download the English model (only needed once)
nlp = stanza.Pipeline('en')  # Initialize pipeline

# Example function
def extract_name_with_stanza(headline):
    """
    Extracts names from a headline using stanza's Named Entity Recognition (NER).

    Args:
        headline (str): The headline text.

    Returns:
        list: A list of names found in the headline.
    """
    # Process the text
    doc = nlp(headline.replace("’s","").replace("'s",""))

    # Extract entities labeled as PERSON
    names = [ent.text for ent in doc.entities if ent.type == "PERSON"]

    return names

# Example usage
headline = "Inside Elon Musk’s Plan to Slash Government Costs"
names = extract_name_with_stanza(headline)
print("Extracted Names:", names)
