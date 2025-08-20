import os
import json
from backend.llm.parser import LLMParser

SAMPLES = [
    "Add a meeting tomorrow at 7:00 pm with Mr. Bansal. Remind me 1 hour before.",
    "create a meeting tomorrow at 5 PM with Alice"
]

if __name__ == '__main__':
    p = LLMParser()
    for s in SAMPLES:
        intent, entities = p.parse(s)
        print('Text:', s)
        print('Intent:', intent)
        print('Entities:', json.dumps(entities, indent=2))
        print('-'*40)
