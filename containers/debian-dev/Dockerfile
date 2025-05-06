FROM debian:12.10 AS base

FROM rust:1.86-bookworm AS helix-builder
ARG HELIX_VERSION="25.01.1"

WORKDIR /app
RUN cargo install --locked cargo-deb
RUN git clone https://github.com/helix-editor/helix.git --branch ${HELIX_VERSION} --depth 1
WORKDIR /app/helix

RUN --mount=type=cache,target=/app/helix/target/release \
    --mount=type=cache,target=/usr/local/cargo/git/db \
    --mount=type=cache,target=/usr/local/cargo/registry/ \
    cargo deb -- --locked

FROM base AS final

# Install useful tools and utilities
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        git \
        curl \
        wget \
        vim \
        nano \
        less \
        htop \
        bat \
        net-tools \
        iputils-ping \
        dnsutils \
        man-db \
        strace \
        lsof \
        tcpdump \
        nmap \
        procps \
        sysstat \
        gdb \
        ncdu \
        file \
        tree \
        jq \
        whois \
        ncat \
        traceroute \
        mtr \
        iperf3 \
        kubernetes-client && \
    rm -rf /var/lib/apt/lists/* && \
    # Rename batcat to bat
    ln -s /usr/bin/batcat /usr/local/bin/bat

COPY --from=helix-builder /app/helix/target/debian/helix*.deb /tmp/
RUN dpkg -i /tmp/helix*.deb && rm -rf /tmp/helix*.deb

COPY root/ /
