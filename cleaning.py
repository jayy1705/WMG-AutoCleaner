"""
cleaning.py

Reusable data-cleaning functions: converting/standardizing customer names
and grouping raw store names under a canonical parent/group name.

Import this from a notebook (for testing) or from app.py (the GUI).
"""

import re
import pandas as pd
import numpy as np


# 1. RAW MAPPING DATA
# Kept as a list of (raw_name, group_name) pairs instead of a dict literal.
RAW_NAME_GROUP_PAIRS = [
    ('ST ROSYAM MART (SEMENYIH)', 'Sri Ternak'),
    ('SRI TERNAK FOOD MART SDN BHD, SELAYANG', 'Sri Ternak'),
    ('SRI TERNAK MART (SK) SDN BHD', 'Sri Ternak'),
    ('ST ROSYAM MART (SHAH ALAM)', 'Sri Ternak'),
    ('ST ROSYAM MART SDN BHD - KLANG', 'Sri Ternak'),
    ('ST ROSYAM MART SDN BHD-JAKEL SQUARE', 'Sri Ternak'),
    ('ST ROSYAM MART SDN BHD (SETIAWANGSA)', 'Sri Ternak'),
    ('ST ROSYAM MART SDN BHD - SNWG', 'Sri Ternak'),
    ('ST ROSYAM MART (SG BULOH) SDN BHD', 'Sri Ternak'),
    ('ST ROSYAM MART (TMN EHSAN) SDN BHD', 'Sri Ternak'),
    ('ST ROSYAM WHOLESALE EXPRESS SDN BHD (R002) USJ', 'Sri Ternak'),
    ('CS BROTHERS SDN BHD', 'CS BROTHERS'),
    ('CS GROCER SDN BHD (KAJANG REKO)', 'CS GROCER'),
    ('CS GROCER SDN BHD (PUCHONG)', 'CS GROCER'),
    ('TARGET SUPERMARKET SDN BHD - CAWANGAN MASAI (TMS)', 'TARGET'),
    ('TARGET SUPERMARKET (BENUT) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (AYER HITAM) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (PARIT RAJA) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET SDN BHD - CAWANGAN YONG PENG', 'TARGET'),
    ('TARGET SUPERMARKET (SRI KLUANG) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (BATU PAHAT) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET SDN BHD- BRANCH GPR', 'TARGET'),
    ('TARGET SUPERMARKET (KLUANG) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (TAMAN KLUANG PERDANA) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (PONTIAN) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (KULAI) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET (BUKIT BAKRI) SDN BHD', 'TARGET'),
    ('TARGET SUPERMARKET SDN BHD -BRANCH TSC', 'TARGET'),
    ('BAHAU ZEMART SDN BHD', 'TABAHAU ZEMART SDN BHD'),
    ('BILLION MART (TANJUNG CHAT) SDN. BHD.', 'BILLION MART (TANJUNG CHAT) SDN. BHD.'),
    ('BORONG DIN AS CASH & CARRY (ALOR JANGGUS)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY (PADANG BESAR)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY (SERIAB)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SB - PENDANG', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (JEJAWI)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (KANGAR KAPITOL)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (KANGAR)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (KUALA PERLIS)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (PAUH)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (POKOK SENA)', 'BORONG DIN AS CASH & CARRY'),
    ('BORONG DIN AS CASH & CARRY SDN BHD (SIMPANG EMPAT)', 'BORONG DIN AS CASH & CARRY'),
    ('CB FROZEN FOOD SDN BHD - DC', 'CB FROZEN FOOD SDN BHD - DC'),
    ('FS FAMILY STORE SDN BHD', 'FS FAMILY STORE SDN BHD'),
    ('GT MART SDN BHD', 'GT MART SDN BHD'),
    ('HOCK MEI TRADING SDN BHD (TAMAN MEDAN)', 'HOCK MEI TRADING SDN BHD'),
    ('KENWINGSTON GROCER SDN. BHD.', 'KENWINGSTON GROCER SDN. BHD.'),
    ('KENWINGSTON GROCER SDN. BHD. - KSG CYBER JAYA', 'KENWINGSTON GROCER SDN. BHD.'),
    ('KK FAMILY MART SDN BHD', 'KK FAMILY MART SDN BHD'),
    ('KUMPULAN PASARAYA PANTAI TIMUR -BUKIT BUNGA', 'KUMPULAN PASARAYA PANTAI TIMUR'),
    ('LS MART PASARAYA  SDN BHD (PS2)', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA (SG.DUA) SDN.BHD.', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA (TANGLING) SDN BHD', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN BHD (BTM)', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN BHD (GSP)', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN BHD (GTK)', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN BHD (TASEK GELUGOR)', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN BHD-SPC', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN. BHD (J.JURU) HQ', 'LS MART PASARAYA SDN BHD'),
    ('LS MART PASARAYA SDN.BHD. (JURU)', 'LS MART PASARAYA SDN BHD'),
    ('MANTIN ZEMART SDN BHD', 'MANTIN ZEMART SDN BHD'),
    ('MASLEE EXPRESS SDN. BHD.', 'MASLEE EXPRESS SDN. BHD.'),
    ('PANTAI TIMOR HYPERMARKET SDN BHD-PENGKALAN CHEPA', 'PANTAI TIMOR HYPERMARKET SDN BHD-PENGKALAN CHEPA'),
    ('PANTAI TIMOR SHOPPING CENTRE (RANTAU) SDN BHD', 'PANTAI TIMOR SHOPPING CENTRE (RANTAU) SDN BHD'),
    ('PASARAYA BORONG DIN AS CASH & CARRY SDN BHD (KUALA NERANG)', 'BORONG DIN AS CASH & CARRY'),
    ('PASARAYA BORONG DIN AS SD BHD (AYER HITAM)', 'BORONG DIN AS CASH & CARRY'),
    ('PASARAYA BORONG DIN AS SDN BHD (JITRA BDI)', 'PASARAYA BORONG DIN AS SDN BHD'),
    ('PASARAYA BORONG DIN AS SDN BHD (MERGONG)', 'PASARAYA BORONG DIN AS SDN BHD'),
    ('PASARAYA BSK SDN BHD (CAWANGAN RAWANG)', 'PASARAYA BSK SDN BHD'),
    ('PASARAYA BSK SDN. BHD. (CAW. KUALA SELANGOR)', 'PASARAYA BSK SDN BHD'),
    ('PASARAYA ECON JAYA ( KELANTAN) SDN BHD', 'PASARAYA ECON JAYA SDN BHD'),
    ('PASARAYA ECON JAYA (MACHANG) SDN BHD', 'PASARAYA ECON JAYA SDN BHD'),
    ('PASARAYA HWA THAI SDN BHD', 'PASARAYA HWA THAI SDN BHD'),
    ('PASARAYA KITO (PT) SDN BHD', 'PASARAYA KITO (PT) SDN BHD'),
    ('PASARAYA PANTAI TIMOR (PASIR MAS)', 'PASARAYA PANTAI TIMOR'),
    ('PASARAYA PANTAI TIMOR (PM) S/B-KUALA KRAI', 'PASARAYA PANTAI TIMOR'),
    ('PASARAYA PANTAI TIMOR (PT) SDN BHD', 'PASARAYA PANTAI TIMOR'),
    ('PASARAYA PANTAI TIMOR (PT) SDN BHD - MACHANG', 'PASARAYA PANTAI TIMOR'),
    ('PERNIAGAAN PAK TORI SDN. BHD.', 'PERNIAGAAN PAK TORI SDN. BHD.'),
    ('SALAMKU GROCERY (PC) SDN BHD', 'SALAMKU GROCERY (PC) SDN BHD'),
    ('SALAMKU RETAIL (BM) SDN BHD', 'SALAMKU RETAIL (BM) SDN BHD'),
    ('SALAMKU SUPER MARKET (PP) SDN BHD', 'SALAMKU SUPER MARKET (PP) SDN BHD'),
    ('SALAMKU XTRA (KJ)', 'SALAMKU XTRA'),
    ('SALAMKU XTRA (KOK LANAS ) SDN BHD', 'SALAMKU XTRA'),
    ('SALAMKU XTRA (PALOH) SDN BHD', 'SALAMKU XTRA'),
    ('SOON CHEONG MARINE PRODUCT SDN BHD KLANG', 'SOON CHEONG MARINE PRODUCT'),
    ('SOON CHEONG MARINE PRODUCTS (BSD)', 'SOON CHEONG MARINE PRODUCTS'),
    ('STAR GROCER SDN BHD', 'STAR GROCER SDN BHD'),
    ('STAR GROCER SDN BHD -  BANDAR GAMUDA GARDENS', 'STAR GROCER SDN BHD'),
    ('STAR GROCER SDN BHD -BANDAR TASIK PUTERI', 'STAR GROCER SDN BHD'),
    ('TY PASAR RAYA JIMAT  SDN BHD (PENGKALAN)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('TY PASAR RAYA JIMAT SDN BHD (KUALA KANGSAR 2)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('TY PASAR RAYA JIMAT SDN BHD (KUALA KANGSAR)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('TY PASAR RAYA JIMAT SDN BHD (STATION 18)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('TY PASAR RAYA JIMAT SDN BHD (TAIPING)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('TY PASAR RAYA JIMAT SDN BHD (TELUK INTAN)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('TY PASAR RAYA JIMAT SDN BHD (TMN PERPADUAN)', 'TY PASAR RAYA JIMAT SDN BHD'),
    ('V SEGAR MART  (LAPANGAN JAYA) SDN BHD', 'V SEGAR MART'),
    ('V SEGAR MART (TAPAH) SDN. BHD.', 'V SEGAR MART'),
    ('V SEGAR MART SDN BHD (SUNGAI SIPUT)', 'V SEGAR MART'),
]

# 2. VALIDATION
def validate_mapping(pairs):
    """
    Scan a list of (raw_name, group_name) pairs for raw_names that appear
    more than once mapped to *different* groups. Returns a dict of
    {raw_name: [group1, group2, ...]} for every conflict found.
    Exact duplicate pairs (same name, same group) are not flagged.
    """
    seen = {}
    for raw_name, group_name in pairs:
        seen.setdefault(raw_name, set()).add(group_name)

    conflicts = {name: sorted(groups) for name, groups in seen.items() if len(groups) > 1}
    return conflicts


def build_mapping(pairs=None, on_conflict="warn"):
    """
    Build the final {raw_name: group_name} dict used for df.map().
    on_conflict: 'warn' (print + keep last), 'raise' (stop and raise ValueError),
                 or 'ignore' (silently keep last, old dict-literal behaviour).
    """
    if pairs is None:
        pairs = RAW_NAME_GROUP_PAIRS

    conflicts = validate_mapping(pairs)
    if conflicts and on_conflict != "ignore":
        msg = "Conflicting mapping entries found (same raw name -> different groups):\n" + \
              "\n".join(f"  - {name!r}: {groups}" for name, groups in conflicts.items())
        if on_conflict == "raise":
            raise ValueError(msg)
        else:
            print("WARNING:", msg)

    return dict(pairs)  # dict() over a list keeps the LAST occurrence per key, same as before


# Build once at import time so AutoCleaner.py can just do: from cleaning import NAME_TO_GROUP
NAME_TO_GROUP = build_mapping(RAW_NAME_GROUP_PAIRS, on_conflict="warn")


# 3. NAME CLEANING (basic standardization)
def normalize_whitespace(text) -> str:
    """
    Fix common whitespace issues seen in real store-name data:
      - leading/trailing spaces        '  ABC '        -> 'ABC'
      - double/irregular internal gaps 'ABC   MART'     -> 'ABC MART'
      - space just inside parentheses  '( PENANG )'     -> '(PENANG)'
                                        '(PENANG  )'     -> '(PENANG)'
    Always returns a string (non-string input is stringified first).
    """
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)     # collapse any run of whitespace to one space
    text = re.sub(r"\(\s+", "(", text)   # remove space right after '('
    text = re.sub(r"\s+\)", ")", text)   # remove space right before ')'
    return text


def clean_names(df: pd.DataFrame, name_col: str = "Name") -> pd.DataFrame:
    """
    Basic text standardization on the name column: fix whitespace issues
    (via normalize_whitespace) and uppercase for consistent matching.
    Returns a copy of df — does not mutate the original.
    """
    df = df.copy()
    df[name_col] = df[name_col].apply(normalize_whitespace).str.upper()
    return df

# 3b. ECONSAVE-SPECIFIC NAME CONVERSION (IKA)
def convert_econsave_names(df: pd.DataFrame, name_col: str = "Name") -> pd.DataFrame:
    """
    Detects rows where `name_col` starts with a 5-digit code (e.g.
    '10026 BUTTERWORTH', or messier real-world variants like
    '10026   BUTTERWORTH  ( PENANG )' with double spaces / spaced parens).

    Extracts the code into a new 'EconsaveCode' column and rewrites the
    name as 'ECONSAVE - <branch>', with whitespace normalized on both the
    branch name and any row that doesn't match the pattern.
    Rows that don't start with a 5-digit code are left as-is (just
    whitespace-normalized) with an empty 'EconsaveCode'.
    """
    df = df.copy()
    pattern = re.compile(r"^(\d{5})\s+(.*)$")

    def split_code(name):
        cleaned = normalize_whitespace(name)
        match = pattern.match(cleaned)
        if match:
            code = match.group(1)
            branch = normalize_whitespace(match.group(2))
            return pd.Series([code, f"ECONSAVE - {branch}"])
        return pd.Series(["", cleaned])

    df[["EconsaveCode", name_col]] = df[name_col].apply(split_code)
    return df


# 4. GROUPING
def apply_grouping(
    df: pd.DataFrame,
    name_col: str = "Name",
    group_col: str = "Group",
    mapping: dict = None,
    default: str = "Other",
) -> pd.DataFrame:
    """
    Add a `group_col` to df by mapping df[name_col] through `mapping`.
    Names not found in the mapping fall back to `default` (so they're
    easy to spot and add to the mapping later, instead of vanishing).
    """
    if mapping is None:
        mapping = NAME_TO_GROUP
    df = df.copy()
    df[group_col] = df[name_col].map(mapping).fillna(default)
    return df


def unmatched_names(df: pd.DataFrame, name_col: str = "Name", mapping: dict = None) -> list:
    """
    Return the sorted list of unique names in df that are NOT covered by
    the mapping. Useful for finding new stores that need to be added.
    """
    if mapping is None:
        mapping = NAME_TO_GROUP
    return sorted(set(df[name_col].astype(str)) - set(mapping.keys()))


# 5. WRAPPER — one call to run the whole pipeline
def process(
    df: pd.DataFrame,
    name_col: str = "Name",
    group_col: str = "Group",
    handle_econsave: bool = True,
) -> pd.DataFrame:
    """
    Full pipeline: normalize whitespace, optionally split out Econsave
    branch codes, then group. This is what app.py should call.
    Set handle_econsave=False if this dataset never has Econsave rows.
    """
    df = clean_names(df, name_col=name_col)
    if handle_econsave:
        df = convert_econsave_names(df, name_col=name_col)
    df = apply_grouping(df, name_col=name_col, group_col=group_col)
    return df


if __name__ == "__main__":
    # Quick manual check when running `python cleaning.py` directly
    conflicts = validate_mapping(RAW_NAME_GROUP_PAIRS)
    if conflicts:
        print(f"{len(conflicts)} conflicting name(s) found:")
        for name, groups in conflicts.items():
            print(f"  - {name!r} -> {groups}")
    else:
        print("No conflicts found in mapping.")
    print(f"Total mapped names: {len(NAME_TO_GROUP)}")
