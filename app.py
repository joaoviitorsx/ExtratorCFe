import flet as ft
from src.config import theme
from src.interface.home import HomePage

def main(page: ft.Page):
    th = theme.aplicar_theme(page)

    page.title = "Extrator CF-e"
    page.window.height = 800
    page.window.width = 650

    def trocaRota(e):
        page.views.clear()

        if page.route in ["/", "/home"]:
            page.views.append(HomePage(page))
        else:
            page.views.append(ft.View("/", controls=[ft.Text("Página não encontrada!")]))

        page.update()

    page.on_route_change = trocaRota
    page.go("/home")

ft.app(target=main, assets_dir="assets", view=ft.AppView.FLET_APP)
