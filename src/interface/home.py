import flet as ft
from src.components.notificacao import notificacao
from src.controller.extratorController import ExtratorController

def HomePage(page: ft.Page):
    controller = ExtratorController()

    pasta_selecionada = ft.Text("Nenhuma pasta selecionada", size=14, italic=True)
    status_text = ft.Text("Aguardando ação...", size=16)

    pasta_picker = ft.FilePicker()

    def on_pasta_selecionada(e):
        if e.path:
            pasta_selecionada.value = f"Pasta selecionada: {e.path}"
            pasta_selecionada.color = "green"
            pasta_selecionada.update()
            notificacao(page, "Pasta selecionada", f"{e.path}", tipo="info")

    pasta_picker.on_result = on_pasta_selecionada

    def processar_arquivos(e):
        if "Pasta selecionada:" not in pasta_selecionada.value:
            notificacao(page, "Erro", "Selecione uma pasta antes de iniciar!", tipo="erro")
            return

        pasta = pasta_selecionada.value.replace("Pasta selecionada: ", "")
        resultado = controller.processar_pasta(pasta)

        if resultado["status"] == "sucesso":
            notificacao(page, "Processamento Concluído", resultado["mensagem"], tipo="sucesso")
            status_text.value = resultado["mensagem"]
        else:
            notificacao(page, "Erro", resultado["mensagem"], tipo="erro")
            status_text.value = "Erro no processamento."

        status_text.update()

    btn_escolher_pasta = ft.ElevatedButton("Selecionar Pasta", on_click=lambda _: pasta_picker.get_directory_path())
    btn_processar = ft.ElevatedButton("Iniciar Processamento", on_click=processar_arquivos)

    return ft.View(
        "/home",
        controls=[
            pasta_picker,
            ft.Column(
                [
                    ft.Text("Extrator CF-e", size=30, weight="bold"),
                    ft.Text("Escolha a pasta com arquivos XML para processar.", size=16),
                    btn_escolher_pasta,
                    pasta_selecionada,
                    btn_processar,
                    ft.Divider(),
                    status_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=20
            )
        ],
    )
