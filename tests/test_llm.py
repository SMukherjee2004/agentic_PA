import pytest
from backend.llm.parser import LLMParser

@pytest.mark.parametrize("text", [
    "create a meeting tomorrow at 5 PM with Alice",
    "add event with Bob at 7pm tomorrow",
])
def test_intent_calendar(text):
    parser = LLMParser()
    intent, _ = parser.parse(text)
    assert intent == 'calendar.create_event'


def test_entity_extraction_calendar():
    parser = LLMParser()
    intent, entities = parser.parse("Add a meeting tomorrow at 7:00 pm with Mr. Bansal. Remind me 60 minutes before.")
    assert intent == 'calendar.create_event'
    # best-effort fields present (model dependent)
    assert 'date' in entities
