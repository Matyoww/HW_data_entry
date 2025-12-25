import streamlit as st
import pandas as pd
from pathlib import Path

# Configure page
st.set_page_config(page_title="HW Catalog Entry", page_icon="🧰", layout="centered")
st.title("HW Catalog Entry")
st.caption("Need additional details? See the Hot Wheels wiki: [Hot Wheels](https://hotwheels.fandom.com/wiki/Hot_Wheels)")

# File setup
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
CSV_FILE = DATA_DIR / "hw_catalog.csv"

COLUMNS = [
    "Toy #",
    "Collector #",
    "Name",
    "Series",
    "Series #",
    "Year",
    "Rarity",
    "Exclusive Description",
    "Color",
    "Tampo",
    "Base Color",
    "Window Color",
    "Interior Color",
    "Wheel Type",
]

def load_catalog() -> pd.DataFrame:
    if CSV_FILE.exists():
        try:
            df = pd.read_csv(CSV_FILE, dtype=str).fillna("")
            # Ensure columns exist even if CSV was created externally
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS]
        except Exception:
            # Fallback to empty DataFrame if file is corrupted
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def save_row(row: dict):
    df = load_catalog()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def duplicate_exists(df: pd.DataFrame, toy_no: str, name: str, series: str, rarity: str, year: str) -> bool:
    if df.empty:
        return False
    t = str(toy_no).strip().lower()
    n = str(name).strip().lower()
    s = str(series).strip().lower()
    r = str(rarity).strip().lower()
    y = str(year).strip().lower()
    try:
        mask = (
            df["Toy #"].astype(str).str.strip().str.lower() == t
        ) & (
            df["Name"].astype(str).str.strip().str.lower() == n
        ) & (
            df["Series"].astype(str).str.strip().str.lower() == s
        ) & (
            df["Rarity"].astype(str).str.strip().str.lower() == r
        ) & (
            df["Year"].astype(str).str.strip().str.lower() == y
        )
        return bool(mask.any())
    except Exception:
        return False

rarity_options = [
    "TH",
    "STH",
    "Normal",
    "New Model",
    "New for Year",
    "New in Mainline",
    "Exclusive",
]

# Entry form
with st.form("catalog_entry"):
    st.caption("Fields marked * are required")

    with st.expander("Required Fields", expanded=True):
        toy_no = st.text_input("Toy # *", key="toy_no")
        name = st.text_input("Name *", key="name")
        series = st.text_input("Series *", key="series")
        rarity = st.selectbox("Rarity *", options=rarity_options, index=2, key="rarity")

    with st.expander("Optional Fields", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            collector_no = st.text_input("Collector #", key="collector_no")
            series_no = st.text_input("Series #", key="series_no")
            year = st.text_input("Year", key="year")
            color = st.text_input("Color", key="color")
        with col2:
            tampo = st.text_input("Tampo", key="tampo")
            base_color = st.text_input("Base Color", key="base_color")
            window_color = st.text_input("Window Color", key="window_color")
            interior_color = st.text_input("Interior Color", key="interior_color")
            wheel_type = st.text_input("Wheel Type", key="wheel_type")

    exclusive_desc = st.text_input("Exclusive Description", help="Only for 'Exclusive' rarity", key="exclusive_desc")

    submitted = st.form_submit_button("Save")

if submitted:
    # Basic validation
    required = {
        "Toy #": toy_no.strip(),
        "Name": name.strip(),
        "Series": series.strip(),
        "Rarity": rarity.strip(),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        st.error(f"Missing required fields: {', '.join(missing)}")
    elif rarity == "Exclusive" and not exclusive_desc.strip():
        st.error("Exclusive Description is required when Rarity is 'Exclusive'.")
    else:
        catalog = load_catalog()
        if duplicate_exists(catalog, toy_no, name, series, rarity, year):
            st.warning("This entry already exists based on Toy #, Name, Series, Rarity, and Year. No new row added.")
        else:
            row = {
                "Toy #": toy_no.strip(),
                "Collector #": collector_no.strip(),
                "Name": name.strip(),
                "Series": series.strip(),
                "Series #": series_no.strip(),
                "Year": year.strip(),
                "Rarity": rarity.strip(),
                "Exclusive Description": exclusive_desc.strip(),
                "Color": color.strip(),
                "Tampo": tampo.strip(),
                "Base Color": base_color.strip(),
                "Window Color": window_color.strip(),
                "Interior Color": interior_color.strip(),
                "Wheel Type": wheel_type.strip(),
            }
            try:
                save_row(row)
                st.success("Entry saved to CSV.")
                # Clear all inputs and reset defaults
                for k in [
                    "toy_no",
                    "collector_no",
                    "name",
                    "series",
                    "series_no",
                    "year",
                    "color",
                    "tampo",
                    "base_color",
                    "window_color",
                    "interior_color",
                    "wheel_type",
                    "exclusive_desc",
                ]:
                    st.session_state[k] = ""
                # Reset rarity to default (Normal)
                st.session_state["rarity"] = "Normal"
                # Rerun to reflect cleared state
                try:
                    st.rerun()
                except Exception:
                    st.experimental_rerun()
            except Exception as e:
                st.error(f"Failed to save entry: {e}")

# Show existing catalog
st.subheader("Current Catalog")
catalog_df = load_catalog()
if catalog_df.empty:
    st.info("No entries yet.")
else:
    total = len(catalog_df)
    latest = catalog_df.tail(10).iloc[::-1]
    st.caption(f"Showing latest {len(latest)} of {total} entries")
    st.dataframe(latest, width='stretch')