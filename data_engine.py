"""
PartPulse - Core Data Engine
Handles NHTSA API querying, response validation, edge cases,
schema normalization, and metric calculations.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import requests

NHTSA_COMPLAINTS_API = "https://api.nhtsa.gov/complaints/complaintsByVehicle"

STANDARD_COLUMNS = [
    "odi_number",
    "report_date",
    "parsed_date",
    "incident_date",
    "components",
    "summary",
    "crash",
    "fire",
    "injuries",
    "deaths",
    "vin",
    "manufacturer",
    "safety_flag"
]


def safe_str(val: Optional[object]) -> str:
    """Safely converts any API value into a clean stripped string."""
    if val is None:
        return ""
    s = str(val).strip()
    return "" if s.upper() in ("N/A", "NONE", "NULL", "UNKNOWN") else s


def safe_bool(val: Optional[object]) -> bool:
    """
    Accurately parses NHTSA boolean flags.
    Handles booleans (True/False), integers (1/0), and strings ('yes'/'no', 'true'/'false').
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val > 0)
    if isinstance(val, str):
        return val.strip().lower() in ("true", "yes", "1", "y")
    return False


def safe_int(val: Optional[object]) -> int:
    """Safely converts count fields to integer, defaulting to 0."""
    if val is None:
        return 0
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return 0


def fetch_nhtsa_complaints(make: str, model: str, year: int) -> Tuple[List[Dict], Optional[str]]:
    """
    Fetches raw complaints from NHTSA's official public complaintsByVehicle API.
    
    CRITICAL EDGE CASE HANDLED:
    When 0 complaints exist for a vehicle or the spelling does not match NHTSA records,
    the federal API responds with HTTP 400 and a JSON body:
    {'count': 0, 'message': 'Results returned successfully', 'results': []}.
    This function recognizes this as an empty dataset rather than a network error.
    
    Returns:
        (results_list, error_message)
    """
    params = {
        "make": make.strip(),
        "model": model.strip(),
        "modelYear": int(year)
    }
    try:
        resp = requests.get(NHTSA_COMPLAINTS_API, params=params, timeout=20)
        
        # NHTSA-specific edge case: HTTP 400 returned for 0 matches
        if resp.status_code == 400:
            try:
                payload = resp.json()
                if payload.get("count") == 0 or not payload.get("results"):
                    return [], None
            except Exception:
                pass
            return [], None
            
        resp.raise_for_status()
        payload = resp.json()
        raw_list = payload.get("results") or payload.get("Results") or []
        return raw_list, None

    except requests.exceptions.Timeout:
        return [], "The NHTSA public API request timed out (20s). The federal server may be experiencing high load."
    except requests.exceptions.ConnectionError:
        return [], "Could not connect to api.nhtsa.gov. Please verify your internet connection."
    except requests.exceptions.RequestException as err:
        return [], f"NHTSA API request failed: {err}"
    except ValueError as err:
        return [], f"Failed to parse NHTSA response as valid JSON: {err}"


def normalize_complaints(raw_rows: List[Dict]) -> pd.DataFrame:
    """
    Transforms raw API dictionary rows into a clean, strictly typed pandas DataFrame.
    Gracefully handles schema drift, missing fields, and date parsing.
    """
    if not raw_rows:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    cleaned = []
    for r in raw_rows:
        # Case-insensitive key lookup dictionary
        low_map = {str(k).lower(): v for k, v in r.items()}
        
        def get_val(*field_names):
            for f in field_names:
                v = low_map.get(f.lower())
                if v is not None and str(v).strip() != "":
                    return v
            return None

        odi_id = safe_str(get_val("odiNumber", "odiID", "complaintId"))
        rep_date_str = safe_str(get_val("dateComplaintFiled", "dateComplaintFiledToNHTSA", "dateAdded"))
        inc_date_str = safe_str(get_val("dateOfIncident", "incidentDate"))
        comps = safe_str(get_val("components", "component", "affectedComponent")) or "UNSPECIFIED"
        summ = safe_str(get_val("summary", "description", "consumerDescription", "notes"))
        crash_flag = safe_bool(get_val("crash", "crashOccurred"))
        fire_flag = safe_bool(get_val("fire", "fireOccurred"))
        injuries = safe_int(get_val("numberOfInjuries", "injuries"))
        deaths = safe_int(get_val("numberOfDeaths", "deaths"))
        vin = safe_str(get_val("vin"))
        mfg = safe_str(get_val("manufacturer"))

        # Composite safety signal: any crash, fire, or injury noted
        has_safety_event = crash_flag or fire_flag or (injuries > 0) or (deaths > 0)

        cleaned.append({
            "odi_number": odi_id,
            "report_date": rep_date_str,
            "incident_date": inc_date_str,
            "components": comps,
            "summary": summ,
            "crash": crash_flag,
            "fire": fire_flag,
            "injuries": injuries,
            "deaths": deaths,
            "vin": vin,
            "manufacturer": mfg,
            "safety_flag": has_safety_event
        })

    df = pd.DataFrame(cleaned)
    df["parsed_date"] = pd.to_datetime(df["report_date"], errors="coerce")
    return df


def extract_component_frequencies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Splits multi-component strings (e.g. 'STEERING, SUSPENSION') into distinct
    atomic components so frequencies reflect true part concerns rather than combinations.
    """
    if df.empty or "components" not in df.columns:
        return pd.DataFrame(columns=["Component", "Count", "Percentage"])

    # Expand comma, semicolon, and slash separated components
    raw_series = (
        df["components"]
        .dropna()
        .str.split(r"[,;/|]")
        .explode()
        .str.strip()
        .str.upper()
    )
    
    clean_series = raw_series[
        (raw_series != "") & (raw_series != "UNKNOWN") & (raw_series != "N/A")
    ]
    if clean_series.empty:
        return pd.DataFrame(columns=["Component", "Count", "Percentage"])

    counts = clean_series.value_counts().reset_index()
    counts.columns = ["Component", "Count"]
    counts["Percentage"] = (counts["Count"] / len(df) * 100).round(1)
    return counts
