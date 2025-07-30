import flet as ft
from src.config import theme

def sectionHeader():
    th = theme.get_theme()
    return ft.Column([
        ft.Container(
            content=ft.Icon(ft.Icons.DESCRIPTION, size=32, color=th["ON_PRIMARY"]),
            width=64,
            height=64,
            bgcolor=th["PRIMARY_COLOR"],
            shape=ft.BoxShape.CIRCLE,
            alignment=ft.alignment.center
        ),
        ft.Text("Extrator CF-e", size=28, weight=ft.FontWeight.W_600, color=th["TEXT"], text_align=ft.TextAlign.CENTER),
        ft.Text("Selecione uma pasta com os arquivos XML para processar", size=16, color=th["TEXT_SECONDARY"], text_align=ft.TextAlign.CENTER),
        ft.Container(height=16),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16)

def sectionDrop(on_click):
    th = theme.get_theme()
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.FOLDER_OPEN, size=48, color=th["PRIMARY_COLOR"]),
            ft.Text("Clique para selecionar uma pasta", size=16, color=th["TEXT"]),
            ft.Text("Arquivos XML de CF-e", size=14, color=th["TEXT_SECONDARY"])
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        height=200,
        width=450,
        border=ft.border.all(1, th["BORDER"]),
        border_radius=12,
        on_click=on_click,
        alignment=ft.alignment.center,
        ink=True,
        padding=20,
        bgcolor=th["CARD"]
    )

def footer():
    th = theme.get_theme()
    
    return ft.Container(
        content=ft.Column([
            ft.Divider(color=th["TEXT_SECONDARY"], opacity=0.3),
            ft.Container(height=16),
            ft.Row([
                ft.Text(
                    "© 2025 Realize Software. Todos os direitos reservados.",
                    size=12, 
                    color=th["TEXT_SECONDARY"]
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=8),
            ft.Row([
                ft.Text("Versão 1.0.0", size=10, color=th["TEXT_SECONDARY"]),
                ft.Text("•", size=10, color=th["TEXT_SECONDARY"]),
                ft.Text("Suporte: suporte@realize.com.br", size=10, color=th["TEXT_SECONDARY"]),
            ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
        ]),
        margin=ft.margin.only(top=48)
    )