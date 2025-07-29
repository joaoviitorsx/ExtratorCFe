import flet as ft
from src.config import theme
from src.components.utility import badge

def folderCard(folder_name: str, total_files: int, on_change_folder):
    th = theme.get_theme()
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER_OPEN, color=th["PRIMARY_COLOR"], size=20),
                    ft.Text("Pasta Selecionada", weight=ft.FontWeight.W_500, size=16, color=th["TEXT"])
                ], spacing=8),
                ft.TextButton("Alterar", icon=ft.Icons.REFRESH, on_click=on_change_folder)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(folder_name, weight=ft.FontWeight.W_500, size=14, color=th["TEXT"]),
            ft.Row([
                badge(f"{total_files} arquivos XML", th["CARD"], th["PRIMARY_COLOR"]),
            ], spacing=8)
        ], spacing=12),
        bgcolor=th["CARD"],
        border_radius=12,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
    )

def processingCard(folder_name: str, processed: int, total: int, on_start=None):
    th = theme.get_theme()
    progress = processed / total if total > 0 else 0
    card_content = [
        ft.Row([
            ft.Icon(ft.Icons.SETTINGS, color=th["PRIMARY_COLOR"], size=20),
            ft.Text("Processando Arquivos", weight=ft.FontWeight.W_500, size=16, color=th["TEXT"])
        ], spacing=8),

        ft.Column([
            ft.Row([
                ft.Text(folder_name, weight=ft.FontWeight.W_500, expand=True),
                ft.Text(f"{processed} de {total}", size=12, color=th["TEXT_SECONDARY"])
            ]),
            ft.ProgressBar(
                value=progress, 
                height=8, 
                bgcolor=th["CARD"], 
                color=th["PRIMARY_COLOR"]
            )
        ], spacing=8),

        ft.Row([
            ft.Column([
                ft.Text(str(processed), size=24, weight=ft.FontWeight.W_600, color=th["PRIMARY_COLOR"]),
                ft.Text("Processados", size=12, color=th["TEXT_SECONDARY"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=1),

            ft.Column([
                ft.Text(str(processed), size=24, weight=ft.FontWeight.W_600, color=th["PRIMARY_COLOR"]),
                ft.Text("Válidos", size=12, color=th["TEXT_SECONDARY"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=1)
        ])
    ]
    if on_start:
        card_content.append(
            ft.Row([
                ft.ElevatedButton(
                    "Iniciar Processamento",
                    icon=ft.Icons.UPLOAD,
                    on_click=on_start,
                    expand=False,
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
    return ft.Container(
        content=ft.Column(card_content, spacing=16),
        bgcolor=th["CARD"],
        border_radius=12,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
    )

def completedCard(total_files: int, validos: int, cancelados: int, erros: int, lista_erros: list, on_download, on_new_folder):
    th = theme.get_theme()

    card_content = [
        ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=20),
            ft.Text("Processamento Concluído", weight=ft.FontWeight.W_500, size=16, color=ft.Colors.GREEN_600)
        ], spacing=8),

        ft.Row([
            ft.Column([
                ft.Text(str(validos), size=24, weight=ft.FontWeight.W_600, color=th["PRIMARY_COLOR"]),
                ft.Text("Válidos", size=12, color=th["TEXT_SECONDARY"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=1),

            ft.Column([
                ft.Text(str(cancelados), size=24, weight=ft.FontWeight.W_600, color=ft.Colors.ORANGE_700),
                ft.Text("Cancelados", size=12, color=th["TEXT_SECONDARY"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=1),

            ft.Column([
                ft.Text(str(erros), size=24, weight=ft.FontWeight.W_600, color=th["ERROR"]),
                ft.Text("Erros", size=12, color=th["TEXT_SECONDARY"])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=1),
        ]),

        ft.Row([
            ft.ElevatedButton(
                "Baixar Planilha",
                icon=ft.Icons.DOWNLOAD,
                bgcolor=th["PRIMARY_COLOR"],
                color=th["ON_PRIMARY"],
                expand=True,
                on_click=on_download
            ),
            ft.OutlinedButton(
                "Nova Pasta",
                icon=ft.Icons.REFRESH,
                expand=True,
                on_click=on_new_folder
            )
        ], spacing=12)
    ]

    if lista_erros:
        erros_visiveis = lista_erros[:3]
        mais_erros = len(lista_erros) - 3 if len(lista_erros) > 3 else 0

        lista_erros_text = [ft.Text(f"• {error}", size=12) for error in erros_visiveis]

        if mais_erros > 0:
            lista_erros_text.append(
                ft.Text(f"... e mais {mais_erros} arquivo(s) com erro.", size=12, italic=True, color=th["TEXT_SECONDARY"])
            )

        card_content.insert(-1, ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.WARNING, color=th["ERROR"], size=16),
                    ft.Text("Arquivos com problemas:", weight=ft.FontWeight.W_500, size=14)
                ], spacing=8),
                ft.Column(lista_erros_text, spacing=2)
            ], spacing=8),
            bgcolor=th["CARD"],
            border=ft.border.all(1, th["ERROR"]),
            border_radius=8,
            padding=12
        ))

    return ft.Container(
        content=ft.Column(card_content, spacing=16),
        bgcolor=th["CARD"],
        border_radius=12,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
    )
