import re

def clean_text(text):
    """Cleans raw text by removing HTML, URLs, and unnecessary characters."""
    
    # Remove HTML tags
    text = re.sub(r"<.*?>", "", text)

    # Remove URLs (http, https, www)
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # Remove non-alphanumeric characters except spaces and basic punctuation (. , ! ?)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)

    # Normalize multiple spaces & strip leading/trailing whitespace
    text = " ".join(text.split())

    return text
