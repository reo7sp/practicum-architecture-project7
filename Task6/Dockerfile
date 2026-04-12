FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python3 -m venv /app/.venv
COPY Task3/requirements.txt /app/requirements.txt
RUN /app/.venv/bin/pip install --no-cache-dir -r /app/requirements.txt
RUN /app/.venv/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('sentence-transformers/all-MiniLM-L6-v2', resume_download=True)"
COPY Task3/build_index.py /app/build_index.py
COPY Task6/update.sh /app/update.sh
COPY Task6/init-cron.sh /app/init-cron.sh

CMD ["/app/init-cron.sh"]
