## Changelog

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
  - # TODO - split data & ml fucntionaity
  - # TODO - abstract the model fit fucntions 
