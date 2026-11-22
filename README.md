# ⚡ PartPulse | Automotive Quality Signal Radar

> **Explore recurring customer-reported vehicle concerns using public U.S. NHTSA complaint data to guide automotive quality investigations.**

PartPulse is a presentation-ready, prototype web application designed for automotive quality reviewers, warranty analysts, and reliability engineers. It interfaces directly with the official public National Highway Traffic Safety Administration (NHTSA) API to transform raw federal owner complaints into clear, actionable quality intelligence.

---

## 🚘 Product Highlights

- **Live Public Data Integration**: Queries official federal records via the NHTSA Complaints REST API (`https://api.nhtsa.gov/complaints/complaintsByVehicle`) with real-time caching.
- **Executive Quality Dashboard**: Surfaces total report volume, most-mentioned components, crash/fire indicators, and an explainable **Incident Signal Index**.
- **Interactive Visualizations**:
  - *Complaint Filing Timeline*: Lifecycle area chart mapping filing volume by month.
  - *Ranked Component Frequency*: Horizontal bar chart breaking down atomic component mentions.
- **Deep Evidence Explorer**:
  - Real-time customer narrative keyword search (e.g. "wobble", "stall", "gear").
  - Subsystem component filtering and safety event filtering (Crash, Fire, Injury).
  - Expandable complaint cards featuring verbatim owner quotes, masked VINs, incident dates, and direct links to official NHTSA ODI records.
- **One-Click Case Studies**: High-profile automotive engineering cases pre-configured for instant demoing:
  - `🚙 2019 Jeep Wrangler` — Steering oscillation & damper concerns
  - `🛻 2021 Ford F-150` — Powertrain & 10-speed transmission shifts
  - `🚗 2020 Honda Civic` — Electric power steering sticky feel
  - `⚡ 2022 Tesla Model 3` — Forward collision & phantom braking reports
  - `🚐 2020 Chrysler Pacifica` — Electrical system & engine stall investigations
- **Export Ready**: Instant CSV export of filtered complaint records with sanitized metadata.

---

## 🎨 Design Philosophy

PartPulse adheres to a refined automotive executive aesthetic:
- **Ink Navy & Deep Slate**: `#091726` and `#0F172A` create an authoritative, focused data environment.
- **Restrained Teal Accent**: `#0D9488` highlights data trends, primary components, and positive actions.
- **Attention Amber / Alert Coral**: `#D97706` and `#E11D48` signal safety concerns (crashes, fires, injuries) without alarmism.
- **Warm Light Canvas**: Clean `#F8FAFC` background with elevated white cards (`#FFFFFF`) and crisp typography.

---

## 🛠️ Project Structure

```
partpulse/
├── .streamlit/
│   └── config.toml          # Custom automotive theme & port configuration
├── app.py                   # Streamlit UI & interactive dashboard
├── data_engine.py           # NHTSA API client, schema normalization & metric calculations
├── test_app.py              # Automated unit tests for data engine & edge cases
├── requirements.txt         # Tested production dependencies (Python 3.10 - 3.12)
├── LEARN_THE_APP.md         # Educational guide, architecture diagram & demo script
└── README.md                # Project documentation & deployment guide
```

---

## 🚀 Local Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or **Python 3.12** (recommended).
- *Note on Python 3.15*: Avoid Python 3.15 pre-releases, as data science C-extensions (NumPy, Pandas) lack pre-compiled PyPI wheels for that version.

### 1. Clone or Open the Repository
```bash
cd C:\Users\LENOVO\.gemini\antigravity\scratch\partpulse
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py --server.port 8502
```
Open **`http://localhost:8502`** in your web browser.

---

## 🧪 Running Unit Tests

To verify the data normalization logic, type conversions, and component extraction:

```bash
python test_app.py
```

Expected output:
```
✓ safe_helpers passed
✓ normalization & component extraction passed
✓ empty dataset handling passed

ALL DATA ENGINE TESTS PASSED!
```

---

## ☁️ Public Deployment Instructions

PartPulse is 100% cloud-ready with zero external database dependencies.

### Deploying to Streamlit Community Cloud (Free)
1. Push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io).
3. Click **New app**.
4. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
5. Click **Deploy!**



---

## 📖 Methodology, Data Sources & Limitations

1. **Owner-Submitted Filings**: Reports in the NHTSA Office of Defects Investigation (ODI) database are submitted by owners, drivers, and fleet operators. They are exploratory signals for review, **not** confirmed engineering defects or recall orders.
2. **Missing Population Denominator**: Complaint counts must not be confused with failure rates. A mass-market vehicle with 500 complaints across 1,000,000 sales has a significantly lower true incident rate than a low-volume niche car with 100 complaints across 5,000 sales. Public NHTSA data does not include vehicle registration or mileage exposure denominators.
3. **Transparent Metric Formulation**: The **Incident Signal Index** measures:
   $$\text{Incident Signal Index} = \left(\frac{\text{Complaints Flagging Crash, Fire, or Injury}}{\text{Total Complaints}}\right) \times 100$$
   This indicates the concentration of acute safety events within the complaint sample—not across the entire vehicle fleet.
4. **Official Data Source**: All complaint records originate from the U.S. Department of Transportation / NHTSA Complaints API. View federal records at [NHTSA Recalls & Complaints Search](https://www.nhtsa.gov/recalls).

---

## 📄 License & Disclaimer

PartPulse is an independent student prototype developed for educational and portfolio demonstration purposes. It is not affiliated with, sponsored by, or endorsed by Stellantis, Ford, Tesla, Honda, or the U.S. National Highway Traffic Safety Administration (NHTSA).
