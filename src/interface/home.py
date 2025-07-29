import os
import flet as ft
import time
import threading
from enum import Enum

from src.components.notificacao import notificacao
from src.controller.extratorController import ExtratorController
from src.config import theme
from src.components.sections import header_section, drop_zone_section
from src.components.card import folderCard, processingCard, completedCard


class ProcessingState(Enum):
    IDLE = "idle"
    FOLDER_SELECTED = "folder_selected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


def HomePage(page: ft.Page):
    th = theme.get_theme()
    controller = ExtratorController()

    state = {
        "status": ProcessingState.IDLE,
        "folder_path": "",
        "folder_name": "",
        "total_files": 0,
        "processed_files": 0,
        "validos": 0,
        "cancelados": 0,
        "errors": []
    }

    pasta_picker = ft.FilePicker()
    salvar_picker = ft.FilePicker()
    page.overlay.extend([pasta_picker, salvar_picker])

    main_view = ft.Container(expand=True)

    def render():
        current = state["status"]
        if current == ProcessingState.IDLE:
            main_view.content = viewIdle()
        elif current == ProcessingState.FOLDER_SELECTED:
            main_view.content = viewFolderSelected()
        elif current == ProcessingState.PROCESSING:
            main_view.content = viewProcessing()
        elif current == ProcessingState.COMPLETED:
            main_view.content = viewCompleted()
        page.update()

    def viewIdle():
        return ft.Column([
            header_section(),
            drop_zone_section(lambda e: pasta_picker.get_directory_path())
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    def viewFolderSelected():
        return ft.Column([
            header_section(),
            processingCard(
                state['folder_name'],
                state['processed_files'],
                state['total_files'],
                on_start=lambda e: iniciarProcessamento()
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    def viewProcessing():
        return ft.Column([
            header_section(),
            processingCard(state['folder_name'], state['processed_files'], state['total_files'])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    def viewCompleted():
        return ft.Column([
            header_section(),
            completedCard(
                total_files=state['total_files'],
                validos=state['validos'],
                cancelados=state['cancelados'],
                erros=len(state['errors']),
                lista_erros=state['errors'],
                on_download=lambda e: salvar_picker.save_file(file_type="xlsx", dialog_title="Salvar planilha como..."),
                on_new_folder=lambda e: resetar()
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    def pastaEscolhida(e):
        if e.path:
            state["folder_path"] = e.path
            state["folder_name"] = e.path.split("\\")[-1]

            total_xml = len([
                f for f in os.listdir(e.path)
                if f.lower().endswith(".xml") and os.path.isfile(os.path.join(e.path, f))
            ])

            state["total_files"] = total_xml
            state["status"] = ProcessingState.FOLDER_SELECTED

            notificacao(page, "Pasta selecionada", f"{e.path} - {total_xml} arquivos XML encontrados", tipo="info")
            render()

    def iniciarProcessamento():
        state["status"] = ProcessingState.PROCESSING
        render()

        def processar():
            for i in range(state["total_files"] + 1):
                state["processed_files"] = i
                render()
                time.sleep(0.05)

            resultado = controller.processarPasta(state["folder_path"])

            if resultado["status"] == "sucesso":
                notificacao(page, "Processamento concluído", resultado["mensagem"], tipo="sucesso")
                state["status"] = ProcessingState.COMPLETED
                state["validos"] = resultado["validos"]
                state["cancelados"] = resultado["cancelados"]
                state["errors"] = resultado["lista_erros"]
            else:
                notificacao(page, "Erro", resultado["mensagem"], tipo="erro")
                state["status"] = ProcessingState.ERROR

            render()

        threading.Thread(target=processar, daemon=True).start()

    def salvarPlanilha(e):
        if not e.path:
            notificacao(page, "Aviso", "Salvamento cancelado", tipo="alerta")
            return

        caminho_planilha = e.path
        if not caminho_planilha.lower().endswith(".xlsx"):
            caminho_planilha += ".xlsx"

        resultado_exportacao = controller.exportarPlanilha(caminho_planilha)
        print(f"Resultado da exportação: {resultado_exportacao}")

        def fecharDialog(e=None):
            page.close(dialog)
            page.update()

        def abrirPlanilha(e=None):
            print(f"Abrindo planilha: {caminho_planilha}")
            import subprocess, sys
            page.close(dialog)
            page.update()
            if sys.platform == "win32":
                os.startfile(caminho_planilha)
            else:
                subprocess.Popen(["open", caminho_planilha])

        if resultado_exportacao["status"] == "sucesso":
            print("Exportação sucesso, mostrando dialog")

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Planilha gerada com sucesso!"),
                content=ft.Text("Deseja abrir a planilha agora?"),
                actions=[
                    ft.TextButton("Abrir", on_click=abrirPlanilha),
                    ft.TextButton("Fechar", on_click=fecharDialog)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.dialog = dialog
            dialog.open = True
            page.update()
        else:
            notificacao(page, "Erro", resultado_exportacao["mensagem"], tipo="erro")

    def resetar():
        state.update({
            "status": ProcessingState.IDLE,
            "folder_path": "",
            "folder_name": "",
            "total_files": 0,
            "processed_files": 0,
            "validos": 0,
            "cancelados": 0,
            "errors": []
        })
        render()

    pasta_picker.on_result = pastaEscolhida
    salvar_picker.on_result = salvarPlanilha

    page.add(ft.Container(
        content=ft.Column([main_view], expand=True, alignment=ft.MainAxisAlignment.CENTER),
        expand=True,
        padding=30
    ))
    render()

    return ft.View(
        route="/home", 
        controls=page.controls
    )
