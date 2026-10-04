"""
Serviço de Processamento em Background Não-Bloqueante (Non-blocking Workers).
Permite executar tarefas pesadas de I/O e telemetria contínua sem congelar a UI.
"""
import threading
import queue
import time
from typing import Callable, Any, Optional


class AsyncWorker(threading.Thread):
    """
    Executa uma tarefa única em background e notifica a thread principal
    via callbacks thread-safe ou fila de eventos.
    """

    def __init__(
        self,
        target_fn: Callable[..., Any],
        args: tuple = (),
        kwargs: dict = None,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_start: Optional[Callable[[], None]] = None,
    ):
        super().__init__(daemon=True)
        self.target_fn = target_fn
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.on_success = on_success
        self.on_error = on_error
        self.on_start = on_start

    def run(self):
        if self.on_start:
            try:
                self.on_start()
            except Exception:
                pass

        try:
            resultado = self.target_fn(*self.args, **self.kwargs)
            if self.on_success:
                self.on_success(resultado)
        except Exception as ex:
            if self.on_error:
                self.on_error(ex)


class LiveMonitoringWorker(threading.Thread):
    """
    Worker daemon para simulação contínua de telemetria em tempo real
    com intervalo configurável e cancelamento seguro.
    """

    def __init__(
        self,
        task_callback: Callable[[], Any],
        interval_seconds: float = 2.0,
        on_tick: Optional[Callable[[Any], None]] = None,
    ):
        super().__init__(daemon=True)
        self.task_callback = task_callback
        self.interval_seconds = interval_seconds
        self.on_tick = on_tick
        self._stop_event = threading.Event()

    def run(self):
        while not self._stop_event.is_set():
            try:
                res = self.task_callback()
                if self.on_tick:
                    self.on_tick(res)
            except Exception as e:
                pass
            self._stop_event.wait(self.interval_seconds)

    def stop(self):
        """Sinaliza encerramento da thread de monitoramento."""
        self._stop_event.set()

    def is_running(self) -> bool:
        return not self._stop_event.is_set()
