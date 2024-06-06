import re
import unicodedata


def normalize_text(text):
    """
    Normalizes the input text by converting it to lowercase, removing
    diacritics, and stripping special characters and extra whitespace.

    Parameters:
        text (str): The input text to be normalized.

    Returns:
        str: The normalized text.
    """
    text = text.lower()
    text = (unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
            .decode('utf-8', 'ignore'))
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()
