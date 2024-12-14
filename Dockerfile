# build the container: docker build . -t iiif -f Dockerfile.in_development
# run the container: docker run -it iiif

# Use an official Python runtime as the base image
FROM public.ecr.aws/docker/library/python:3.8.20

# Set environment variables to avoid interactive prompts during package installation
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_WORK=/home/wsgi
ENV APP_CURRENT=/app

# Set the working directory in the container
WORKDIR /app

# Update the package manager and install necessary development libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    bash \
    libjpeg-dev \
    libfreetype6-dev \
    zlib1g-dev \
    liblcms2-dev \
    # lcms2-utils \
    libtiff-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p \
    $APP_WORK/tmp \
    $APP_WORK/log \
    $APP_WORK/cache \
    $APP_WORK/cache-loris2 \
    $APP_WORK/cache-links && \
    chown -R root:root $APP_WORK

# Copy application code into the container (if applicable)
COPY . /app/

# Create a virtual environment, activate it, and install dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Set up crontab
COPY ./crontab /etc/cron.d/app-cron
RUN chmod 0644 /etc/cron.d/app-cron && \
    crontab /etc/cron.d/app-cron

# Ensure the script is executable
RUN chmod +x beanstalk_cache_clean.sh

# Specify the default command to run in the container
# CMD ["/bin/bash"]
CMD ["/bin/bash", "-c", "cron && gunicorn --bind 0.0.0.0:8000 --workers 3 loris2:application"]
