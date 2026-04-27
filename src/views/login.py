import flet as ft
import asyncio
from gears.db_control import DBControl

class Dialog_NewPass(ft.AlertDialog):
    def __init__(self, cpf: str, page: ft.Page, on_success=None):
        super().__init__()
        self.cpf = cpf
        self.page_ref = page
        self.on_success = on_success
        
        self.title = ft.Text("Cadastrar Nova Senha")
        self.modal = True
        
        self.txt_cpf = ft.TextField(
            label="CPF",
            value=self.cpf,
            disabled=True,
            width=300
        )
        self.txt_senha = ft.TextField(
            label="Senha (Mín. 3 dígitos)",
            key="senha",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self.save
        )
        self.txt_repete = ft.TextField(
            label="Repita a Senha",
            key="repete",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self.save
        )
            
        self.content = ft.Column(
            controls=[self.txt_cpf, self.txt_senha, self.txt_repete],
            tight=True
        )
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close_dialog),
            ft.TextButton("Confirmar", on_click=self.save),
        ]
            
    def close_dialog(self, e=None):
        self.open = False
        self.page_ref.update()

    def show_msg(self, msg: str, color: str):
        self.page_ref.show_dialog(
            ft.SnackBar(content=ft.Text(msg), bgcolor=color)
        )

    def save(self, e=None):
        s1 = self.txt_senha.value
        s2 = self.txt_repete.value
        
        if not s1 or len(s1) < 3:
            self.show_msg("A senha deve ter no mínimo 3 dígitos.", ft.Colors.RED_600)
            return
            
        if s1 != s2:
            self.show_msg("As senhas não coincidem.", ft.Colors.RED_600)
            return

        sucesso = DBControl.atualizar_senha_usuario(self.cpf, s1)
        if sucesso:
            self.show_msg("Senha cadastrada com sucesso! Insira-a para login.", ft.Colors.GREEN_600)
            self.close_dialog()
            if self.on_success:
                self.on_success()
        else:
            self.show_msg("Erro interno ao atualizar a senha.", ft.Colors.RED_600)
            self.close_dialog()

class FormLogin(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.Alignment.CENTER

        # Elementos
        self.txt_user = ft.TextField(
            label="CPF",
            key="cpf",
            max_length=11,
            keyboard_type=ft.KeyboardType.NUMBER,
            )
        self.txt_password = ft.TextField(
            label="Senha",
            key="senha",
            password=True,
            can_reveal_password=True,
            disabled=True
            )

        # Retorna o layout com os botões
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[self.txt_user, self.txt_password],
        )

class ActionButtons(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.Alignment.CENTER_RIGHT

        # Elementos
        self.btn_login = ft.IconButton(
            tooltip="Login",
            key="login",
            icon=ft.Icons.LOGIN,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN_300,
            hover_color=ft.Colors.GREEN_500
            )
        self.btn_clean = ft.IconButton(
            tooltip="Limpar",
            key="limpar",
            icon=ft.Icons.CLEANING_SERVICES,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.ORANGE_300,
            hover_color=ft.Colors.ORANGE_500
            )

        # Retorna o layout com os botões
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            wrap=True,
            controls=[self.btn_login, self.btn_clean],
        )

class Login(ft.View):
    def __init__(self):
        super().__init__()
        self.route = "/login"
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.theme_mode = ft.ThemeMode.LIGHT

        # Cria Elementos
        self.form_login = FormLogin()
        self.action_buttons = ActionButtons()
        self.logo = ft.Container(
            alignment=ft.Alignment.CENTER,
            border=ft.Border.all(1, ft.Colors.BLUE_300),
            border_radius=ft.BorderRadius.all(10),
            content=ft.Image(
                src="logos/udv_logo.png",
                width=250,
                height=150,
            ),
        )
        self.db_info = ft.Icon(ft.Icons.TOKEN)
        self._verificar_conexao()

        # Associa os eventos (Callbacks)
        self.form_login.txt_user.on_submit = self.verificar_cpf
        self.form_login.txt_user.on_blur = self.verificar_cpf
        self.form_login.txt_password.on_submit = self.fazer_login
        self.action_buttons.btn_login.on_click = self.fazer_login
        self.action_buttons.btn_clean.on_click = self.limpar_campos

        # Paginação
        self.controls = [
            ft.Column(
                intrinsic_width=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
                scroll=ft.ScrollMode.ADAPTIVE,
                controls= [
                    ft.Row(controls=[self.db_info], alignment=ft.MainAxisAlignment.END),
                    ft.Column(controls=[self.logo], intrinsic_width=True),
                    self.form_login,
                    self.action_buttons
                    ]
                )
            ]

    def _verificar_conexao(self):
        sucesso, msg_or_version = DBControl.verificar_conexao()
        if sucesso:
            self.db_info.color = ft.Colors.GREEN_500
            self.db_info.tooltip = f"Banco de Dados Conectado\n{msg_or_version}"
        else:
            self.db_info.color = ft.Colors.RED_500
            self.db_info.tooltip = f"Erro de Conexão\nOffline"

    def limpar_campos(self, e):
        self.form_login.txt_user.value = ""
        self.form_login.txt_password.value = ""
        self.form_login.txt_password.disabled = True
        self.form_login.txt_user.update()
        self.form_login.txt_password.update()

    async def verificar_cpf(self, e):
        cpf = self.form_login.txt_user.value
        if not cpf:
            return

        usuario = DBControl.get_usuario_por_cpf(cpf)
        
        if not usuario:
            self.page.show_dialog(
                ft.SnackBar(content=ft.Text("CPF não cadastrado."), bgcolor=ft.Colors.RED_600)
            )
            self.form_login.txt_password.disabled = True
            self.form_login.txt_password.update()
        else:
            # Usuário existe. Verifica se tem senha.
            if not usuario.get("senha"):
                # Abre o Dialog para o cadastro da senha
                def ao_sucesso():
                    self.form_login.txt_password.disabled = False
                    self.form_login.txt_password.update()
                    
                dialog_senha = Dialog_NewPass(cpf, self.page, on_success=ao_sucesso)
                self.page.show_dialog(dialog_senha)
            else:
                # Se tem senha, ativa o campo de senha
                self.form_login.txt_password.disabled = False
                self.form_login.txt_password.update()
                await asyncio.sleep(0.1)
                await self.form_login.txt_password.focus()

    async def fazer_login(self, e):
        cpf = self.form_login.txt_user.value
        senha = self.form_login.txt_password.value
        
        if not cpf or not senha:
            # Exibe aviso caso campos estejam vazios
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Por favor, preencha CPF e Senha."),
                    bgcolor=ft.Colors.AMBER_800
                )
            )
            return
            
        usuario = DBControl.autenticar_usuario(cpf, senha)
        
        if usuario:
            # Login efetuado com sucesso
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(f"Login efetuado com sucesso! Bem-vindo, {usuario['nome']}."),
                    bgcolor=ft.Colors.GREEN_600
                )
            )
            
            # Chama a view dashboard caso o login com usuário não administrador
            if not usuario.get("is_admin"):
                await self.page.push_route(f"/dashboard/{cpf}")
            else:
                await self.page.push_route("/managment")
            
        else:
            # Falha no login
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Senha incorreta!"),
                    bgcolor=ft.Colors.RED_600
                )
            )
