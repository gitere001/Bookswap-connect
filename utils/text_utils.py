import re
import unicodedata


def normalize_text(text):
    text = text.lower()
    text = (unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
            .decode('utf-8', 'ignore'))
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()
