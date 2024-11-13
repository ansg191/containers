FROM alpine:3.20.3@sha256:1e42bbe2508154c9126d48c2b8a75420c3544343bf86fd041fb7527e017a4b4a AS build

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apk \
    apk --update add \
        gcc \
        libc-dev \
        make \
        openssl \
        openssl-dev \
        zlib-dev \
        e2fsprogs-dev

WORKDIR /app

# Download tarsnap source code and verify its integrity
ARG TARSNAP_VERSION=1.0.40
ADD --checksum=sha256:bccae5380c1c1d6be25dccfb7c2eaa8364ba3401aafaee61e3c5574203c27fd5 \
    https://www.tarsnap.com/download/tarsnap-autoconf-$TARSNAP_VERSION.tgz /app/

# Build and install tarsnap
RUN tar -xzf tarsnap-autoconf-$TARSNAP_VERSION.tgz && \
    cd tarsnap-autoconf-$TARSNAP_VERSION && \
    ./configure --prefix /app && \
    make all && \
    make install

# Final stage
FROM alpine:3.20.3@sha256:1e42bbe2508154c9126d48c2b8a75420c3544343bf86fd041fb7527e017a4b4a AS final

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

# Copy binaries from the build stage
COPY --from=build /app/bin/* /usr/local/bin/
# Copy the tarsnap.conf file
COPY tarsnap.conf /app/etc/tarsnap.conf

USER appuser

CMD [ "tarsnap" ]
