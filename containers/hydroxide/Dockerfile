# syntax=docker/dockerfile:1
################################################################################
# BUILD STAGE
################################################################################
ARG GO_VERSION=1.17
FROM --platform=$BUILDPLATFORM golang:${GO_VERSION} AS build
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
FROM alpine:3.20 AS final

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
CMD [ "hydroxide", "serve" ]
