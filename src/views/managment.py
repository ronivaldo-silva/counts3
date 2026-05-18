import flet as ft
from views.crud_registros import *
from views.crud_user import *
from views.crud_categoria import *

class Managment(ft.View):
    def __init__(self):
        super().__init__()
        self.route = "/managment"
        
        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS),
            leading_width=40,
            title=ft.Text("Gerenciamento"),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            actions_padding=ft.Padding.only(right=20),
            actions=[
                ft.IconButton(ft.Icons.LOGOUT, on_click=self.logout),
            ]
        )

        self.action_panel_mngmt = ActionPanel()
        self.registros_table = TabRegistros()

        self.action_panel_users = ActionPanelUser()
        self.users_table = TabUsuarios()

        self.action_panel_categorias = ActionPanelCategoria()
        self.categorias_table = TabCategorias()

        self.abas = ft.TabBar(
            indicator_color=ft.Colors.AMBER_300,
            tabs=[
                ft.Tab(label="Dividas", icon=ft.Icons.MONETIZATION_ON),
                ft.Tab(label="Usuários", icon=ft.Icons.GROUP),
                ft.Tab(label="Categorias", icon=ft.Icons.CATEGORY),
            ],
        )

        self.abas_views = ft.TabBarView(
            margin=ft.Margin.all(10),
            expand=True,
            controls = [
                ft.Column([self.action_panel_mngmt, self.registros_table], expand=True, margin=ft.Margin.only(top=20)),
                ft.Column([self.action_panel_users, self.users_table], expand=True, margin=ft.Margin.only(top=20)),
                ft.Column([self.action_panel_categorias, self.categorias_table], expand=True, margin=ft.Margin.only(top=20))
            ],  
        )

        self.controls = [
            ft.Tabs(
                selected_index=0,
                length=3,
                align=ft.Alignment.TOP_CENTER,
                expand=True,
                content=ft.Column(
                    width=800,
                    controls=[
                        self.abas,
                        self.abas_views
                    ]
                )
            )
        ]

        # Configura os eventos de busca e atualização
        self.action_panel_mngmt.search.on_submit = self.buscar_dividas
        self.action_panel_mngmt.dropdown_categoria.on_select = self.buscar_dividas
        self.action_panel_mngmt.dropdown_classificacao.on_select = self.buscar_dividas
        self.action_panel_mngmt.btn_atualizar.on_click = self.atualizar_dividas
        self.action_panel_mngmt.new_divida_dialog.on_save = self.atualizar_dividas
        
        self.action_panel_users.search.on_submit = self.buscar_usuarios
        self.action_panel_users.dropdown_status.on_select = self.buscar_usuarios
        self.action_panel_users.btn_atualizar.on_click = self.atualizar_usuarios
        self.action_panel_users.new_user_dialog.on_save = self.atualizar_usuarios

        self.action_panel_categorias.search.on_submit = self.buscar_categorias
        self.action_panel_categorias.dropdown_tipo.on_select = self.buscar_categorias
        self.action_panel_categorias.btn_atualizar.on_click = self.atualizar_categorias
        self.action_panel_categorias.new_categoria_dialog.on_save = self.atualizar_categorias

    def buscar_dividas(self, e):
        query = self.action_panel_mngmt.search.value
        categoria = self.action_panel_mngmt.dropdown_categoria.value
        classificacao = self.action_panel_mngmt.dropdown_classificacao.value
        self.registros_table.atualizar_lista(query, categoria, classificacao)

    def atualizar_dividas(self, e=None):
        self.action_panel_mngmt.search.value = ""
        self.action_panel_mngmt.search.update()
        self.action_panel_mngmt.dropdown_categoria.value = "Todas"
        self.action_panel_mngmt.dropdown_categoria.update()
        self.action_panel_mngmt.dropdown_classificacao.value = "Todas"
        self.action_panel_mngmt.dropdown_classificacao.update()
        self.registros_table.atualizar_lista()

    def buscar_usuarios(self, e):
        query = self.action_panel_users.search.value
        status = self.action_panel_users.dropdown_status.value
        self.users_table.atualizar_lista(query, status)

    def atualizar_usuarios(self, e=None):
        self.action_panel_users.search.value = ""
        self.action_panel_users.search.update()
        self.action_panel_users.dropdown_status.value = "Todos"
        self.action_panel_users.dropdown_status.update()
        self.users_table.atualizar_lista()

    def buscar_categorias(self, e):
        query = self.action_panel_categorias.search.value
        tipo = self.action_panel_categorias.dropdown_tipo.value
        self.categorias_table.atualizar_lista(query, tipo)

    def atualizar_categorias(self, e=None):
        self.action_panel_categorias.search.value = ""
        self.action_panel_categorias.search.update()
        self.action_panel_categorias.dropdown_tipo.value = "Todas"
        self.action_panel_categorias.dropdown_tipo.update()
        self.categorias_table.atualizar_lista()

    async def logout(self, e):
        self.page.session.store.clear()
        await ft.SharedPreferences().remove("user_cpf")
        await self.page.push_route("/login")
