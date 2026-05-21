import flet as ft

card_titulo = ft.Row(
    alignment=ft.MainAxisAlignment.START,
    controls=[
        ft.Icon(ft.Icons.PEOPLE_ALT, color=ft.Colors.BLUE_300),
        ft.Text("Titulo"),
    ],
)

card_corpo = ft.Row(
    alignment=ft.MainAxisAlignment.CENTER,
    controls=[
        ft.Text("Conteudo expressivo do cartão"),
    ],
)

card_botoes = ft.Row(
    alignment=ft.MainAxisAlignment.END,
    controls=[
        ft.IconButton(ft.Icons.EDIT, tooltip="Editar"),
        ft.IconButton(ft.Icons.CANCEL, tooltip="Cancelar"),
    ],
)

cartao = ft.Card(
    width=400,
    content=ft.Column(
        controls=[
            card_titulo,
            ft.Divider(thickness=0.5),
            card_corpo,
            card_botoes,
        ]
    )
)

dialog = ft.AlertDialog(
    title=ft.Text("Titulo"),
    content=ft.Text("Conteudo"),
    actions=[
        ft.TextButton("Cancelar", on_click=lambda e: e.control.page.pop_dialog()),
        ft.TextButton("Salvar", on_click=lambda e: e.control.page.pop_dialog()),
    ],
)

def main(page: ft.Page):
    page.window.width = 800
    
    cards = ft.Column(
        tight=True,
        width=400,
        scroll=ft.ScrollMode.ALWAYS,
        controls=[
            cartao
            for i in range(1000)
        ]
    )

    page.add(
        ft.SafeArea(
            align=ft.Alignment.CENTER,
            content=cards
        )
    )

ft.app(main)