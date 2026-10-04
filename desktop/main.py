"""
Ponto de entrada (Entrypoint) da Aplicação MetalSense Desktop.
Inicializa serviços, controladores e a janela principal do sistema.
"""
import sys
import os
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para garantir imports consistentes
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def main():
    try:
        import customtkinter as ctk
    except ImportError:
        print("\n" + "=" * 60)
        print(" [ERRO] O pacote 'customtkinter' é necessário para a interface desktop.")
        print(" Por favor, instale as dependências executando:")
        print("     pip install customtkinter matplotlib")
        print("=" * 60 + "\n")
        sys.exit(1)

    from desktop.config import DATA_FILE
    from desktop.services.telemetry_service import TelemetryService
    from desktop.controllers.app_controller import AppController
    from desktop.views.main_window import MainWindow

    # 1. Instanciação dos Serviços de Domínio
    telemetry_service = TelemetryService(data_path=DATA_FILE)

    # 2. Instanciação do Controlador
    controller = AppController(service=telemetry_service)

    # 3. Instanciação da View / Janela Principal
    app = MainWindow(controller=controller)
    controller.set_view(app)

    # 4. Encerramento seguro de threads de background ao fechar janela
    def on_closing():
        controller.parar_streaming_ao_vivo()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", on_closing)

    # 5. Início do Loop de Eventos da GUI
    app.mainloop()


if __name__ == "__main__":
    main()
