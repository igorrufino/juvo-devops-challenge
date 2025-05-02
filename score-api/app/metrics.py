# app/metrics.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import start_http_server, Counter, Histogram
import time

# Métricas definidas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP',
    ['endpoint']
)

def init_metrics(port=8001):
    """Inicializa o servidor de métricas Prometheus"""
    start_http_server(port)
    print(f"Métricas expostas na porta {port} (rota: /metrics)")

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coletar métricas Prometheus"""
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        REQUEST_LATENCY.labels(endpoint=endpoint).observe(process_time)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()

        return response
