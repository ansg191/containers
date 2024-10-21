FROM ghcr.io/ansg191/containers/tarsnapper:v0.5.0

WORKDIR /app

USER root
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY main.py .

USER appuser
CMD [ "python", "main.py" ]
