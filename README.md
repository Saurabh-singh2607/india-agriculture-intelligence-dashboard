# India Agriculture & Crop Price Dashboard

An interactive Streamlit dashboard built from the two supplied CSV datasets.

## Features
- Year-range, state, season and crop filters
- KPI cards for total production, cultivated area, crop count and state/UT count
- Annual production trend
- Top crops and top states by production
- Seasonal production distribution
- Searchable crop-price table
- Modal price vs MSP comparison and price-range chart

## Run locally
1. Install Python 3.9 or newer.
2. Keep `app.py`, `crop_production.csv`, and `india-crop-prices.csv` in the same folder.
3. Open a terminal in that folder and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens in your browser.

## Data note
The production dataset and price dataset have different schemas, so they are presented in separate dashboard sections. Production units are preserved as supplied by the source file. Crop prices are in rupees per quintal.
