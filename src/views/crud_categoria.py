import flet as ft
from gears.db_control import DBControl
from models.db_models import Categoria

class ConfirmDialogCategoria(ft.AlertDialog):
    def __init__(self, categoria: Categoria, tipo_acao: str):
        super().__init__()
        self.data = categoria
        self.tipo_acao = tipo_acao
        self.on_confirm = None

        self.title_icon = self.__build_icon()
        self.title_text = self.__build_text()
        self.title = ft.Row(controls=[self.title_icon, self.title_text])

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(f'Nome: {self.data.categoria}'),
                ft.Text(f'Recorrente: {"Sim" if self.data.repete else "Não"}'),
            ]
        )

        self.btn_confirm = ft.IconButton(
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            icon_color=ft.Colors.GREEN_300,
            on_click=self._confirm,
        )

        self.btn_cancel = ft.IconButton(
            icon=ft.Icons.CANCEL_OUTLINED,
            icon_color=ft.Colors.RED_300,
            on_click=self._cancel
        )

        self.actions = [self.btn_cancel, self.btn_confirm]
        self.actions_alignment = ft.MainAxisAlignment.END

    def _confirm(self, e):
        if self.on_confirm:
            self.on_confirm()
        self.page.pop_dialog()

    def _cancel(self, e):
        self.page.pop_dialog()

    def __build_icon(self):
        if self.tipo_acao == "Excluir":
            return ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED_300)
        return ft.Icon(ft.Icons.HELP, color=ft.Colors.ORANGE_300)

    def __build_text(self):
        return ft.Text(f" Deseja {self.tipo_acao} ? ")


class FormCategoria(ft.AlertDialog):
    def __init__(self, id_categoria: int = None):
        super().__init__()
        self.id_categoria = id_categoria
        self.data = DBControl.get_categoria_por_id(id_categoria) if id_categoria else None
        self.on_save = None

        self.input_nome = ft.TextField(label="Nome da Categoria")
        self.switch_repete = ft.Switch(label="Recorrente (Mensal)", value=False, active_track_color=ft.Colors.BLUE_300)

        if self.data:
            self.input_nome.value = self.data.categoria
            self.switch_repete.value = self.data.repete

        if self.id_categoria:
            self.title = ft.Column(
                controls=[
                    ft.Row(controls=[ft.Icon(ft.Icons.CATEGORY, color=ft.Colors.BLUE_300), ft.Text("Alterar Categoria", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                ]
            )
        else:
            self.title = ft.Column(
                controls=[
                    ft.Row(controls=[ft.Icon(ft.Icons.CATEGORY_OUTLINED, color=ft.Colors.BLUE_300), ft.Text("Nova Categoria", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                ]
            )

        self.content = ft.Container(
            content=ft.Column(
                tight=True,
                controls=[
                    self.input_nome,
                    self.switch_repete,
                ]
            )
        )

        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
            ft.TextButton("Salvar", on_click=self.__save),
        ]

    def __save(self, e: ft.ControlEvent):
        nome = self.input_nome.value
        repete = self.switch_repete.value

        if not nome:
            self.page.show_dialog(
                ft.SnackBar(content=ft.Text("Por favor, informe o nome da categoria!"), bgcolor=ft.Colors.RED_700)
            )
            return

        if self.id_categoria:
            sucesso, msg = DBControl.atualizar_categoria(self.id_categoria, nome, repete)
        else:
            sucesso, msg = DBControl.criar_categoria(nome, repete)

        if sucesso and self.on_save:
            self.on_save()
            self.page.pop_dialog()

        self.page.show_dialog(
            ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700)
        )


class ActionPanelCategoria(ft.Container):
    def __init__(self):
        super().__init__()
        self.new_categoria_dialog = FormCategoria()

        self.btn_new = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Nova Categoria",
            on_click=self.show_dialog,
        )

        self.btn_atualizar = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Atualizar Categorias"
        )

        self.search = ft.SearchBar(
            bar_hint_text="Pesquisar",
            width=200,
            height=40,
            bar_bgcolor=ft.Colors.SURFACE_CONTAINER,
            tooltip="Nome da categoria"
        )

        self.dropdown_tipo = ft.Dropdown(
            label="Tipo",
            menu_height=300,
            options=[
                ft.DropdownOption(text="Todas", key="Todas"),
                ft.DropdownOption(text="Recorrentes", key="Recorrentes"),
                ft.DropdownOption(text="Avulsas", key="Avulsas"),
            ],
            value="Todas"
        )

        self.content = ft.Row(
            wrap=True,
            controls=[
                self.btn_new,
                self.btn_atualizar,
                self.search,
                self.dropdown_tipo
            ]
        )

    async def show_dialog(self, e):
        self.page.show_dialog(self.new_categoria_dialog)


class CardCategoria(ft.Card):
    def __init__(self, categoria: Categoria):
        super().__init__()
        self.data = categoria

        self.edit_dialog = FormCategoria(self.data.id)
        self.edit_dialog.on_save = self.auto_update

        self.delete_dialog = ConfirmDialogCategoria(self.data, "Excluir")
        self.delete_dialog.on_confirm = self.delete_categoria

        self.titulo = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True)
        self.info = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True, spacing=8)

        self.btn_delete = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, tooltip="Excluir", on_click=self.confirm_delete)
        self.btn_edit   = ft.IconButton(icon=ft.Icons.EDIT,   icon_color=ft.Colors.BLUE_300, tooltip="Editar", on_click=self.editar_categoria)

        self.__definir_valores(self.data)

        self.content = ft.Column(
            tight=True,
            spacing=4,
            controls=[
                ft.Container(
                    padding=ft.Padding.only(left=5, right=5, top=5, bottom=2),
                    content=ft.Column(
                        tight=True,
                        controls=[
                            self.titulo,
                            self.info,
                        ],
                    ),
                ),
                ft.Divider(height=1, thickness=0.5),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[self.btn_edit, self.btn_delete],
                ),
            ],
        )

    def __definir_valores(self, cat: Categoria):
        tipo_text = "Recorrente (Mensal)" if cat.repete else "Avulsa"
        tipo_color = ft.Colors.BLUE_300 if cat.repete else ft.Colors.GREEN_300
        tipo_icon = ft.Icons.AUTORENEW if cat.repete else ft.Icons.AUTO_FIX_HIGH

        self.titulo.controls = [
            ft.Text(cat.categoria, weight=ft.FontWeight.BOLD, size=14, selectable=True),
        ]
        
        estatisticas = DBControl.get_estatisticas_categoria(cat.id)

        self.info.controls = [
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, tipo_color),
                height=30,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(tipo_icon, size=14, color=tipo_color),
                        ft.Text(tipo_text, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ]
                )
            ),
        ]
        
        self.info.controls.append(
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.PURPLE_300),
                height=30,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.PEOPLE_ALT, size=14, color=ft.Colors.PURPLE_300),
                        ft.Text(f"{estatisticas['qtd_pessoas']} Pessoas", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ]
                )
            )
        )
        
        for type_id, soma in estatisticas['soma_cartoes'].items():
            if soma > 0:
                soma_str = f"R$ {soma:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.info.controls.append(
                    ft.Container(
                        bgcolor=ft.Colors.SURFACE_BRIGHT,
                        padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                        border_radius=ft.BorderRadius.all(8),
                        border=ft.Border.all(1, ft.Colors.ORANGE_300),
                        height=30,
                        content=ft.Row(
                            tight=True,
                            controls=[
                                ft.Icon(ft.Icons.CREDIT_CARD, size=14, color=ft.Colors.ORANGE_300),
                                ft.Text(f"{soma_str}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                            ]
                        )
                    )
                )

    async def editar_categoria(self, e):
        self.page.show_dialog(self.edit_dialog)

    async def confirm_delete(self, e):
        self.page.show_dialog(self.delete_dialog)

    def auto_update(self):
        self.data = DBControl.get_categoria_por_id(self.data.id)
        self.__definir_valores(self.data)
        self.update()

    def delete_categoria(self):
        sucesso, msg = DBControl.deletar_categoria(self.data.id)
        if sucesso:
            self.parent.controls.remove(self)
            self.parent.update()
        else:
            self.page.show_dialog(
                ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.RED_700)
            )


class TabCategorias(ft.Column):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.ALWAYS
        self.controls = self._carregar_categorias()

    def atualizar_lista(self, query: str = "", tipo: str = "Todas"):
        self.controls = self._carregar_categorias(query, tipo)
        self.update()

    def _carregar_categorias(self, query: str = "", tipo: str = "Todas") -> list:
        categorias = DBControl.get_all_categorias()

        if query:
            q = query.lower()
            categorias = [
                c for c in categorias
                if q in c.categoria.lower()
            ]

        if tipo != "Todas":
            if tipo == "Recorrentes":
                categorias = [c for c in categorias if c.repete]
            elif tipo == "Avulsas":
                categorias = [c for c in categorias if not c.repete]

        if not categorias:
            return [
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Nenhuma categoria encontrada.",
                        color=ft.Colors.GREY_500,
                        italic=True,
                    ),
                )
            ]
        return [CardCategoria(categoria=c) for c in categorias]
