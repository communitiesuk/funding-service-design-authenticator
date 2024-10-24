# Use non-slim image as includes GCC
FROM python:3.10-bullseye

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .
RUN uv sync
COPY . .

EXPOSE 8080

CMD ["uv", "run", "flask", "run", "--host", "0.0.0.0", "--port", "8080"]
