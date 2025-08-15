FROM python:3.12-slim

# Install run-time dependencies in base image
RUN apt-get -y update && apt-get install -y \
    libc6 \
    libstdc++6 \
    libprotobuf32 \
    libnl-route-3-200 \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libtool \
    make \
    pkg-config \
    protobuf-compiler

# Build and install nsjail
RUN git clone https://github.com/google/nsjail  \
    && cd nsjail \
    && make \
    && cp nsjail /usr/local/bin/ \
    && cd / \
    && rm -rf nsjail

# Create chroot environment with debootstrap
RUN pip install pandas numpy

# Install Python dependencies for the Flask app
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY app /app/app

# Create non-privileged user
RUN useradd -u 9999 -U -m sandboxuser

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "-m", "app.main"]