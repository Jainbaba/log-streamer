# Set the python version as a build-time argument
# with Python 3.12 as the default
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# Create a virtual environment
RUN python -m venv /opt/venv

# Set the virtual environment as the current location
ENV PATH=/opt/venv/bin:$PATH

# Upgrade pip
RUN pip install --upgrade pip

# Set Python-related environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    redis-server \
    gcc \
    netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Kafka dependencies
RUN apt-get update && apt-get install -y \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Create the mini vm's code directory
RUN mkdir -p /code

# Set the working directory to that same code directory
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt /tmp/requirements.txt

# Set the Env Details
ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}

ARG DJANGO_DEBUG=0
ENV DJANGO_DEBUG=${DJANGO_DEBUG}

ARG DATABASE_URL
ENV DATABASE_URL=${DATABASE_URL}

ARG DJANGO_DEBUG=0
ENV CONN_MAX_AGE=${CONN_MAX_AGE}

# Copy the project code into the container's working directory
COPY ./src /code

# Install the Python project requirements
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN python manage.py collectstatic --noinput

# Set the Django default project name
ARG PROJ_NAME="logger"

# Create a startup script to run all necessary commands
RUN printf "#!/bin/bash\n" > ./start.sh && \
    printf "while ! nc -z kafka 9092; do\n" >> ./start.sh && \
    printf "  sleep 0.1 # wait for Kafka\n" >> ./start.sh && \
    printf "done\n\n" >> ./start.sh && \
    printf "echo 'Kafka is ready!'\n" >> ./start.sh && \
    printf "python manage.py migrate --no-input\n" >> ./start.sh && \
    printf "python manage.py runserver 0.0.0.0:8000\n" >> ./start.sh

# Make the startup script executable
RUN chmod +x start.sh

# Clean up apt cache to reduce image size
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Run the Django project via the startup script when the container starts
CMD ./start.sh