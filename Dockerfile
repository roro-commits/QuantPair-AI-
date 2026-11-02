# QuantPairs dashboard — API layer only.
# The API reads committed CSVs; it imports nothing from quantpairs,
# so we skip the project install and its pyproject pins entirely.
FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pandas

COPY api/ api/
COPY cointegration_output/ cointegration_output/
COPY strategy_output/ strategy_output/
COPY model_output/ model_output/
COPY sentiment_output/ sentiment_output/

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
