# QuantPair-AI
 
Pair trading strategy on S&P 500 technology stocks using 8 years of market data (2018–2025). Identifies cointegrated pairs, backtests a mean-reversion trading strategy, trains an ML classifier on the strategy's features, and serves the results through a FastAPI dashboard. Built as a modular monolith of pure, reusable operators following the HtDP design methodology.
 
## Results at a glance
 
| Phase | Finding |
|---|---|
| Cointegration screen | 1 of 23 pairs passed both gates: **QCOM/AMD** (p = 0.043, half-life ~64d, beta = 0.71). Provisional, and the margin is borderline |
| Strategy backtest | The Altucher unilateral system **loses systematically** (−72.5%, Sharpe −0.26): directional shorts against AMD's uptrend, no stop-loss, and a vol-blind entry filter. A negative result with identifiable causes |
| ML classifier | The ensemble ties the one-rule baseline (65.7% vs 66.9%): the features carry no information beyond \|z\|, so the model rediscovered the classical threshold rule |
| Sentiment | VADER over Google News, display-only by module contract. It never gates trading |
 
Honest negative findings are reported as findings. The pipeline is the deliverable; the strategy's P&L is the experiment's output, not its goal.
 
## Architecture
 
```
src/quantpairs/reusableModule/   pure operator libraries (data in -> data out, no I/O)
├── eda/                         returns, volatility, correlations, beta
├── cointegration/               Engle-Granger, hedge ratio, spread, half-life
├── strategy/                    Altucher unilateral system, steps 1-8
├── features/                    SHARED feature engineering (training + live inference)
└── sentiment/                   VADER scoring, display-only (imported by nothing else)
 
code/                            orchestration scripts (I/O, composition, CSV outputs)
├── data/dataAPI.py              yfinance pull -> master_data.csv
└── features/                    data_analysis, cointegration, trading_strategy,
                                 train_model, sentiment_analysis, full_universe
 
api/main.py                      read-only FastAPI dashboard over the CSV outputs
*_output/                        committed results per phase (tables, model.pkl)
```
 
Operators never do I/O or plotting. Orchestration scripts compose them and write CSVs. The `features/` module is the single source of truth for feature engineering across training and any future live inference (LEAN).
 
## Quickstart
 
```bash
pdm install
pdm run code/data/dataAPI.py                      # pull data, build master
pdm run code/features/data_analysis.py            # Phase 2 EDA
pdm run code/features/cointergration-analysis.py  # Phase 3 screen
pdm run code/features/trading_strategy.py         # Phase 4 backtest
pdm run code/features/train_model.py              # Phase 5 classifier
pdm run code/features/sentiment_analysis.py       # sentiment (display-only)
```
 
### Dashboard
 
```bash
pdm add fastapi uvicorn
pdm run uvicorn api.main:app --reload
# http://127.0.0.1:8000/dashboard   (JSON endpoints listed at /)
```
 
### Docker
 
```bash
docker build -t quantpairs .
docker run -p 8000:8000 quantpairs
```
 
## Development approach
 
Built on a fixed 9-ticker harness (MSFT, AAPL, NVDA, AVGO, ORCL, CRM, ADBE, AMD, QCOM plus ^GSPC/^VIX benchmarks) to keep complexity down during development. The pipeline is universe-agnostic: the stock list lives only in configuration, and `code/features/full_universe.py` reruns the same screen on the full S&P 500 IT sector, with the Bonferroni/FDR correction the wider universe makes mandatory.
 
## Known limitations and future work
 
- Beta and spread statistics were fit on the full 8-year window. Refitting on 2018–2023 only is the outstanding robustness check on the locked pair.
- The Altucher system has no stop-loss or time exit, which matches the source. Any live use would need one.
- A second version of the classifier (binary labels, context features that add information beyond \|z\|) is scoped but deferred.
- LEAN engine integration for paper trading through IBKR is the designed stretch goal.
- Code quality: ruff linting, a logging system to replace prints, and removing the remaining hardcoded paths in the analysis scripts.
## References
 
- Altucher, *Trade Like a Hedge Fund* (2004): the unilateral pairs system
- Felleisen et al., *How to Design Programs*, 2nd ed.: the operator design methodology
