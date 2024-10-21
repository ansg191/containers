FROM ghcr.io/ansg191/containers/tarsnapper:v0.5.0@sha256:2770db20f0ef0d9c9d4e07ab9a21f4e8fdcc28cc0c97693263505f793f25335a

WORKDIR /app

USER root
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY main.py .

USER appuser
CMD [ "python", "main.py" ]
