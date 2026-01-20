FROM ubuntu:22.04

# Base sandbox image
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /sandbox
