import flet as ft
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2:5.3b"

def main(page: ft.Page):
    page.title = "Chat con IA – Parte 2"
    page.bgcolor = ft.Colors.GREY_100

    mensajes = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
    prompt = ft.TextField(label="Escribe tu mensaje...", expand=True, multiline=True, min_lines=1, max_lines=4)

    def burbuja(texto, es_usuario):
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(
                        texto,
                        color=ft.Colors.WHITE if es_usuario else ft.Colors.BLACK,
                        size=15,
                        selectable=True,
                    ),
                    bgcolor=ft.Colors.BLUE_400 if es_usuario else ft.Colors.GREY_300,
                    padding=12,
                    border_radius=30,
                    width=350,
                )
            ],
            alignment=ft.MainAxisAlignment.END if es_usuario else ft.MainAxisAlignment.START,
        )

    def enviar_click_streaming(e):
        texto = prompt.value.strip()
        if not texto:
            return
        mensajes.controls.append(burbuja(texto, es_usuario=True))
        page.update()
        prompt.value = ""
        page.update()

        live_text = ft.Text("", color=ft.Colors.BLACK, size=15, selectable=True)
        cont = ft.Row(
            [
                ft.Container(content=live_text, bgcolor=ft.Colors.GREY_300, padding=12, border_radius=30, width=350)
            ],
            alignment=ft.MainAxisAlignment.START
        )
        mensajes.controls.append(cont)
        page.update()

        try:
            r = requests.post(
                OLLAMA_URL,
                json={"model": MODEL, "prompt": texto, "stream": True},
                stream=True,
                timeout=300,
            )
            r.raise_for_status()
            completo = ""
            for line in r.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if "response" in data:
                    completo += data["response"]
                    live_text.value = completo
                    page.update()
        except Exception as ex:
            live_text.value = f"Error: {ex}"
            page.update()

    def limpiar_chat(e):
        mensajes.controls.clear()
        page.update()

    boton_enviar = ft.ElevatedButton("Enviar", on_click=enviar_click_streaming, bgcolor=ft.Colors.BLUE_400, color=ft.Colors.WHITE)
    prompt.on_submit = enviar_click_streaming

    page.add(
        ft.Column(
            [
                ft.Row([ft.TextButton("🧹 Limpiar chat", on_click=limpiar_chat)], alignment=ft.MainAxisAlignment.START),
                mensajes,
                ft.Row([prompt, boton_enviar], vertical_alignment=ft.CrossAxisAlignment.END),
            ],
            expand=True
        )
    )

ft.app(target=main)
