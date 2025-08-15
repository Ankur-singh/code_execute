# --- Build stage ---
FROM python:3.12-slim AS build

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    git \
    gcc \
    g++ \
    make \
    autoconf \
    bison \
    flex \
    libtool \
    pkg-config \
    libprotobuf-dev \
    libnl-route-3-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Build nsjail
RUN git clone --depth=1 https://github.com/google/nsjail /tmp/nsjail \
    && cd /tmp/nsjail \
    && make \
    && cp nsjail /usr/local/bin/ \
    && cd / \
    && rm -rf /tmp/nsjail

# --- Final stage ---
FROM python:3.12-slim

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    libc6 \
    libstdc++6 \
    libprotobuf32 \
    libnl-route-3-200 \
    && rm -rf /var/lib/apt/lists/*

# Copy nsjail from build stage
COPY --from=build /usr/local/bin/nsjail /usr/local/bin/nsjail

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt numpy pandas

COPY src /app/src

RUN useradd -u 9999 -U -m sandboxuser
USER sandboxuser

EXPOSE 8080

CMD ["python", "-m", "src.main"]