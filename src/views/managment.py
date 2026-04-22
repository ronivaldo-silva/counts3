import flet as ft
from gears.db_control import DBControl
from database.models import Registro, Usuario

class FormNewDebito(ft.Container):
    def __init__(self):
        super().__init__()
        # Buscar todos os usuários
        self.usuarios: list[Usuario] = DBControl.get_all_usuarios()
        self.cpf_field = ft.SearchBar(controls=[ft.ListTile(text=usuario.cpf) for usuario in self.usuarios])

        self.content = ft.Column(
            controls=[
                ft.Text("Nova Dívida"),
            ]
        )

class ActionPanel(ft.Container):
    def __init__(self):
        super().__init__()

        self.btn_new = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Nova Dívida"
        )

        self.btn_atualizar = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Atualizar Dívidas"
        )

        self.search = ft.SearchBar(
            bar_hint_text="Pesquisar", 
            width=200, 
            height=40, 
            bar_bgcolor=ft.Colors.SURFACE_CONTAINER, 
            tooltip="CPF ou Nome"
        )
        
        self.content = ft.Row(
            wrap=True,
            controls=[
                self.btn_new,
                self.btn_atualizar,
                self.search
            ]
        )

class Dividas(ft.Card):
    """Cartão que exibe os dados de um Registro (dívida) com seu usuário relacionado."""

    def __init__(self, registro: Registro):
        super().__init__()
        self.registro = registro

        # --- Dados vindos dos relacionamentos carregados ---
        cpf       = registro.usuario.cpf
        nome      = registro.usuario.nome
        valor     = f"R$ {registro.valor:,.2f}"
        saldo     = f"R$ {registro.saldo:,.2f}"
        categoria = registro.categoria_rel.categoria
        status    = registro.classificacao_rel.classificacao
        # Formata vencimento
        if registro.data_debito:
            vencimento = registro.data_debito.strftime("%d/%m/%Y")
        elif registro.data_prevista:
            vencimento = registro.data_prevista.strftime("%d/%m/%Y")
        else:
            vencimento = "N/A"

        # --- Linha 1: Nome | CPF | Categoria---
        self.titulo = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            wrap=True,
            controls=[
                ft.Text(nome, weight=ft.FontWeight.BOLD, size=14, selectable=True),
                ft.Text("|", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
                ft.Text(cpf, size=12, color=ft.Colors.BLUE_300, selectable=True),
                ft.Text("|", color=ft.Colors.ORANGE_300, weight=ft.FontWeight.BOLD),
                ft.Text(categoria, size=12, color=ft.Colors.ORANGE_300, selectable=True),
            ],
        )

        # --- Linha 2: Valor - Saldo - Vencimento ---
        self.info = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            wrap=True,
            spacing=8,
            controls=[
                ft.Chip(
                    label=ft.Text(valor, size=11),
                    leading=ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=ft.Colors.GREEN_400),
                    bgcolor=ft.Colors.GREEN_100,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                ),
                ft.Chip(
                    label=ft.Text(f"Saldo: {saldo}", size=11),
                    leading=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=14, color=ft.Colors.BLUE_400),
                    bgcolor=ft.Colors.BLUE_100,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                ),
                ft.Chip(
                    label=ft.Text(vencimento, size=11),
                    leading=ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=ft.Colors.ORANGE_400),
                    bgcolor=ft.Colors.ORANGE_100,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                ),
                ft.Chip(
                    label=ft.Text(status, size=11),
                    bgcolor=ft.Colors.GREY_200,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                ),
            ],
        )

        # --- Linha 3: Botões ---
        self.btn_delete = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, tooltip="Excluir")
        self.btn_edit   = ft.IconButton(icon=ft.Icons.EDIT,   icon_color=ft.Colors.BLUE_300, tooltip="Editar")
        self.btn_quitar = ft.IconButton(icon=ft.Icons.MONEY, icon_color=ft.Colors.GREEN_300, tooltip="Quitar")

        self.content = ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    padding=ft.Padding.only(left=5, right=5, top=5, bottom=2),
                    content=ft.Column(
                        controls=[
                            self.titulo,
                            self.info,
                        ],
                    ),
                ),
                ft.Divider(height=1, thickness=0.5),
                ft.Row(
                    controls=[self.btn_quitar, self.btn_edit, self.btn_delete],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        )

class TableDividas(ft.Column):
    """Coluna com scroll que lista todas as dívidas (Registros) do banco."""

    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.controls = self._carregar_dividas()

    def atualizar_lista(self, query: str = ""):
        self.controls = self._carregar_dividas(query)
        self.update()

    def _carregar_dividas(self, query: str = "") -> list:
        """Busca todos os Registros no banco e retorna uma lista de cartões Dividas."""
        registros: list[Registro] = DBControl.get_todos_registros()
        
        if query:
            q = query.lower()
            registros = [
                reg for reg in registros 
                if q in reg.usuario.nome.lower() or q in reg.usuario.cpf.lower()
            ]

        if not registros:
            return [
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Nenhuma dívida encontrada.",
                        color=ft.Colors.GREY_500,
                        italic=True,
                    ),
                )
            ]
        return [Dividas(registro=reg) for reg in registros]

class Managment(ft.View):
    def __init__(self):
        super().__init__()
        self.route = "/managment"
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.theme_mode = ft.ThemeMode.LIGHT
        
        self.action_panel = ActionPanel()
        self.dividas_table = TableDividas()

        self.appbar = ft.AppBar(
            title=ft.Text("Gerenciamento"),
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.Icons.LOGOUT),
            ]
        )
        
        self.abas = ft.TabBar(
            tabs=[
                ft.Tab(label="Dividas", icon=ft.Icons.MONETIZATION_ON),
            ],
        )

        self.abas_views = ft.TabBarView(
            expand=True,
            controls = [self.dividas_table],  
        )

        self.controls = [
            ft.Tabs(
                selected_index=0,
                length=1,
                expand=True,
                content=ft.Column(
                    width=800,
                    controls=[
                        self.abas,
                        self.action_panel,
                        self.abas_views
                    ]
                )
            )
        ]

        # Configura os eventos de busca e atualização
        self.action_panel.search.on_submit = self.buscar_dividas
        self.action_panel.btn_atualizar.on_click = self.atualizar_dividas

    def buscar_dividas(self, e):
        query = self.action_panel.search.value
        self.dividas_table.atualizar_lista(query)

    def atualizar_dividas(self, e):
        self.action_panel.search.value = ""
        self.action_panel.search.update()
        self.dividas_table.atualizar_lista()
