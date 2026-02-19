import json

def generate_raw_json(text):
    return json.dumps({"raw_text": text}, indent=4)
