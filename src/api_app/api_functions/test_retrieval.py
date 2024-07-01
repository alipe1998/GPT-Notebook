import tiktoken
import retrieval as ret

def test_empty_string():
    # test empty string
    text = ""
    expected_tokens = 0
    actual_tokens = ret.count_tokens(text)
    assert actual_tokens == expected_tokens, "Empty string should have 0 tokens"

    # test one word
    text = "Hello"
    expected_tokens = 1  # May vary depending on the model's tokenization
    actual_tokens = ret.count_tokens(text)
    assert actual_tokens == expected_tokens, "Single word should have 1 token (may vary)"

    # test a sentence
    text = "This is a test sentence."
    expected_tokens = len(tiktoken.split(text, model="gpt-3.5-turbo"))  # More accurate token count
    actual_tokens = ret.count_tokens(text)
    assert actual_tokens == expected_tokens, "Sentence should have correct token count"
