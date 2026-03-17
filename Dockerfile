FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir ".[dashboard]" \
    && chmod +x docker-entrypoint.sh

EXPOSE 8050

ENTRYPOINT ["./docker-entrypoint.sh"]
