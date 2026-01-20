FROM sandbox-base:latest

# Python sandbox environment
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /sandbox
