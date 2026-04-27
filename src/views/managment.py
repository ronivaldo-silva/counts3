
import flet as ft
from views.crud_registros import *
from views.crud_user import *

class Managment(ft.View):
    def __init__(self):
        super().__init__()
        self.route = "/managment"
        
        self.appbar = ft.AppBar(
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

        self.abas = ft.TabBar(
            indicator_color=ft.Colors.AMBER_300,
            tabs=[
                ft.Tab(label="Dividas", icon=ft.Icons.MONETIZATION_ON),
                ft.Tab(label="Usuários", icon=ft.Icons.GROUP),
            ],
        )

        self.abas_views = ft.TabBarView(
            margin=ft.Margin.all(10),
            expand=True,
            controls = [
                ft.Column([self.action_panel_mngmt, self.registros_table], expand=True),
                ft.Column([self.action_panel_users, self.users_table], expand=True)
            ],  
        )

        self.controls = [
            ft.Tabs(
                selected_index=0,
                length=2,
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
        self.action_panel_mngmt.btn_atualizar.on_click = self.atualizar_dividas
        self.action_panel_mngmt.new_divida_dialog.on_save = self.atualizar_dividas
        
        self.action_panel_users.search.on_submit = self.buscar_usuarios
        self.action_panel_users.btn_atualizar.on_click = self.atualizar_usuarios
        self.action_panel_users.new_user_dialog.on_save = self.atualizar_usuarios

    def buscar_dividas(self, e):
        query = self.action_panel_mngmt.search.value
        self.registros_table.atualizar_lista(query)

    def atualizar_dividas(self, e=None):
        self.action_panel_mngmt.search.value = ""
        self.action_panel_mngmt.search.update()
        self.registros_table.atualizar_lista()

    def buscar_usuarios(self, e):
        query = self.action_panel_users.search.value
        self.users_table.atualizar_lista(query)

    def atualizar_usuarios(self, e=None):
        self.action_panel_users.search.value = ""
        self.action_panel_users.search.update()
        self.users_table.atualizar_lista()

    async def logout(self, e):
        await self.page.push_route("/login")
