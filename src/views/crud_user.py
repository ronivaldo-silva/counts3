import flet as ft
from gears.db_control import DBControl
from models.db_models import Usuario

class ConfirmDialogUser(ft.AlertDialog):
    def __init__(self, usuario: Usuario, tipo_acao: str):
        super().__init__()
        # 1. Definir os parâmetros das classes primeiro
        self.data = usuario
        self.tipo_acao = tipo_acao
        self.on_confirm = None

        # 2. Construir as estruturas de layout depois
        self.title_icon = self.__build_icon()
        self.title_text = self.__build_text()
        self.title = ft.Row(controls=[self.title_icon, self.title_text])

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(f'CPF: {self.data.cpf}'),
                ft.Text(f'Nome: {self.data.nome}'),
            ]
        )

        # 3. Inserir os controles de exibição depois
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
        self.actions_margin = ft.Margin.only(left=5, right=5)

    # 4. Funções importantes no final
    def _confirm(self, e):
        if self.on_confirm:
            self.on_confirm()
        self.page.pop_dialog()

    def _cancel(self, e):
        self.page.pop_dialog()
    
    def __build_icon(self):
        if self.tipo_acao == "Excluir":
            return ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED_300)
        elif self.tipo_acao == "Ativar/Inativar":
            return ft.Icon(ft.Icons.POWER_SETTINGS_NEW, color=ft.Colors.ORANGE_300)

    def __build_text(self):
        return ft.Text(f" Deseja {self.tipo_acao} ? ")


class FormUser(ft.AlertDialog):
    def __init__(self, id_usuario: int = None):
        super().__init__()
        # 1. Definir os parâmetros das classes primeiro
        self.id_usuario = id_usuario
        self.data = DBControl.get_usuario_por_id(id_usuario) if id_usuario else None
        self.on_save = None

        # 2. Construir as estruturas de layout depois / Inserir os controles de exibição
        self.input_cpf = ft.TextField(label="CPF", keyboard_type=ft.KeyboardType.NUMBER, max_length=11)
        self.input_nome = ft.TextField(label="Nome")
        self.input_senha = ft.TextField(label="Senha", password=True, can_reveal_password=True)
        
        self.switch_admin = ft.Switch(label="Administrador", value=False, active_track_color=ft.Colors.BLUE_300)
        self.switch_ativo = ft.Switch(label="Ativo", value=True, active_track_color=ft.Colors.GREEN_300)

        if self.data:
            self.input_cpf.value = self.data.cpf
            self.input_nome.value = self.data.nome
            self.input_senha.value = self.data.senha
            self.switch_admin.value = self.data.is_admin
            self.switch_ativo.value = self.data.actived

        if self.id_usuario: # UPDATE
            self.title = ft.Column(
                controls=[
                    ft.Row(controls=[ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_300), ft.Text("Alterar Usuário", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                ]
            )
        else: # CREATE
            self.title = ft.Column(
                controls=[
                    ft.Row(controls=[ft.Icon(ft.Icons.PERSON_ADD, color=ft.Colors.BLUE_300), ft.Text("Novo Usuário", size=16, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                ]
            )
        
        self.content = ft.Container(
            content=ft.Column(
                tight=True,
                controls=[
                    self.input_cpf,
                    self.input_nome,
                    self.input_senha,
                    self.switch_admin,
                    self.switch_ativo
                ]
            )
        )

        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
            ft.TextButton("Salvar", on_click=self.__save),
        ]

    # 4. Funções importantes no final
    def __save(self, e: ft.ControlEvent):
        cpf = self.input_cpf.value
        nome = self.input_nome.value
        senha = self.input_senha.value
        is_admin = self.switch_admin.value
        actived = self.switch_ativo.value

        if not cpf or not nome:
            self.page.show_dialog(
                ft.SnackBar(content=ft.Text("Por favor, preencha CPF e Nome!"), bgcolor=ft.Colors.RED_700)
            )
            return

        if self.id_usuario:
            sucesso, msg = DBControl.atualizar_usuario(self.id_usuario, cpf, nome, senha, is_admin, actived)
        else:
            sucesso, msg = DBControl.criar_usuario_completo(cpf, nome, senha, is_admin, actived)

        if sucesso and self.on_save:
            self.on_save()
            self.page.pop_dialog()

        self.page.show_dialog(
            ft.SnackBar(content=ft.Text(msg), bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700)
        )


class ActionPanelUser(ft.Container):
    def __init__(self):
        super().__init__()
        # 1. Definir os parâmetros das classes primeiro
        self.new_user_dialog = FormUser()

        # 2 & 3. Construir as estruturas de layout depois / Inserir os controles de exibição
        self.btn_new = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Novo Usuário",
            on_click=self.show_dialog,
        )

        self.btn_atualizar = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Atualizar Usuários"
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
        
    # 4. Funções importantes no final
    async def show_dialog(self, e):
        self.page.show_dialog(self.new_user_dialog)


class CardUser(ft.Card):
    def __init__(self, usuario: Usuario):
        super().__init__()
        # 1. Definir os parâmetros das classes primeiro
        self.data = usuario

        self.edit_user_dialog = FormUser(self.data.id)
        self.edit_user_dialog.on_save = self.auto_update

        self.delete_dialog = ConfirmDialogUser(self.data, "Excluir")
        self.delete_dialog.on_confirm = self.delete_user

        # 2. Construir as estruturas de layout depois
        self.titulo = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True)
        self.info = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True, spacing=8)

        # 3. Inserir os controles de exibição depois
        self.btn_delete = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, tooltip="Excluir", on_click=self.confirm_delete)
        self.btn_edit   = ft.IconButton(icon=ft.Icons.EDIT,   icon_color=ft.Colors.BLUE_300, tooltip="Editar", on_click=self.editar_user)

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

    # 4. Funções importantes no final
    def __definir_valores(self, usuario: Usuario):
        nome = usuario.nome
        cpf = usuario.cpf
        admin_text = "Admin" if usuario.is_admin else "Padrão"
        status_text = "Ativo" if usuario.actived else "Inativo"
        
        status_color = ft.Colors.GREEN_300 if usuario.actived else ft.Colors.RED_300
        admin_color = ft.Colors.BLUE_300 if usuario.is_admin else ft.Colors.GREY_400

        total, data_antiga = DBControl.get_estatisticas_dividas_usuario(usuario.id)
        total_text = f"R$ {total:,.2f}"
        data_text = data_antiga.strftime("%d/%m/%Y") if data_antiga else "N/A"

        self.titulo.controls = [
            ft.Text(nome, weight=ft.FontWeight.BOLD, size=14, selectable=True),
            ft.Text("|", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
            ft.Text(cpf, size=12, color=ft.Colors.BLUE_300, selectable=True),
        ]

        self.info.controls = [
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, admin_color),
                height=30,
                content=ft.Row(
                    tight=True,
                    controls= [
                        ft.Icon(ft.Icons.SECURITY, size=14, color=admin_color),
                        ft.Text(admin_text, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ],
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, status_color),
                height=30,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.POWER_SETTINGS_NEW, size=14, color=status_color),
                        ft.Text(status_text, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ]
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.RED_300),
                height=30,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.MONEY_OFF, size=14, color=ft.Colors.RED_300),
                        ft.Text(total_text, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ]
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.ORANGE_300),
                height=30,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.WARNING_AMBER, size=14, color=ft.Colors.ORANGE_300),
                        ft.Text(f"Antiga: {data_text}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ]
                )
            ),
        ]

    async def editar_user(self, e):
        self.page.show_dialog(self.edit_user_dialog)
    
    async def confirm_delete(self, e):
        self.page.show_dialog(self.delete_dialog)

    def auto_update(self):
        self.data = DBControl.get_usuario_por_id(self.data.id)
        self.__definir_valores(self.data)
        self.update()

    def delete_user(self):
        DBControl.deletar_usuario(self.data.id)
        self.parent.controls.remove(self)
        self.parent.update()
    
    def toggle_status(self):
        DBControl.toggle_status_usuario(self.data.id)
        self.auto_update()


class TabUsuarios(ft.Column):
    def __init__(self):
        super().__init__()
        # 1. Definir os parâmetros das classes primeiro
        self.expand = True
        self.scroll = ft.ScrollMode.ALWAYS
        # 2 & 3. Construir as estruturas de layout depois / Inserir os controles de exibição
        self.controls = self._carregar_usuarios()

    # 4. Funções importantes no final
    def atualizar_lista(self, query: str = ""):
        self.controls = self._carregar_usuarios(query)
        self.update()

    def _carregar_usuarios(self, query: str = "") -> list:
        usuarios = DBControl.get_all_usuarios()
        
        if query:
            q = query.lower()
            usuarios = [
                u for u in usuarios 
                if q in u.nome.lower() or q in u.cpf.lower()
            ]

        if not usuarios:
            return [
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Nenhum usuário encontrado.",
                        color=ft.Colors.GREY_500,
                        italic=True,
                    ),
                )
            ]
        return [CardUser(usuario=u) for u in usuarios]
