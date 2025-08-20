from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from functools import lru_cache
import re

INTENTS = [
    'calendar.create_event',
    'sheets.append_row',
    'docs.create',
    'gmail.send'
]

class LLMParser:
    def __init__(self, intent_model: str = 'facebook/bart-large-mnli', ner_model: str = 'google/flan-t5-base'):
        self.intent_model_name = intent_model
        self.ner_model_name = ner_model
        self._intent_pipe = None
        self._ner_pipe = None

    @property
    def intent_pipe(self):
        if self._intent_pipe is None:
            self._intent_pipe = pipeline('zero-shot-classification', model=self.intent_model_name)
        return self._intent_pipe

    @property
    def ner_pipe(self):
        if self._ner_pipe is None:
            self._ner_pipe = pipeline('text2text-generation', model=self.ner_model_name)
        return self._ner_pipe

    def classify_intent(self, text: str) -> str:
        result = self.intent_pipe(text, candidate_labels=INTENTS)
        return result['labels'][0]

    def extract_entities(self, text: str, intent: str) -> dict:
        # Prompt engineering for simple structured extraction
        if intent == 'calendar.create_event':
            prompt = (
                "Extract calendar event fields as JSON with keys: title, date, time, reminder_minutes, description, attendees. "
                f"Text: {text}\nReturn JSON:"
            )
        elif intent == 'sheets.append_row':
            prompt = (
                "Extract sheets fields as JSON with keys: sheet_name, row(list of strings). "
                f"Text: {text}\nReturn JSON:"
            )
        elif intent == 'docs.create':
            prompt = (
                "Extract docs fields as JSON with keys: name, content. "
                f"Text: {text}\nReturn JSON:"
            )
        elif intent == 'gmail.send':
            prompt = (
                "Extract gmail fields as JSON with keys: to, subject, body. "
                f"Text: {text}\nReturn JSON:"
            )
        else:
            return {}

        out = self.ner_pipe(prompt, max_new_tokens=128)
        text_out = out[0]['generated_text']
        # Heuristic to find JSON in output
        match = re.search(r"\{[\s\S]*\}", text_out)
        if match:
            import json
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {}

    def parse(self, text: str):
        intent = self.classify_intent(text)
        entities = self.extract_entities(text, intent)
        return intent, entities
