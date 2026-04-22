import flet as ft
from gears.db_control import DBControl

class FormCrudUser(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.Alignment.CENTER
        
        # Elementos
        self.txt_cpf = ft.TextField(
            label="CPF",
            key="cpf",
            max_length=11,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.txt_nome = ft.TextField(
            label="Nome Completo",
            key="nome",
            max_length=100
        )
        self.txt_senha = ft.TextField(
            label="Senha (Opcional)",
            key="senha",
            password=True,
            can_reveal_password=True
        )
        self.chk_admin = ft.Checkbox(
            label="Administrador do sistema",
            value=False
        )
        
        # Agrupamento Visual
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                self.txt_cpf,
                self.txt_nome,
                self.txt_senha,
                self.chk_admin
            ]
        )
    
class TabUsers(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.Alignment.CENTER

class CrudUser(ft.View):
    def __init__(self):
        super().__init__()
        self.route = "/new_user"
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.theme_mode = ft.ThemeMode.LIGHT
        
        # Componentes principais
        self.title_text = ft.Text("Novo Usuário", size=24, weight=ft.FontWeight.BOLD)
        self.form_crud = FormCrudUser()
        
        # Botões de Ação
        self.btn_salvar = ft.Button("Salvar Usuário", icon=ft.Icons.SAVE, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, on_click=self.salvar_usuario)
        self.btn_voltar = ft.TextButton("Voltar", on_click=self.voltar)
        
        self.row_actions = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[self.btn_voltar, self.btn_salvar]
        )
        
        # Paginação
        self.controls = [
            ft.Column(
                intrinsic_width=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.title_text,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.form_crud,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.row_actions
                ]
            )
        ]

    def show_msg(self, msg: str, color: str):
        self.page.show_dialog(
            ft.SnackBar(content=ft.Text(msg), bgcolor=color)
        )

    def limpar_campos(self):
        self.form_crud.txt_nome.value = ""
        self.form_crud.txt_cpf.value = ""
        self.form_crud.txt_senha.value = ""
        self.form_crud.chk_admin.value = False
        self.form_crud.update()

    async def voltar(self, e):
        # Apenas tira a tela da pilha do Router se o Router suportar, ou limpa e redireciona.
        if len(self.page.views) > 1:
            self.page.views.pop()
            top_view = self.page.views[-1]
            await self.page.push_route(top_view.route)
        else:
            await self.page.push_route("/login")

    def salvar_usuario(self, e):
        nome = self.form_crud.txt_nome.value
        cpf = self.form_crud.txt_cpf.value
        senha = self.form_crud.txt_senha.value
        is_admin = self.form_crud.chk_admin.value
        
        if not nome or not cpf:
            self.show_msg("Os campos 'Nome' e 'CPF' são obrigatórios.", ft.Colors.RED_600)
            return
            
        senha_final = senha if senha else None
            
        sucesso, msg = DBControl.criar_usuario(cpf, nome, senha=senha_final, is_admin=is_admin)
        
        if sucesso:
            self.show_msg(msg, ft.Colors.GREEN_600)
            self.limpar_campos()
        else:
            self.show_msg(msg, ft.Colors.RED_600)
