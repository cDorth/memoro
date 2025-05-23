import flet as ft
import os
import sqlite3
from datetime import datetime
from ia import summarize_text, extract_tags, ocr_image, current_timestamp
import shutil
from typing import List
from functools import partial
from ia import generate_embedding
from embeddings import buscar_semanticamente
from db import save_note,get_notes_grouped_by_day
from db import ensure_embedding_column_exists

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

def adicionar_coluna_embedding():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE notes ADD COLUMN embedding TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            raise
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

def update_note(note_id: int, new_content: str, new_summary: str, new_tags: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE notes SET content = ?, summary = ?, tags = ? WHERE id = ?",
              (new_content, new_summary, new_tags, note_id))
    conn.commit()
    conn.close()

def delete_note(note_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()



def main(page: ft.Page):
    page.title = "🧠 Memoro – Memória Artificial Pessoal"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 750
    page.window_height = 800
    page.padding = 20
    page.scroll = "adaptive"

    upload_result = ft.Text(value="", style="bodySmall", color="green")

    def abrir_dialogo(dlg: ft.AlertDialog):
        if dlg not in page.overlay:
            page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def show_dialog(title: str, message: str):
        dialog = ft.AlertDialog(
            title=ft.Text(title, weight="bold"),
            content=ft.Text(message),
            actions=[ft.TextButton("Fechar", on_click=lambda e: fechar_dialog(dialog))],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def fechar_dialog(dialog):
        dialog.open = False
        page.update()

    def abrir_edicao(note_id: int, e=None):
        print(f"Tentando abrir edição para nota {note_id}")  # Debug
        note = get_note_by_id(note_id)
        if not note:
            show_dialog("Erro", "Anotação não encontrada para edição.")
            return

        content, summary, tags, _ = note

        content_field = ft.TextField(
            value=content, 
            multiline=True, 
            expand=True,
            min_lines=10,
            max_lines=20,
            border="outline",
            label="Conteúdo"
        )
        tags_field = ft.TextField(
            value=tags, 
            label="Tags (separadas por vírgula)",
            border="outline",
            helper_text="Ex: trabalho, ideias, pessoal"
        )

        def salvar_edicao(e):
            novo_conteudo = content_field.value.strip()
            novas_tags = tags_field.value.strip()
            
            if not novo_conteudo:
                show_dialog("Erro", "O conteúdo não pode estar vazio.")
                return
                
            try:
                novo_resumo = summarize_text(novo_conteudo)
                update_note(note_id, novo_conteudo, novo_resumo, novas_tags)
                dlg.open = False
                page.update()
                show_note_details(note_id)
                atualizar_lista()
                show_dialog("Sucesso", "Anotação atualizada com sucesso!")
            except Exception as err:
                show_dialog("Erro", f"Não foi possível atualizar: {str(err)}")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("✏️ Editar Anotação", style=ft.TextStyle(size=20, weight="bold")),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Edite o conteúdo e as tags abaixo:", style="bodyMedium", color=ft.Colors.BLUE_GREY_700),
                    ft.Container(height=10),
                    content_field,
                    ft.Container(height=10),
                    tags_field
                ], spacing=10),
                width=650,
                height=450,
                padding=ft.padding.all(10)
            ),
            actions=[
                ft.TextButton(
                    "❌ Cancelar", 
                    on_click=lambda e: fechar_dialog(dlg),
                    style=ft.ButtonStyle(color=ft.Colors.RED_400)
                ),
                ft.ElevatedButton(
                    "💾 Salvar Alterações", 
                    on_click=salvar_edicao,
                    icon=ft.Icons.SAVE,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_400)
                )
            ],
            actions_alignment="spaceBetween"
        )
        
        abrir_dialogo(dlg)
        print("Dialog de edição deveria estar aberto agora")  # Debug

    def confirmar_exclusao(note_id: int, e=None):
        print(f"Tentando abrir confirmação de exclusão para nota {note_id}")  # Debug
        
        def deletar(e):
            try:
                delete_note(note_id)
                dlg.open = False
                page.update()
                atualizar_lista()
                selected_note_container.content = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=50),
                        ft.Text("✅ Anotação excluída com sucesso!", 
                               style="titleMedium", 
                               color=ft.Colors.GREEN_600,
                               text_align="center")
                    ], alignment="center", horizontal_alignment="center", spacing=15),
                    padding=30,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.GREEN_50,
                    border_radius=10
                )
                page.update()
            except Exception as err:
                show_dialog("Erro", f"Não foi possível excluir: {str(err)}")

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Exclusão", style=ft.TextStyle(size=20, weight="bold", color=ft.Colors.RED_600)),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED_600, size=60),
                    ft.Container(height=10),
                    ft.Text("Tem certeza que deseja excluir esta anotação permanentemente?", 
                           style="bodyLarge", 
                           text_align="center",
                           color=ft.Colors.BLACK,
                           weight="w500"),
                    ft.Container(height=5),
                    ft.Text("Esta ação não pode ser desfeita!", 
                           style="bodySmall", 
                           text_align="center",
                           color=ft.Colors.BLACK87,
                           italic=True)
                ], spacing=10, horizontal_alignment="center"),
                width=400,
                height=250,
                padding=ft.padding.all(20)
            ),
            actions=[
                ft.TextButton(
                    "❌ Cancelar", 
                    on_click=lambda e: fechar_dialog(dlg),
                    style=ft.ButtonStyle(color=ft.Colors.BLUE_600)
                ),
                ft.ElevatedButton(
                    " Excluir Permanentemente", 
                    on_click=deletar, 
                    icon=ft.Icons.DELETE_FOREVER,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
                )
            ],
            actions_alignment="spaceBetween"
        )
        
        abrir_dialogo(dlg)
        print("Dialog de exclusão deveria estar aberto agora")  # Debug

    def exportar_anotacao(note_id: int):
        note = get_note_by_id(note_id)
        if not note:
            show_dialog("Erro", "Anotação não encontrada.")
            return

        content, summary, tags, timestamp = note
        filename = f"memoro_{note_id}_{timestamp[:10]}.txt"
        export_dir = "export"
        os.makedirs(export_dir, exist_ok=True)
        path = os.path.join(export_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"🗂 Anotação de {timestamp}\n\n")
            f.write(f"🧠 Resumo:\n{summary}\n\n")
            f.write(f"📄 Conteúdo:\n{content}\n\n")
            f.write(f"🏷 Tags: {tags}\n")

        show_dialog("Exportado", f"Arquivo salvo em:\n{path}")

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

            embedding = generate_embedding(content)
            save_note(content, summary, tags, embedding)

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
    selected_note_container = ft.Container(padding=10)

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
    from db import get_notes_grouped_by_day  # certifique-se de importar isso no topo se ainda não tiver

    timeline_column = ft.Column(scroll="auto", spacing=20)

    def atualizar_timeline():
        timeline_column.controls.clear()
        grouped_notes = get_notes_grouped_by_day()

        for data, notas in grouped_notes.items():
            timeline_column.controls.append(
                ft.Text(f"📅 {data}", style="titleMedium", weight="bold")
            )
            for note_id, summary, tags, timestamp in notas:
                timeline_column.controls.append(
                    ft.Card(
                        content=ft.ListTile(
                            title=ft.Text(summary),
                            subtitle=ft.Text(f"🏷 {tags}"),
                            trailing=ft.Text(timestamp[11:16]),
                            on_click=lambda e, nid=note_id: show_note_details(nid)
                        )
                    )
                )
        page.update()

    aba_timeline = ft.Container(
        content=timeline_column,
        padding=20,
        expand=True
    )
    
    # ==== ABA 2 ====
    search_input = ft.TextField(label="🔍 Pesquisar", on_change=lambda e: atualizar_lista())
    notas_listview = ft.ListView(expand=True, spacing=10)

    def atualizar_lista():
        termo = search_input.value.strip().lower()
        if termo:
            nota_ids = buscar_semanticamente(termo)
            todas = get_all_notes()
            notas = [n for n in todas if n[0] in nota_ids]
        else:
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
                        on_click=partial(show_note_details, note_id),
                    )
                )
            )
        page.update()

    selected_note_container = ft.Container(padding=10)

    def show_note_details(note_id: int, e=None):
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
                ft.Divider(),
                ft.Row([
                    ft.ElevatedButton(
                        " Editar ", 
                        on_click=lambda e, note_id=note_id: abrir_edicao(note_id),
                        icon=ft.Icons.EDIT,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_50)
                    ),
                    ft.ElevatedButton(
                        " Excluir ", 
                        on_click=lambda e, note_id=note_id: confirmar_exclusao(note_id),
                        icon=ft.Icons.DELETE,
                        style=ft.ButtonStyle(color=ft.Colors.RED_600)
                    ),
                    ft.TextButton(
                        " Exportar ", 
                        on_click=lambda e, note_id=note_id: exportar_anotacao(note_id),
                        icon=ft.Icons.DOWNLOAD
                    ),
                ], spacing=10)
            ], spacing=10)
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
            ft.Tab(text="🗓 Timeline", content=aba_timeline),
        ]
    )




    page.add(tabs)
    atualizar_lista()
    atualizar_timeline()

if __name__ == "__main__":
    init_db()
    ensure_embedding_column_exists()
    adicionar_coluna_embedding()

    ft.app(target=main)