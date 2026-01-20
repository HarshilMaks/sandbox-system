FROM sandbox-base:latest

# Browser sandbox environment
RUN apt-get update && apt-get install -y \
    chromium-browser \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /sandbox
