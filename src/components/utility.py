import flet as ft

def badge(text: str, text_color: str, bg_color: str):
    return ft.Container(
        content=ft.Text(text, size=12, color=text_color),
        bgcolor=bg_color,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=12, vertical=6)
    )