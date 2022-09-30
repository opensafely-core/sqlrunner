# syntax=docker/dockerfile:1.2

#################################################
#
# Create an image for system dependencies
# hadolint ignore=DL3007
FROM ghcr.io/opensafely-core/base-docker:22.04 as sqlrunner-dependencies

# Default env vars for all images
ENV VIRTUAL_ENV=/opt/venv \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN mkdir /workspace
WORKDIR /workspace

# We are going to use an apt cache on the host, so we disable the default Debian Docker
# clean up that deletes that cache on every apt install.
RUN rm -f /etc/apt/apt.conf.d/docker-clean

# Install system dependencies
COPY dependencies.txt /root/dependencies.txt
RUN --mount=type=cache,target=/var/cache/apt \
    /usr/bin/env /root/docker-apt-install.sh /root/dependencies.txt

#################################################
#
# Create an image for build dependencies from the system dependencies image
FROM sqlrunner-dependencies as sqlrunner-builder

# Install build dependencies
COPY build-dependencies.txt /root/build-dependencies.txt
RUN /root/docker-apt-install.sh /root/build-dependencies.txt

# Create a virtualenv for isolation from system Python
RUN --mount=type=cache,target=/root/.cache \
    python3 -m venv /opt/venv && \
    /opt/venv/bin/python -m pip install -U pip

# Install Python dependencies into the virtualenv
COPY requirements.prod.txt /root/requirements.prod.txt
# hadolint ignore=DL3042
RUN --mount=type=cache,target=/root/.cache \
    python -m pip install -r /root/requirements.prod.txt

################################################
#
# Create a base image from the the system dependencies image
FROM sqlrunner-dependencies as sqlrunner-base

# Some static metadata for this specific image, as defined by:
# https://github.com/opencontainers/image-spec/blob/master/annotations.md#pre-defined-annotation-keys
# The org.opensafely.action label is used by the jobrunner to indicate this is
# an approved action image to run.
LABEL org.opencontainers.image.title="sqlrunner" \
    org.opencontainers.image.description="SQLRunner action for opensafely.org" \
    org.opencontainers.image.source="https://github.com/opensafely-core/sqlrunner" \
    org.opensafely.action="sqlrunner"

# Copy the virtualenv
COPY --from=sqlrunner-builder /opt/venv /opt/venv

################################################
#
# Create a production image from the base image
FROM sqlrunner-base as sqlrunner

ENTRYPOINT ["python", "-m", "sqlrunner"]

# Copy the application code
COPY . /app
