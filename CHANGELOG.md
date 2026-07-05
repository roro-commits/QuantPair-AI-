## Changelog

## Major TODO
- Add
 - A logging system / replace print statements where not needed
 - A ruff linter
- Change
 - Refactor code to linter standard
                                    
### v0.5.0 — 05.07.2026

- Added unilateral_pairs_trading_system.md (strategy spec)
    - Abstracted from Trade Like a Hedge Fund (Altucher, 2004)
    - 8 rules: P1/P2 ratio -> MA20 -> diff -> z-score -> entry (|z| > 1.5 + 2% P1 move) -> exit (|z| < 0.5)
    - Notation generalised to P1/P2 (QQQ/SPY as concrete instance)
- Added unilateral_pairs_flowchart.svg (black & white, code-ready)
    - Compute chain + position-state branch (entry if/elif/else vs exit if/elif/else)
    - Embedded in the md via relative image link

- ### TODO - implementation of the system

### v0.4.0 — 29.06.2026
- Added cointegration.py (reusable analysis library)
  - Pure operators: adf_pvalue, coint_pvalue, hedge_ratio, compute_spread, zscore, half_life
  - Engle-Granger via statsmodels; data in -> data out (no plots, no I/O)
- Added cointegration_analysis.py (Phase 3 script)
  - Composes cointegration.py; loads master + pair_shortlist
  - Tests pairs both directions, keeps lower p-value + winning direction
  - Two gates: p < 0.05 and half-life <= 126d
  - Results table + locked pairs -> CSV (cointegration_output/)
  - TOP_N knob to scale top-N -> all pairs
  - Locked pair (full-window screen, provisional): QCOM/AMD
- Added statsmodels dependency to pdm
- Fixed
  - Benchmarks (GSPC/VIX) leaking into pair universe -> filtered in main
  - test_pair / main tangle - moved loop + I/O back to main
- ### TODO - refit beta + spread stats on train window only (avoid lookahead)
- ### TODO - z-score entry/exit signals -> ML classifier features

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
  - ### TODO - split data & ml functionality
  - ### TODO - abstract the model fit functions 
