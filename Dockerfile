# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.9.6
FROM python:${PYTHON_VERSION}-slim as base

# Switch to root to install and configure cron
USER root

# Install cron
RUN apt-get update && apt-get install -y cron

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Copy the source code
COPY . .

# Create and set up cron job
RUN echo "0 15 * * 1-5 /usr/bin/python3 /app/monitor_file.py >> /var/log/cron.log 2>&1" > /etc/cron.d/monitor_job \
    && chmod 0644 /etc/cron.d/monitor_job \
    && crontab /etc/cron.d/monitor_job

# Ensure cron directories have the correct permissions
RUN mkdir -p /var/run && chmod 0755 /var/run \
    && mkdir -p /var/run/crond && chmod 0755 /var/run/crond

# Switch back to the non-privileged user
USER appuser

# Start cron and your application
CMD service cron start && python3 /app/monitor_file.py

# Expose port
EXPOSE 5243
