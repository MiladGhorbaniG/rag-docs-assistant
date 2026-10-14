FROM python:3.12-slim

WORKDIR /app

COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install --no-cache-dir .

COPY sample_data ./sample_data

ENV SAMPLE_DATA_DIR=/app/sample_data
ENV LLM_PROVIDER=mock
ENV EMBEDDING_DIM=64

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
