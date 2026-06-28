## Changelog

### v0.3.0 — 28.06.2026
- Added eda.py (reusable analysis library)
  - Pure operators: select, mean returns, volatility, correlation, rank pairs, beta, rolling correlation
  - Operator-classified, data in → data out (no plots, no I/O)
- Added data_analysis.py (Phase 2 EDA script)
  - Composes eda.py; loads master_data.csv
  - Summary table + correlation-ranked pair shortlist → CSV
  - Plots: heatmap, cumulative growth, volatility bar, beta bar, scatter, rolling correlation
  - Saves to eda_output/
- Fixed
  - strip_prefix renamed index instead of columns
  - Date-is-index gotcha in add_calendar
- # TODO - Engle–Granger cointegration on pair_shortlist (Phase 3)
- # TODO - lock final pairs from cointegration, not correlation

### v0.2.0 - 28.06.2026
- Added to dataAPI.py
  - Calculate return data - feature engineering
  - Add s&p 5000 daily return
  - Extract, calculated & aggregate master data features
  - Added data_files folder 
- Changed
 - Moved source codes into code folder - separated from src (re-usable library)
 - Separated the data downloaded into data_files instead of code/data folder

### v0.1.0 — 21.06.2026
- Added dataAPI.py
  - function to download stock data for the last 8 years
  - extracting the close data
  - Added PDM as package manager
- Added a re-usable data & ml module
  - various functionality
  - # TODO - split data & ml functionality
  - # TODO - abstract the model fit functions 
