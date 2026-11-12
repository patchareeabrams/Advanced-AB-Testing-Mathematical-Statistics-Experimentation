import pandas as pd
from src.analyze import analyze

def test_identical_conversion_rates():
    df = pd.DataFrame({"user_id": range(1,9), "variant": ["A"]*4+["B"]*4, "converted": [0,1,0,1]*2})
    _, result = analyze(df)
    assert result["p_value"] == 1.0
    assert result["lift_absolute"] == 0

def test_invalid_duplicate_users():
    df = pd.DataFrame({"user_id": [1,1], "variant": ["A","B"], "converted": [0,1]})
    try: analyze(df)
    except ValueError: return
    assert False, "Expected ValueError"
