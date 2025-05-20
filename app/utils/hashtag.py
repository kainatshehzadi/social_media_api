import re

def extract_hashtags(text: str):
    return list(set(re.findall(r"#(\w+)", text)))
