FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Deno for YouTube JS signature extraction
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="${DENO_INSTALL}/bin:${PATH}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp nightly
RUN pip install --no-cache-dir --pre "yt-dlp[default]"

COPY api/ ./api/
COPY frontend/ ./frontend/
COPY streamlit_app.py .

# Create volume mount points
RUN mkdir -p /downloads /cookies /data

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
