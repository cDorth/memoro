import flet as ft
import os
import sqlite3
from datetime import datetime
from ia import summarize_text, extract_tags, ocr_image, current_timestamp
import shutil

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

def main(page: ft.Page):
    page.title = "Memoro - Dia 2: Adição de Conteúdo"
    page.padding = 20
    page.window_width = 600
    page.window_height = 700

    # Componentes da UI
    text_field = ft.TextField(label="Nova anotação", multiline=True, expand=True)
    summary_label = ft.Text(value="", selectable=True, style="bodyLarge")
    tags_label = ft.Text(value="", selectable=True, style="bodyMedium")
    upload_result = ft.Text(value="", style="bodySmall", color="green")

    def show_dialog(title: str, message: str):
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: setattr(dlg, "open", False))]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def handle_submit(e):
        content = text_field.value.strip()
        if not content:
            show_dialog("Erro", "Digite algo para salvar.")
            return

        try:
            summary = summarize_text(content)
            tags = extract_tags(content)

            save_note(content, summary, tags)

            summary_label.value = "Resumo:\n" + summary
            tags_label.value = "Tópicos/Tags:\n" + ", ".join(tags)
            upload_result.value = "Anotação salva com sucesso!"
            text_field.value = ""
        except Exception as err:
            upload_result.value = f"Erro ao processar IA: {err}"

        page.update()

    def handle_upload(e):
        if not file_picker.result or not file_picker.result.files:
            return

        file = file_picker.result.files[0]
        original_path = file.path

        if not original_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
            upload_result.value = "Formato de imagem não suportado."
            page.update()
            return

        temp_path = f"temp_{file.name}"
        shutil.copy(original_path, temp_path)

        try:
            extracted_text = ocr_image(temp_path)
            text_field.value = extracted_text
            upload_result.value = "Texto extraído com sucesso da imagem."
        except Exception as err:
            upload_result.value = f"Erro ao processar a imagem: {err}"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        page.update()

    file_picker = ft.FilePicker(on_result=handle_upload)
    page.overlay.append(file_picker)

    page.add(
        ft.Text("Digite ou cole sua anotação:", style="headlineMedium"),
        text_field,
        ft.ElevatedButton("Salvar Anotação", on_click=handle_submit),
        ft.ElevatedButton("Carregar imagem para OCR", on_click=lambda e: file_picker.pick_files(allow_multiple=False)),
        upload_result,
        summary_label,
        tags_label,
    )

if __name__ == "__main__":
    init_db()
    ft.app(target=main)
