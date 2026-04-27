# 🏢 Real Estate CRM Intelligence Dashboard

A professional Streamlit dashboard for Real Estate client analytics.

---

## 📁 Project Structure

```
real_estate_dashboard/
├── app.py              ← Main dashboard (this is what Streamlit runs)
├── data.csv            ← Your cleaned data file
├── requirements.txt    ← Python packages needed
└── README.md           ← This guide
```

---

## 🚀 Step-by-Step: Run Locally First

### Step 1 — Install Python
- Download Python 3.10 or newer from https://www.python.org/downloads/
- During install on Windows, tick **"Add Python to PATH"**
- Verify: open Terminal / Command Prompt and run: `python --version`

### Step 2 — Create a project folder
```bash
mkdir real_estate_dashboard
cd real_estate_dashboard
```
Copy `app.py`, `data.csv`, and `requirements.txt` into this folder.

### Step 3 — Create a virtual environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Run the dashboard locally
```bash
streamlit run app.py
```
Your browser will open automatically at **http://localhost:8501** 🎉

---

## ☁️ Deploy to Streamlit Cloud (Free & Public URL)

### Step 1 — Create a GitHub account
Go to https://github.com and sign up (free).

### Step 2 — Create a new repository
1. Click the **+** icon → **New repository**
2. Name it: `real-estate-dashboard`
3. Set to **Public**
4. Click **Create repository**

### Step 3 — Upload your files
In the new repo, click **"uploading an existing file"** and upload:
- `app.py`
- `data.csv`
- `requirements.txt`

Commit the files.

### Step 4 — Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **"New app"**
4. Choose your repository `real-estate-dashboard`
5. Set **Main file path** to `app.py`
6. Click **Deploy!**

Within 2–3 minutes you'll get a free public URL like:
`https://yourname-real-estate-dashboard-app-xxxx.streamlit.app`

---

## 📊 Dashboard Features

| Tab | What it shows |
|-----|---------------|
| Overview | Client type, referral channels, satisfaction & engagement distributions |
| Client Segments | Revenue by segment, satisfaction vs engagement bubble chart, gender split |
| Sales & Pricing | Price distribution, floor area scatter, country revenue, loan analysis |
| Investment Analysis | Investment profile breakdown, cluster analysis, score deep dives |
| Geographic | Country/region revenue, treemap, satisfaction vs price scatter |

### Sidebar Filters (apply to all tabs)
- Country
- Client Segment
- Investment Profile
- Referral Channel
- Acquisition Purpose
- Sale Price Range

---

## 🧹 Data Quality Checks Applied

| Check | Status |
|-------|--------|
| Missing values | ✅ None found |
| String whitespace | ✅ Stripped |
| Country name casing | ✅ Standardised to Title Case |
| satisfaction_score range | ✅ Clipped to [1, 5] |
| engagement_score range | ✅ Clipped to [0, 100] |
| investment_score range | ✅ Clipped to [0, 1] |
| Negative prices/areas | ✅ Clipped to 0 |
| Duplicate client IDs | ✅ All 2000 are unique |

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Port already in use | Run `streamlit run app.py --server.port 8502` |
| Data not loading | Make sure `data.csv` is in the **same folder** as `app.py` |
| Slow loading | Normal on first run; caching kicks in after that |
