"""
Test suite for PartPulse data engine.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_engine import (
    safe_str,
    safe_bool,
    safe_int,
    normalize_complaints,
    extract_component_frequencies,
    STANDARD_COLUMNS
)

def test_safe_helpers():
    assert safe_str("  Hello  ") == "Hello"
    assert safe_str(None) == ""
    assert safe_str("N/A") == ""
    assert safe_str("None") == ""

    assert safe_bool(True) is True
    assert safe_bool(False) is False
    assert safe_bool("true") is True
    assert safe_bool("yes") is True
    assert safe_bool("1") is True
    assert safe_bool("0") is False
    assert safe_bool("No") is False

    assert safe_int(5) == 5
    assert safe_int("10") == 10
    assert safe_int(None) == 0
    assert safe_int("invalid") == 0
    print("✓ safe_helpers passed")

def test_normalization():
    mock_raw = [
        {
            "odiNumber": 12345678,
            "dateComplaintFiled": "10/15/2021",
            "dateOfIncident": "10/10/2021",
            "components": "STEERING, SUSPENSION",
            "summary": "Vehicle experienced severe oscillation at highway speeds.",
            "crash": True,
            "fire": "No",
            "numberOfInjuries": "0",
            "numberOfDeaths": 0,
            "vin": "1C4HJXDG8KW",
            "manufacturer": "Chrysler (FCA US, LLC)"
        },
        {
            "odiNumber": "87654321",
            "dateComplaintFiled": "01/05/2022",
            "dateOfIncident": "12/28/2021",
            "components": "ELECTRICAL SYSTEM",
            "summary": "Display cluster went blank while driving.",
            "crash": False,
            "fire": True,
            "numberOfInjuries": 2,
            "numberOfDeaths": 0,
            "vin": "1C4HJXDG9LW",
            "manufacturer": "Chrysler (FCA US, LLC)"
        }
    ]

    df = normalize_complaints(mock_raw)
    assert len(df) == 2
    assert df.loc[0, "odi_number"] == "12345678"
    assert bool(df.loc[0, "crash"]) is True
    assert bool(df.loc[0, "fire"]) is False
    assert bool(df.loc[1, "fire"]) is True
    assert int(df.loc[1, "injuries"]) == 2
    assert bool(df.loc[0, "safety_flag"]) is True
    assert bool(df.loc[1, "safety_flag"]) is True

    # Test component frequency extraction
    comp_df = extract_component_frequencies(df)
    comps = set(comp_df["Component"].tolist())
    assert "STEERING" in comps
    assert "SUSPENSION" in comps
    assert "ELECTRICAL SYSTEM" in comps
    print("✓ normalization & component extraction passed")

def test_empty_dataset():
    df_empty = normalize_complaints([])
    assert df_empty.empty
    for col in STANDARD_COLUMNS:
        assert col in df_empty.columns
    comp_empty = extract_component_frequencies(df_empty)
    assert comp_empty.empty
    print("✓ empty dataset handling passed")

if __name__ == "__main__":
    test_safe_helpers()
    test_normalization()
    test_empty_dataset()
    print("\nALL DATA ENGINE TESTS PASSED!")
