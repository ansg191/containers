FROM alpine:3.20.3 AS build

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apk \
    apk --update add \
        gcc \
        libc-dev \
        make \
        openssl \
        openssl-dev \
        zlib-dev \
        e2fsprogs-dev \
        gnupg

WORKDIR /app

## Download tarsnap GPG key
ARG TARSNAP_GPG_ID=1EF1354792C56BEA
RUN mkdir -p ~/.gnupg/public-keys.d && \
    gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys $TARSNAP_GPG_ID && \
    gpg --batch --fingerprint $TARSNAP_GPG_ID

# Download tarsnap source code and verify its integrity
ARG TARSNAP_VERSION=1.0.40
RUN wget https://www.tarsnap.com/download/tarsnap-autoconf-$TARSNAP_VERSION.tgz && \
    wget https://www.tarsnap.com/download/tarsnap-sigs-$TARSNAP_VERSION.asc && \
    gpg --batch --decrypt tarsnap-sigs-$TARSNAP_VERSION.asc | \
    grep 'SHA256' | \
    sed -E 's/SHA256 \(([^)]+)\) = ([0-9a-fA-F]+)/\2  \1/' | \
    sha256sum -c - && \
    tar -xzf tarsnap-autoconf-$TARSNAP_VERSION.tgz && \
    cd tarsnap-autoconf-$TARSNAP_VERSION && \
    ./configure --prefix /app && \
    make all && \
    make install

# Final stage
FROM alpine:3.20.3 AS final

# Install tini
RUN --mount=type=cache,target=/var/cache/apk \
    apk --update add tini

# Copy binaries from the build stage
COPY --from=build /app/bin/* /usr/local/bin/
# Copy the tarsnap.conf file
COPY tarsnap.conf /app/etc/tarsnap.conf

ENTRYPOINT [ "tini", "--" ]
CMD [ "tarsnap" ]
