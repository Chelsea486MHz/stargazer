#
# Python deps image
#
FROM python:3.11 AS image-build

RUN apt update
RUN apt install -y --no-install-recommends \
    build-essential \
    gcc
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Download the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#
# Production image
#
FROM python:3.11

# App settings
ENV DEBUG False
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install dependencies from the build image venv
COPY --from=image-build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install the app
COPY app.py .
COPY gunicorn_config.py .

# App information
ENV STARGAZER_VERSION=0.0.1
ENV STARGAZER_TYPE=manager

# Run the app
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]