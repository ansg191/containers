ARG TARSNAP_VERSION=1.0.40
FROM ghcr.io/ansg191/containers/tarsnap:v${TARSNAP_VERSION} AS tarsnap-base

FROM python:3.13.1-alpine@sha256:657dbdb20479a6523b46c06114c8fec7db448232f956a429d3cc0606d30c1b59

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Create a non-priviliged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy tarsnap binary and config from tarsnap-base
WORKDIR /app
COPY --from=tarsnap-base /usr/local/bin/* /usr/local/bin/
COPY --from=tarsnap-base /app/etc/tarsnap.conf /app/etc/tarsnap.conf

# Install tarsnapper
ARG TARSNAPPER_VERSION=0.5.0
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install tarsnapper==${TARSNAPPER_VERSION}

USER appuser

CMD [ "tarsnapper" ]
