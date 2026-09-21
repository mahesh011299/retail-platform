FROM python:3.12-slim

WORKDIR /app

RUN useradd -m appuser

COPY app1/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app1/ .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8081

ENV APP_VERSION=4.2.0
ENV ENVIRONMENT=production
ENV PAYMENT_STATUS=working
ENV HEALTH_STATUS=healthy

HEALTHCHECK --interval=10s \
    --timeout=5s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8081/health')"

CMD ["python", "app.py"]