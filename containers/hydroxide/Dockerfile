################################################################################
# BUILD STAGE
################################################################################
FROM --platform=$BUILDPLATFORM golang:1.23@sha256:70031844b8c225351d0bb63e2c383f80db85d92ba894e3da7e13bcf80efa9a37 AS build
WORKDIR /src

# Clone hydroxide
ARG HYDROXIDE_VERSION=v0.2.29
RUN git clone \
    --depth 1 \
    --branch $HYDROXIDE_VERSION \
    https://github.com/emersion/hydroxide.git /src

# Download dependencies
RUN --mount=type=cache,target=/go/pkg/mod/ \
    go mod download -x

# Target architecture for the build.
ARG TARGETARCH

# Build the application.
RUN --mount=type=cache,target=/go/pkg/mod/ \
    CGO_ENABLED=0 GOARCH=$TARGETARCH go build -o /bin/hydroxide ./cmd/hydroxide

################################################################################
# FINAL STAGE
################################################################################
FROM alpine:3.21@sha256:21dc6063fd678b478f57c0e13f47560d0ea4eeba26dfc947b2a4f81f686b9f45 AS final

# Install runtime dependencies
RUN --mount=type=cache,target=/var/cache/apk \
    apk --update add \
        ca-certificates \
        tzdata \
        tini \
        && \
        update-ca-certificates

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistant" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser
USER appuser

# Copy the executable from the "build" stage.
COPY --from=build /bin/hydroxide /bin/

ENV XDG_CONFIG_HOME=/config
ENTRYPOINT [ "tini", "--" ]

EXPOSE 1025 1143 8080

CMD [ \
    "hydroxide", \
    "-smtp-host", \
    "0.0.0.0", \
    "-imap-host", \
    "0.0.0.0", \
    "-carddav-host", \
    "0.0.0.0", \
    "serve" \
]
