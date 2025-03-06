# Pull the base python image + uv | Note: this repository needs python 3.9
FROM python:3.9-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Set the working directory
WORKDIR /app
