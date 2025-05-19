import flet as ft

def main(page: ft.Page):
    page.title = "Memoro"
    page.window_width = 800
    page.window_height = 600

    page.add(
        ft.Text("Bem-vindo ao Memoro!", size=30, weight="bold"),
        ft.Text("Sua memória digital pessoal com IA")
    )

ft.app(target=main)