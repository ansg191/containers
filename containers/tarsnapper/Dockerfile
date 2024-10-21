ARG TARSNAP_VERSION=1.0.40
FROM ghcr.io/ansg191/containers/tarsnap:v${TARSNAP_VERSION} AS tarsnap-base

FROM python:3.13.0-alpine@sha256:c38ead8bcf521573dad837d7ecfdebbc87792202e89953ba8b2b83a9c5a520b6

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
