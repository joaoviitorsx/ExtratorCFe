import os
import flet as ft
import time
import threading
from enum import Enum

from src.components.notificacao import notificacao, notificacaoProgresso
from src.controller.extratorController import ExtratorController
from src.config import theme
from src.components.sections import sectionHeader, sectionDrop, footer
from src.components.card import folderCard, processingCard, completedCard, mainCard

class ProcessingState(Enum):
    IDLE = "idle"
    FOLDER_SELECTED = "folder_selected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

def HomePage(page: ft.Page):
    th = theme.aplicar_theme(page)
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
            sectionHeader(),
            mainCard([
                ft.Container(height=8),
                sectionDrop(lambda e: pasta_picker.get_directory_path()),
            ]),
            footer()
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
    
    def viewFolderSelected():
        return ft.Column([
            sectionHeader(),
            mainCard([
                folderCard(
                    state['folder_name'],
                    state['total_files'],
                    on_change_folder=lambda e: pasta_picker.get_directory_path(),
                    on_next=lambda e: gotoProcessing()
                )
            ]),
            footer()
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def gotoProcessing():
        state["status"] = ProcessingState.PROCESSING
        render()

    def viewProcessing():
        return ft.Column([
            sectionHeader(),
            mainCard([
                processingCard(
                    state['folder_name'],
                    state['processed_files'],
                    state['total_files'],
                    on_start=lambda e: iniciarProcessamento()
                )
            ]),
            footer()
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def viewCompleted():
        return ft.Column([
            sectionHeader(),
            mainCard([
                completedCard(
                    total_files=state['total_files'],
                    validos=state['validos'],
                    cancelados=state['cancelados'],
                    erros=len(state['errors']),
                    lista_erros=state['errors'],
                    on_download=lambda e: salvar_picker.save_file(file_type="xlsx", dialog_title="Salvar planilha como..."),
                    on_new_folder=lambda e: resetar()
                )
            ]),
            footer()
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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

        def atualizarProgresso(processados, total):
            state["processed_files"] = processados
            state["total_files"] = total
            render()

        def processar():
            resultado = controller.processarPasta(
                state["folder_path"],
                progresso_callback=atualizarProgresso
            )

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

        progresso_card = notificacaoProgresso(page)

        def exportar():
            resultado_exportacao = controller.exportarPlanilha(caminho_planilha)
            if progresso_card in page.overlay:
                page.overlay.remove(progresso_card)
                page.update()

            def fecharDialog(e=None):
                page.close(dialog)
                page.update()

            def abrirPlanilha(e=None):
                import subprocess, sys
                page.close(dialog)
                page.update()
                if sys.platform == "win32":
                    os.startfile(caminho_planilha)
                else:
                    subprocess.Popen(["open", caminho_planilha])

            if resultado_exportacao["status"] == "sucesso":
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
                page.open(dialog)
            else:
                notificacao(page, "Erro", resultado_exportacao["mensagem"], tipo="erro")

        threading.Thread(target=exportar, daemon=True).start()

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
        padding=30,
    ))
    render()

    return ft.View(
        route="/home", 
        controls=page.controls
    )
