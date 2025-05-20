import flet as ft
import os
import sqlite3
from datetime import datetime
from ia import summarize_text, extract_tags, ocr_image, current_timestamp
import shutil
from typing import List

DB_PATH = "memoro.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            summary TEXT,
            tags TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_note(content: str, summary: str, tags: list[str]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tags_str = ", ".join(tags)
    timestamp = current_timestamp()
    c.execute("INSERT INTO notes (content, summary, tags, timestamp) VALUES (?, ?, ?, ?)",
              (content, summary, tags_str, timestamp))
    conn.commit()
    conn.close()

def get_all_notes():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, summary, tags, timestamp FROM notes ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_note_by_id(note_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content, summary, tags, timestamp FROM notes WHERE id=?", (note_id,))
    note = c.fetchone()
    conn.close()
    return note

def main(page: ft.Page):
    page.title = "🧠 Memoro – Memória Artificial Pessoal"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 800
    page.padding = 20
    page.scroll = "adaptive"

    upload_result = ft.Text(value="", style="bodySmall", color="green")

    def show_dialog(title: str, message: str):
        page.dialog = ft.AlertDialog(
            title=ft.Text(title, weight="bold"),
            content=ft.Text(message),
            actions=[ft.TextButton("Fechar", on_click=lambda e: setattr(page.dialog, "open", False))],
        )
        page.dialog.open = True
        page.update()

    # ==== ABA 1 ====
    text_field = ft.TextField(
        label="Digite sua anotação",
        multiline=True,
        min_lines=6,
        max_lines=20,
        expand=True,
        border="underline",
    )
    summary_label = ft.Text(value="", selectable=True, style="bodyMedium")
    tags_label = ft.Text(value="", selectable=True, style="bodySmall")

    def handle_submit(e):
        content = text_field.value.strip()
        if not content:
            show_dialog("Erro", "Digite algo para salvar.")
            return
        try:
            summary = summarize_text(content)
            tags = extract_tags(content)

            save_note(content, summary, tags)

            summary_label.value = f"🧠 Resumo:\n{summary}"
            tags_label.value = f"🏷 Tags: {', '.join(tags)}"
            upload_result.value = "✅ Anotação salva com sucesso!"
            text_field.value = ""
        except Exception as err:
            upload_result.value = f"❌ Erro ao processar IA: {err}"

        page.update()

    def handle_upload(e):
        if not file_picker.result or not file_picker.result.files:
            return

        file = file_picker.result.files[0]
        original_path = file.path

        if not original_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
            upload_result.value = "❌ Formato de imagem não suportado."
            page.update()
            return

        temp_path = f"temp_{file.name}"
        shutil.copy(original_path, temp_path)

        try:
            extracted_text = ocr_image(temp_path)
            text_field.value = extracted_text
            upload_result.value = "📸 Texto extraído com sucesso da imagem."
        except Exception as err:
            upload_result.value = f"❌ Erro ao processar a imagem: {err}"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        page.update()

    file_picker = ft.FilePicker(on_result=handle_upload)
    page.overlay.append(file_picker)

    aba_anotacao = ft.Container(
        content=ft.Column(
            [
                ft.Text("📝 Nova Anotação", style="titleLarge"),
                text_field,
                ft.Row([
                    ft.ElevatedButton("💾 Salvar", on_click=handle_submit),
                    ft.ElevatedButton("📷 OCR de Imagem", on_click=lambda e: file_picker.pick_files(allow_multiple=False)),
                ]),
                upload_result,
                summary_label,
                tags_label,
            ],
            scroll="auto",
            spacing=20
        ),
        padding=20,
        expand=True
    )

    # ==== ABA 2 ====
    search_input = ft.TextField(label="🔍 Pesquisar", on_change=lambda e: atualizar_lista())
    notas_listview = ft.ListView(expand=True, spacing=10)

    def criar_on_click(note_id):
        return lambda e: show_note_details(note_id)

    def atualizar_lista():
        termo = search_input.value.strip().lower()
        notas = get_all_notes()

        notas_listview.controls.clear()
        for note_id, summary, tags, timestamp in notas:
            if termo and termo not in summary.lower() and termo not in tags.lower():
                continue
            notas_listview.controls.append(
                ft.Card(
                    content=ft.ListTile(
                        title=ft.Text(summary, overflow="ellipsis", max_lines=2),
                        subtitle=ft.Text(f"🏷 {tags}"),
                        trailing=ft.Text(timestamp[:10], size=12, italic=True),
                        on_click=criar_on_click(note_id),
                    )
                )
            )
        page.update()


    selected_note_container = ft.Container(padding=10)

    def show_note_details(note_id: int):
        note = get_note_by_id(note_id)
        if not note:
            selected_note_container.content = ft.Text("❌ Anotação não encontrada.", color="red")
            page.update()
            return

        content, summary, tags, timestamp = note

        selected_note_container.content = ft.Container(
            bgcolor=ft.Colors.BLUE_GREY_50,
            border_radius=10,
            padding=15,
            content=ft.Column([
                ft.Text(f"🗂 Anotação de {timestamp[:10]}", style="titleMedium", weight="bold"),
                ft.Divider(),
                ft.Text("🧠 Resumo:", weight="bold"),
                ft.Text(summary),
                ft.Divider(),
                ft.Text("📄 Conteúdo:", weight="bold"),
                ft.Text(content, selectable=True),
                ft.Divider(),
                ft.Text("🏷 Tags:", weight="bold"),
                ft.Text(tags, italic=True, color=ft.Colors.BLUE_GREY_700),
            ], spacing=10, scroll="auto")
        )

        page.update()

    aba_listagem = ft.Container(
        content=ft.Column([
            ft.Text("📚 Minhas Anotações", style="titleLarge"),
            search_input,
            ft.Divider(),
            ft.Container(content=notas_listview, height=350),
            ft.Divider(),
            ft.Text("🔎 Detalhes da Anotação", style="titleMedium"),
            selected_note_container,
        ], scroll="adaptive", spacing=15),
        padding=20,
        expand=True
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(text="✍️ Nova Anotação", content=aba_anotacao),
            ft.Tab(text="📁 Ver Anotações", content=aba_listagem),
        ]
    )

    page.add(tabs)
    atualizar_lista()

if __name__ == "__main__":
    init_db()
    ft.app(target=main)
