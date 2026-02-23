from prometheus_client import Counter, Gauge, Histogram, Summary, CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest
from fastapi import FastAPI, Response, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Define metrics
REQUEST_COUNT = Counter('request_count', 'Total number of requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Latency of requests in seconds', ['method', 'endpoint'])


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time

        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(latency)

        return response
    
def setup_metrics(app: FastAPI):
    app.add_middleware(PrometheusMiddleware)

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        registry = CollectorRegistry()
        registry.register(REQUEST_COUNT)
        registry.register(REQUEST_LATENCY)
        data = generate_latest(registry)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)