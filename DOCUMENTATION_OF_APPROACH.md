# PartPulse: Quality Signal Radar
## Documentation of Technical Approach & Implementation Architecture

---

### Meta Information
- **Project Name:** PartPulse Automotive Quality Intelligence
- **Candidate / Author:** KRRISHNATH
- **GitHub Repository:** [https://github.com/KRRISHNATH/partpulse-quality-signals](https://github.com/KRRISHNATH/partpulse-quality-signals)
- **Live MVP Application:** [https://partpulse-quality-signals-sf2rmaeynm5hdoow8wq4ht.streamlit.app](https://partpulse-quality-signals-sf2rmaeynm5hdoow8wq4ht.streamlit.app)
- **Primary Data Source:** Official U.S. National Highway Traffic Safety Administration (NHTSA) Complaints REST API

---

### 1. Problem Statement & Operational Objective
Automotive original equipment manufacturers (OEMs), reliability engineers, and warranty review teams monitor field quality signals to catch safety-critical component anomalies before they escalate into mandatory recalls or fleet-wide failures. The U.S. National Highway Traffic Safety Administration (NHTSA) hosts tens of thousands of owner-submitted vehicle complaints, yet this data is fundamentally messy, unstructured, and difficult for engineers to triage rapidly. Existing federal search portals require manual, one-off lookups and lack aggregated subsystem analytics.

**Core Objective:** Build *PartPulse* as a responsive, presentation-ready quality intelligence radar that connects to live federal databases, normalizes owner complaint filings, surfaces frequency patterns and acute safety signals (crashes, fires, injuries), and provides granular evidence drill-downs for engineering investigation.

---

### 2. Data Architecture & Federal API Integration
PartPulse utilizes a decoupled two-tier architecture: a backend data engine (`data_engine.py`) and a reactive presentation layer (`app.py`). This separation of concerns guarantees clean testing and modularity.

#### Key Data Engineering Highlights:
1. **Live Federal Querying & Caching:** Calls NHTSA's `complaintsByVehicle` REST API with vehicle Make, Model, and Year. Requests are wrapped in Streamlit's `@st.cache_data(ttl=3600)` with network retry handling, preventing redundant queries and federal server throttling.
2. **NHTSA Edge-Case Handling:** When zero complaints match a vehicle, NHTSA's API returns HTTP 400 with a payload of `{'count': 0, 'results': []}` instead of HTTP 200. The data engine intercepts this specific status and translates it into an empty dataset rather than raising an unhandled exception.
3. **Schema Normalization & Defensive Parsing:** Handles schema drift, null dates, masked VINs, and disparate boolean representations (e.g., parsing `True`, `'yes'`, `1`, and `'true'` for crash and fire flags into strict boolean types).
4. **Atomic Component Splitting:** NHTSA complaints frequently group interacting assemblies into single compound strings (e.g. *'STEERING, SUSPENSION'*). PartPulse decomposes these multi-part strings into distinct atomic units so part rankings accurately reflect true mechanical subsystems.

---

### 3. Analytical Methodology & Explainable Metrics
In safety-critical automotive engineering, opacity is dangerous. PartPulse deliberately avoids uninterpretable "black box" models in favor of transparent, auditable mathematical metrics:

- **Incident Signal Index (ISI):** Defined as `(Reports with Crash, Fire, or Injury / Total Reports) × 100`. This quantifies the concentration of acute safety events within the complaint sample.
- **The Missing Population Denominator Caveat:** The system explicitly warns reviewers that raw complaint counts are *not* mechanical failure rates. Public NHTSA records lack sales volumes and fleet mileage exposure. 300 complaints on a truck with 800,000 units sold represents a drastically lower true failure rate than 80 complaints on a specialty vehicle with 5,000 units sold.
- **Triangulation Role:** PartPulse positions public complaint data as an early detection radar to be cross-referenced with internal warranty claims (R/1000), dealer Technical Service Bulletins (TSBs), and physical teardown metallurgy.

---

### 4. Role of Artificial Intelligence (Minimal & Moderate Usage)
In alignment with rigorous software engineering best practices, artificial intelligence was utilized in a **moderate, targeted engineering capacity** rather than being blindly embedded into the core logic:

- **Used for Engineering Acceleration:** AI assistance was leveraged as a technical pair programmer to scaffold boilerplate data schemas, accelerate CSS layout styling, formulate regex patterns for multi-component parsing, and assist in unit test coverage design.
- **Deliberately Omitted from Diagnostics:** Generative AI was *not* used to diagnose mechanical defects or summarize customer narratives. LLMs can hallucinate causes, invent non-existent recalls, or misinterpret technical fault codes. In automotive quality compliance, verbatim consumer quotes and transparent statistical aggregations are strictly required.

---

### 5. Verification, Testing & Deployment
The project was verified through a structured engineering pipeline:

- **Automated Test Suite (`test_app.py`):** Unit tests cover safe type coercions, empty dataset responses, atomic component parsing, and safety index arithmetic.
- **Environmental Compatibility:** Diagnosed and resolved Python 3.15 C-extension compilation errors by pinning dependencies to stable Python 3.12 (supported by NumPy and Pandas binary wheels).
- **Cloud CI/CD Deployment:** Successfully deployed to Streamlit Community Cloud with GitHub integration. Resolved internal container port binding to ensure automated health checks pass reliably on standard port 8501.
