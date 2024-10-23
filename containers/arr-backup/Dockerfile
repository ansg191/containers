FROM ghcr.io/ansg191/containers/tarsnapper:v0.5.0@sha256:435846c83d5e6cd55fd6a4ccda065fd2a0e126e54244638836266978aedf38c2

WORKDIR /app

USER root
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY main.py .

USER appuser
CMD [ "python", "main.py" ]
