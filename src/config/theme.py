import flet as ft

_LIGHT_THEME = {
    "MODE": "light",
    "PRIMARY_COLOR": "#2563EB", 
    "PRIMARY_HOVER": "#4162BD",
    "BACKGROUND": "#F9FAFB",
    "CARD": "#F3F4F6",
    "CARD_DARK": "#2d2d2d",
    "BORDER": "#404040",
    "ON_PRIMARY": "#FFFFFF",
    "TEXT": "#1F2937",
    "TEXT_SECONDARY": "#6B7280",
    "ERROR": "#EF4444",
    "BACKGROUNDSCREEN": "#D6D5D5",
    "BACK": "#E6E6E6",
    "BLACK": "#000000",
    "INPUT_BG": "#FFFFFF",
}

STYLE = {
    "CARD_RADIUS": 12,
    "CARD_ELEVATION": 8,
    "BORDER_RADIUS_INPUT": 8,
    "FONT_FAMILY": "Segoe UI"
}

__current_theme = _LIGHT_THEME

def set_theme(mode: str = "light"):
    global __current_theme
    __current_theme = _LIGHT_THEME

def get_theme() -> dict:
    return __current_theme

def aplicar_theme(page: ft.Page):
    th = get_theme()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = th["BACKGROUNDSCREEN"]
    page.window_bgcolor = th["BACKGROUNDSCREEN"]
    return th