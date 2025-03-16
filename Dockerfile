FROM alpine:latest

# Install necessary dependencies: Git, Curl, CMake, and build tools
RUN apk add --no-cache git curl cmake make gcc g++ python3-dev musl-dev

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY . /mevy-bot/

WORKDIR /mevy-bot

# Install project
RUN uv sync --frozen

WORKDIR /mevy-bot/mevy_bot/rest_api/

RUN ["uv", "run", "fastapi", "run", "main.py"]

