## Changelog

## Major TODO
### Add
 - A logging system / replace print statements where not needed
 - A ruff linter
### Change
 - Refactor code to linter standard
 - Remove Hardcoded paths 

### v0.9.0 — 02.08.2026
- Added sentiment.py (reusable sentiment library) -> src/quantpairs/reusableModule/sentiment/
  - Pure operators: score_headline, score_headlines, sentiment_label, summarise_ticker
  - VADER compound scores; conventional thresholds (+-0.05)
  - Display-only: never imported by features/, model/, strategy/, or lean_app/ (stated in module docstring)
- Added sentiment_analysis.py (orchestration) -> code/features/
  - Google News RSS per ticker (free, no key, stdlib fetch); satisfies brief's X-or-Google-News requirement
  - Outputs: sentiment.csv (per-ticker summary) + headlines_scored.csv (audit trail) -> sentiment_output/
  - First run: 9/9 tickers, 20 headlines each; QCOM only negative (leg of locked pair -> dashboard talking point)
- Added vaderSentiment dependency to pdm
- # TODO - FastAPI dashboard: read-only endpoints over cointegration/strategy/model/sentiment outputs
- # TODO - Docker containerization: streamline the build (one image, reproducible env; also the Cloud Run deploy unit)

### v0.8.0 — 02.08.2026
- Added build_features.py (shared feature library) -> src/quantpairs/reusableModule/features/
  - build_features: 6 features computable at close t (z, z_change_1d, z_change_5d, p1_change, vol_p1, vol_p2)
  - build_labels: Option A target - |z| shrinks (revert) / grows (diverge) / flat over k=5d, dead zone 0.25
  - Contract: build_features runs in training AND LEAN; build_labels training-only (looks ahead)
- Added train_model.py (training script) -> code/features/
  - Train 2018-2023 (1,460 rows) / test 2024-2025 (495 rows), k-day purge at boundary
  - Baselines: always-revert 41.2%; one-rule (|z| > 1) 66.9%
  - Models: logistic 40.0%; forest / gboost / ensemble 65.7% -> model.pkl
- Finding: model ties the one-rule baseline - features carry no information beyond |z|;
  classifier rediscovered the classical threshold rule (rules-as-features validated, ceiling exposed)
- # TODO - v2: binary labels (drop flat, f1 0.05); context features orthogonal to |z|
  (rolling correlation, VIX, rolling half-life) - deferred, vertical slice first

### v0.7.0 — 02.08.2026
- Ran trading_strategy.py backtest on locked pair (P1=AMD by volatility, P2=QCOM)
  - diff ADF p = 0.0000, half-life 8.7d -> signal construction sound
  - Full: -72.5% cumulative, Sharpe -0.26, max drawdown -81.6%, 112 trades, 39% days in market
  - Loses in both sub-periods -> systematic, not regime luck
- Diagnosis (negative result, mechanistic causes)
  - Unilateral shorts against AMD's 8-year uptrend + no stop-loss -> -81% drawdown
  - 2% move filter calibrated to QQQ (~1% vol); ~0.6 sigma on AMD -> vol-blind, fires routinely
- Note: train/test labels renamed sub-period analysis - strategy fits no parameters, nothing is trained
- # TODO - split P&L by position side (confirm shorts drive the loss)
- # TODO - vol-scaled entry filter (tuning -> would reintroduce a real train boundary)

### v0.6.0 — 02.08.2026
- Added strategy.py (reusable strategy library) -> src/quantpairs/reusableModule/strategy/
  - Pure operators, steps 1-8 of the Altucher system: price_ratio, moving_average, ratio_difference,
    rolling_zscore, daily_change, generate_positions, strategy_returns
  - Aggregates: sharpe_ratio, max_drawdown, trade_count
  - generate_positions = the one stateful fold (flat | long | short), still pure (Series in -> Series out)
- Added trading_strategy.py (Phase 4 script) -> code/features/
  - Composes strategy.py; reuses eda (select_columns, volatility, cumulative_returns)
    + cointegration (adf_pvalue, half_life as sanity checks)
  - assign_legs: P1 = more volatile leg via eda.volatility (not hardcoded)
  - Position at close t earns return t+1 (no same-day lookahead)
  - Outputs: signals.csv + performance.csv -> strategy_output/
- Notes
  - Rolling z-score = no fitted params; did NOT reuse cointegration.zscore (full-sample = lookahead)
  - Imports reference existing filename cointergration (typo) -> update after git mv
- # TODO - verify step 5 ("prior 20 days"): rolling(20) incl. today vs shift(1) variant
- # TODO - stop-loss / time exit (brief requires it)
- # TODO - rename cointergration.py -> cointegration.py; underscore cointergration-analysis.py
                                    
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
