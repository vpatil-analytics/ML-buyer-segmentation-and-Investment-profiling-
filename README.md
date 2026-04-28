# 🏢 Real Estate CRM Dashboard

A Streamlit-based analytics dashboard for:
- Buyer segmentation
- Investment profiling
- Sales analysis
- Geographic insights

## 🚀 Live App
[Click here to view dashboard](https://analytics-real-estate.streamlit.app/)

## 📊 Tech Stack
- Streamlit
- Pandas
- Plotly

## 📂 How to run locally
pip install -r requirements.txt
streamlit run app.py

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| Port already in use | Run `streamlit run app.py --server.port 8502` |
| Data not loading | Make sure `data.csv` is in the **same folder** as `app.py` |
| Slow loading | Normal on first run; caching kicks in after that |
