"""
Configuração Industrial do Servidor WSGI Gunicorn para o MetalSense Gateway.
Otimizado para alto throughput de telemetria IoT com threads pool e baixo footprint de memória.
"""

import os
import multiprocessing

# Endereço de Bind
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:5000")

# Dimensionamento de Workers baseado em CPU
# Em ambientes fabris, 2-4 workers com threads garantem concorrência e resiliência
workers = int(os.environ.get("GUNICORN_WORKERS", 4))
threads = int(os.environ.get("GUNICORN_THREADS", 4))
worker_class = "gthread"
worker_connections = 1000

# Timeouts industriais (evita hanging connections)
timeout = 30
keepalive = 5
graceful_timeout = 15

# Logging unificado para stdout/stderr para agregação em containers
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("METALSENSE_LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" (%(D)s µs)'


def on_starting(server):
    server.log.info("⚙️ Servidor Gunicorn WSGI MetalSense iniciando...")


def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} finalizado graciosamente.")
