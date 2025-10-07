# -------- Whisper.cpp build stage --------
FROM debian:stable-slim AS whisper_builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
RUN git clone https://github.com/ggerganov/whisper.cpp.git
WORKDIR /opt/whisper.cpp
RUN make -j$(nproc)

# -------- Piper build stage --------
FROM debian:stable-slim AS piper_builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git pkg-config libssl-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
# Install Rust (non-interactive)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN git clone https://github.com/rhasspy/piper.git
WORKDIR /opt/piper
RUN cargo build --release

# -------- Final runtime image --------
FROM python:3.11-slim
WORKDIR /app

# System deps for FAISS and audio libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy executables from builders
COPY --from=whisper_builder /opt/whisper.cpp/main /usr/local/bin/whisper
COPY --from=piper_builder /opt/piper/target/release/piper /usr/local/bin/piper

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
