FROM python:3.9-slim-bookworm

# Copy UV tool
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
WORKDIR /app
ADD . /app

# Sync the project using the frozen lockfile
RUN uv sync --frozen

# Command to run when container starts
CMD ["uv", "run", "streamlit", "run", "src/main.py"]