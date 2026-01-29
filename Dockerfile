FROM ghcr.io/astral-sh/uv:debian-slim

RUN mkdir webhook
WORKDIR /webhook

COPY . .

ENTRYPOINT ["uv", "run", "webhook.py"]