from src.entity_resolver import EntityResolver

def test_openai_variants():
    r = EntityResolver(["OpenAI"])
    assert r.resolve("Open AI", "STARTUP").canonical_name == "OpenAI"
    assert r.resolve("OpenAI, Inc.", "STARTUP").canonical_name == "OpenAI"
