import flet as ft
from src.config import theme

def sectionHeader():
    th = theme.get_theme()
    return ft.Column([
        ft.Text("Extrator CF-e", size=28, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
        ft.Text("Selecione uma pasta com os arquivos XML para processar", size=16, color=th["TEXT_SECONDARY"], text_align=ft.TextAlign.CENTER)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)


def sectionDrop(on_click):
    th = theme.get_theme()
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.FOLDER_OPEN, size=48, color=th["TEXT_SECONDARY"]),
            ft.Text("Clique para selecionar uma pasta", size=16),
            ft.Text("Arquivos XML de CF-e", size=14, color=th["TEXT_SECONDARY"])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        height=200,
        border=ft.border.all(2, th["BORDER"]),
        border_radius=12,
        on_click=on_click,
        alignment=ft.alignment.center,
        ink=True,
        padding=20
    )
