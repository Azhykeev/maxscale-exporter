import asyncio
from aiohttp import web, BasicAuth
import aiohttp
import prometheus_client
from prometheus_client import Gauge
import os

# Prometheus metrics
maxscale_up = Gauge('maxscale_up', 'MaxScale service availability', ['pod'])
maxscale_queries = Gauge('maxscale_queries', 'Number of queries processed by MaxScale', ['pod'])
maxscale_connections = Gauge('maxscale_connections', 'Number of current connections to MaxScale', ['pod'])
maxscale_sessions = Gauge('maxscale_sessions', 'Number of active sessions on MaxScale', ['pod'])
maxscale_latency = Gauge('maxscale_latency', 'Average query latency in milliseconds', ['pod'])
maxscale_errors = Gauge('maxscale_errors', 'Number of errors encountered by MaxScale', ['pod'])
maxscale_service_connections = Gauge('maxscale_service_connections', 'Connections per service', ['pod', 'service'])
maxscale_server_connections = Gauge('maxscale_server_connections', 'Connections per server', ['pod', 'server'])
maxscale_version = Gauge('maxscale_version', 'MaxScale version', ['pod', 'version'])
maxscale_thread_usage = Gauge('maxscale_thread_usage', 'Thread usage in MaxScale', ['pod'])
maxscale_listener_connections = Gauge('maxscale_listener_connections', 'Connections per listener', ['pod', 'listener'])
maxscale_memory_usage = Gauge('maxscale_memory_usage', 'Memory usage of MaxScale in bytes', ['pod'])
maxscale_cpu_usage = Gauge('maxscale_cpu_usage', 'CPU usage of MaxScale as a percentage', ['pod'])

class MaxScaleExporter:
    def __init__(self, maxscale_pods, username, password):
        self.maxscale_pods = maxscale_pods
        self.endpoints = ["/v1/maxscale", "/v1/services", "/v1/servers", "/v1/threads", "/v1/listeners"]
        self.auth = BasicAuth(username, password)

    async def fetch_metrics(self, session, pod, endpoint):
        url = f"http://{pod}:8989{endpoint}"
        try:
            async with session.get(url, auth=self.auth) as response:
                if response.status == 200:
                    data = await response.json()
                    maxscale_up.labels(pod=pod).set(1)
                    maxscale_queries.labels(pod=pod).set(data.get('queries', 0))
                    maxscale_connections.labels(pod=pod).set(data.get('connections', 0))
                    maxscale_sessions.labels(pod=pod).set(data.get('sessions', 0))
                    maxscale_latency.labels(pod=pod).set(data.get('latency', 0))
                    maxscale_errors.labels(pod=pod).set(data.get('errors', 0))
                    
                    # Service-level connections
                    for service, connections in data.get('services', {}).items():
                        maxscale_service_connections.labels(pod=pod, service=service).set(connections)

                    # Server-level connections
                    for server, connections in data.get('servers', {}).items():
                        maxscale_server_connections.labels(pod=pod, server=server).set(connections)

                    # Thread usage
                    for thread, usage in data.get('threads', {}).items():
                        maxscale_thread_usage.labels(pod=pod).set(usage)

                    # Listener connections
                    for listener, connections in data.get('listeners', {}).items():
                        maxscale_listener_connections.labels(pod=pod, listener=listener).set(connections)

                    # Memory usage (if available)
                    if 'memory' in data:
                        maxscale_memory_usage.labels(pod=pod).set(data['memory'].get('total', 0))

                    # CPU usage (if available)
                    if 'cpu' in data:
                        maxscale_cpu_usage.labels(pod=pod).set(data['cpu'].get('usage', 0))

                    # MaxScale version
                    version = data.get('version', 'unknown')
                    maxscale_version.labels(pod=pod, version=version).set(1)
                else:
                    maxscale_up.labels(pod=pod).set(0)
        except Exception as e:
            print(f"Error fetching metrics from {pod}{endpoint}: {e}")
            maxscale_up.labels(pod=pod).set(0)

    async def collect_metrics(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_metrics(session, pod, endpoint) for pod in self.maxscale_pods for endpoint in self.endpoints]
            await asyncio.gather(*tasks)

async def metrics_handler(request):
    await exporter.collect_metrics()
    return web.Response(text=prometheus_client.generate_latest().decode('utf-8'), content_type='text/plain')

if __name__ == "__main__":
    # Read MaxScale pods from environment variables
    maxscale_pods = os.getenv("MAXSCALE_PODS", "maxscale-pod-1,maxscale-pod-2,maxscale-pod-3").split(",")
    username = os.getenv("MAXSCALE_USER", "admin")
    password = os.getenv("MAXSCALE_PASSWORD", "admin")

    # Create the exporter instance with authentication
    exporter = MaxScaleExporter(maxscale_pods, username, password)

    # Start the web server
    app = web.Application()
    app.router.add_get('/metrics', metrics_handler)

    # Expose metrics endpoint
    prometheus_client.start_http_server(8001)
    web.run_app(app, port=8000)
