from datetime import datetime
import flet as ft
from gears.db_control import DBControl
from gears.asaas_control import Asaas
from datetime import datetime
import asyncio

# Registros do Banco __________________________________________
class Registro(ft.Card):
    def __init__(self, titulo: str, valor: float, data_divida: str, categoria: str, on_pagar_click):
        super().__init__()
        self.elevation = 1
        self.margin = ft.Margin.all(5)

        self.content = ft.Container(
            padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(titulo, weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(f"{categoria} • Vence: {data_divida}", size=12, color=ft.Colors.GREY_300),
                        ]
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Text(f"R$ {valor:.2f}", weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.RED_300),
                            ft.IconButton(
                                icon=ft.Icons.PAYMENT,
                                icon_color=ft.Colors.BLUE_300,
                                bgcolor=ft.Colors.ON_SURFACE,
                                hover_color=ft.Colors.BLUE_400,
                                icon_size=20,
                                tooltip="Pagar",
                                on_click=on_pagar_click
                            )
                        ]
                    )
                ]
            )
        )

class TabRegistros(ft.Column):
    def __init__(self, cpf: str):
        super().__init__()
        self.cpf = cpf
        self.spacing = 10
        self.user_data = self.get_user_data()
        self.carregar_dividas()

    def get_user_data(self):
        return DBControl.get_usuario_por_cpf(self.cpf)

    def carregar_dividas(self):
        # Carregando dados reais do banco de dados via DBControl
        dividas_reais = DBControl.get_registros_por_cpf(self.cpf)
        
        self.controls = [
            ft.Text("Dívidas Pendentes", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ]
        
        if not dividas_reais:
            self.controls.append(ft.Text("Você não possui dívidas pendentes.", italic=True))
        else:
            for d in dividas_reais:
                self.controls.append(
                    Registro(
                        titulo=d["titulo"],
                        valor=d["valor"],
                        data_divida=d["data_divida"],
                        categoria=d["categoria"]
                    )
                )

class TabResumo(ft.Column):
    def __init__(self, cpf: str):
        super().__init__()
        self.cpf = cpf
        self.spacing = 10
        self.carregar_resumo()
        
    def carregar_resumo(self):
        from gears.db_control import DBControl
        registros = DBControl.get_registros_por_cpf(self.cpf)
        
        total_debito = sum(r["valor"] for r in registros if r["type_id"] == 1)
        total_credito = sum(r["valor"] for r in registros if r["type_id"] == 2)
        saldo_atual = total_credito - total_debito
        
        def criar_indicador(titulo, valor, cor, icone):
            return ft.Container(
                padding=15,
                bgcolor=ft.Colors.ON_SURFACE_VARIANT,
                border_radius=12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=5,
                            controls=[
                                ft.Text(titulo, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                                ft.Text(f"R$ {valor:.2f}", size=22, weight=ft.FontWeight.BOLD, color=cor),
                            ]
                        ),
                    ]
                )
            )

        self.controls = [
            ft.Text("Resumo Financeiro", size=20, weight=ft.FontWeight.BOLD),
            criar_indicador("Saldo Atual", saldo_atual, ft.Colors.BLUE_600 if saldo_atual >= 0 else ft.Colors.RED_600, ft.Icons.ACCOUNT_BALANCE_WALLET),
            criar_indicador("Créditos", total_credito, ft.Colors.GREEN_600, ft.Icons.ARROW_UPWARD),
            criar_indicador("Débitos", total_debito, ft.Colors.RED_600, ft.Icons.ARROW_DOWNWARD),
        ]

class DashboardComum(ft.View):
    def __init__(self, cpf: str = ""):
        super().__init__()
        self.route = "/dashboard_comum"
        self.user_cpf = cpf
        self.user_data = None
        
        # Configurações visuais da View
        self.padding = 20
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        titulo_texto = "Dashboard"
        nome_usuario = "Usuário"
        
        if self.user_cpf:
            from gears.db_control import DBControl
            self.user_data = DBControl.get_usuario_por_cpf(self.user_cpf)
            if self.user_data:
                nome_usuario = self.user_data.get('nome', 'Usuário')
                titulo_texto = f"Bem vindo(a), {nome_usuario}"
                
        self.appbar = ft.AppBar(
            title=ft.Text(titulo_texto),
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.Icons.SETTINGS, on_click=self.settings),
                ft.IconButton(ft.Icons.LOGOUT, on_click=self.logout),
            ]
        )
        
        # AlertDialog para o botão de Pagar
        self.dialog_pagar = ft.AlertDialog(
            title=ft.Text("Confirmar Pagamento"),
            content=ft.Text("Aqui entrará as opções e lógica para processar o pagamento da dívida selecionada.", width=350),
            actions=[
                ft.TextButton("Cancelar", on_click=self.fechar_dialog_pagar),
                ft.FilledButton("Processar Pagamento", style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE), on_click=self.fechar_dialog_pagar)
            ]
        )
        
        # Instanciar a lista de registros com os parâmetros
        self.tab_registros = TabRegistros(
            cpf=self.user_cpf, 
            nome_usuario=nome_usuario, 
            on_pagar_click=self.abrir_dialog_pagar
        )
        
        # Instanciar o resumo financeiro
        self.tab_resumo = TabResumo(cpf=self.user_cpf)
        
        # Layout responsivo
        self.controls = [
            ft.Container(
                expand=True,
                padding=ft.Padding.only(top=10),
                content=ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Column(
                            col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                            controls=[self.tab_resumo]
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 12, "md": 8, "lg": 8},
                            controls=[self.tab_registros]
                        )
                    ]
                )
            )
        ]
        
    def abrir_dialog_pagar(self, e):
        self.page.show_dialog(self.dialog_pagar)
        
    def fechar_dialog_pagar(self, e):
        self.page.pop_dialog()
        
    async def settings(self, e):
        pass
        
    async def logout(self, e):
        await self.page.push_route("/login")

# Registros do Asaas __________________________________________
class RegistroAsaas(ft.Card):
    def __init__(self, data_response: dict = None):
        super().__init__()
        self.id = data_response['id']
        self._pix_qrcode = None
        self._pix_payload:str = None

        self.elevation = 1
        self.margin = ft.Margin.all(5)

        self.img_qr_code = ft.Image(src="", width=200, height=200)

        self.bt_cop_payload = ft.IconButton(icon=ft.Icons.COPY, tooltip="Copiar Payload", on_click=self.copiar_payload)
        self.bt_link_pagar = ft.IconButton(icon=ft.Icons.LINK, tooltip="Link Asaas", url=data_response['invoiceUrl'])
        self.bt_link_boleto = ft.IconButton(icon=ft.Icons.ARTICLE_ROUNDED, tooltip="Link Boleto", url=data_response['bankSlipUrl'])
        
        self.dialog_pay = ft.AlertDialog(
            title=ft.Text(data_response['description'], weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[self.img_qr_code],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            actions=[
                self.bt_cop_payload,
                self.bt_link_pagar,
                self.bt_link_boleto,
                ft.TextButton("Fechar", on_click=lambda e: self.page.pop_dialog()),
            ]
        )

        self.content = ft.Container(
            padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            bgcolor=ft.Colors.ON_INVERSE_SURFACE,
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(data_response['description'], weight=ft.FontWeight.BOLD, size=15),
                            ft.Text(f"{data_response['status']} • Vence: {data_response['dueDate']}", size=12, color=ft.Colors.GREY_700),
                        ]
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.Text(f"R$ {data_response['value']:.2f}", weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.RED_300),
                            ft.IconButton(
                                icon=ft.Icons.PAYMENT,
                                icon_color=ft.Colors.BLUE_300,
                                icon_size=20,
                                tooltip="Pagar",
                                on_click=self.open_dialog_pagar
                            )
                        ]
                    )
                ]
            )
        )
    
    async def open_dialog_pagar(self, e):
        # Abre o dialog
        self.page.show_dialog(self.dialog_pay)
        
        if not self._pix_qrcode:
            # Busca os dados da API (síncrono)
            response = Asaas.get_pix_qr_code(self.id)
            if response and response.get('success'):
                self._pix_qrcode = f"data:image/png;base64,{response['encodedImage']}"
                self._pix_payload = response['payload']
                
                # Atualiza o componente de imagem com o novo base64
                self.img_qr_code.src = self._pix_qrcode
                self.img_qr_code.update()
            else:
                self.img_qr_code.src = "" # ou uma imagem de erro
                self.img_qr_code.update()
    
    async def copiar_payload(self, e):
        if not self._pix_payload:
            return
        await ft.Clipboard().set(self._pix_payload)
        
class TabRegistrosAsaas(ft.Column):
    def __init__(self, cpf: str):
        super().__init__()
        self.cpf = cpf
        self.customer_id:str = None
        self.spacing = 10
        self.__offset = 0
        self.__limit = 10
        
        self.controls = [
            ft.Text("Cobranças Asaas (Pendentes)", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
        ]
        
    def did_mount(self):
        # flet lifecycle method
        # IMPORTANTE: Nunca passe requisições síncronas HTTP diretamente no did_mount para não travar a UI toda.
        self.page.run_task(self.carregar_cobrancas_async)

    async def carregar_cobrancas_async(self):
        if not self.cpf:
            self.controls.append(ft.Text("CPF inválido.", italic=True))
            self.update()
            return
            
        try:
            # Requisita na API Asaas em background sem travar a thread principal da tela
            self.customer_id = Asaas.get_customerid(self.cpf)
            
            if not self.customer_id:
                self.controls.append(ft.Text("Cliente não encontrado.", italic=True))
                self.update()
                return
                
            has_more = True
            
            while has_more:
                try:
                    resposta_pagamentos = Asaas.get_cobrancas(
                        customer_id=self.customer_id,
                        status="PENDING", 
                        offset=self.__offset,
                        limit=self.__limit
                    )
                except Exception as e:
                    self.controls.append(ft.Text(f"Erro na API Asaas: {str(e)}", color=ft.Colors.RED))
                    self.update()
                    return
                
                if resposta_pagamentos and resposta_pagamentos.get("data"):
                    for pag in resposta_pagamentos["data"]:
                        venc = pag.get("dueDate", "N/A")
                        try:
                            venc = datetime.strptime(venc, "%Y-%m-%d").strftime("%d/%m/%Y")
                        except:
                            pass
                            
                        self.controls.append(
                            RegistroAsaas(
                                data_response=pag
                            )
                        )
                    self.page.update()
                    has_more = resposta_pagamentos.get("hasMore", False)
                    self.__offset += self.__limit
                    await asyncio.sleep(0.1)
                    self.update()
                else:
                    has_more = False
                    
            if len(self.controls) == 2:
                self.controls.append(ft.Text("Nenhuma cobrança pendente.", italic=True))
                self.update()
                
        except Exception as e:
            self.controls.append(ft.Text(f"Erro na API Asaas: {str(e)}", color=ft.Colors.RED))
            self.update()

class DashboardAsaas(ft.View):
    def __init__(self, cpf: str = ""):
        super().__init__()
        self.route = "/dashboard_asaas"
        self.user_cpf = cpf
        self.user_data = None
        
        # Configurações visuais da View
        self.padding = 20
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        titulo_texto = "Dashboard Asaas"
        nome_usuario = "Usuário"
        
        if self.user_cpf:
            from gears.db_control import DBControl
            self.user_data = DBControl.get_usuario_por_cpf(self.user_cpf)
            if self.user_data:
                nome_usuario = self.user_data.get('nome', 'Usuário')
                titulo_texto = f"Dashboard Asaas de {nome_usuario}"
                
        self.appbar = ft.AppBar(
            title=ft.Text(titulo_texto),
            bgcolor=ft.Colors.GREEN_300, 
            actions=[
                ft.IconButton(ft.Icons.HOME, on_click=self.go_home),
                ft.IconButton(ft.Icons.LOGOUT, on_click=self.logout),
            ]
        )
        
        self.tab_registros_asaas = TabRegistrosAsaas(
            cpf=self.user_cpf
        )
        
        self.controls = [
            ft.Container(
                expand=True,
                padding=ft.Padding.only(top=10),
                content=ft.ResponsiveRow(
                    columns=12,
                    controls=[
                        ft.Column(
                            col={"xs": 12, "sm": 12, "md": 8, "lg": 8},
                            controls=[self.tab_registros_asaas]
                        )
                    ]
                )
            )
        ]
        
    async def go_home(self, e):
        await self.page.push_route(f"/dashboard/{self.user_cpf}")
        
    async def logout(self, e):
        await self.page.push_route("/login")

# Painel principal Navegação de Dashboards
class Dashboard(ft.View):
    def __init__(self, cpf: str = ""):
        super().__init__()
        self.route = f"/dashboard/{cpf}"
        self.user_cpf = cpf
        self.user_data = None

        titulo_texto = "Painel Contas"
        nome_usuario = "Usuário"

        if self.user_cpf:
            from gears.db_control import DBControl
            self.user_data = DBControl.get_usuario_por_cpf(self.user_cpf)
            if self.user_data:
                nome_usuario = self.user_data.get('nome', 'Usuário')
                titulo_texto = f"Painel de {nome_usuario}"

        self.appbar = ft.AppBar(
            title=ft.Text(titulo_texto),
            bgcolor=ft.Colors.ON_SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.Icons.LOGOUT, tooltip="Sair", on_click=self.logout),
            ]
        )

        # Conteúdo da aba "Painel Contas"
        tab_registros = TabRegistros(
            cpf=self.user_cpf
        )

        painel_contas_content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding.only(top=10),
                    content=ft.ResponsiveRow(
                        columns=12,
                        controls=[
                            ft.Column(
                                col={"xs": 12, "sm": 12, "md": 8, "lg": 8},
                                controls=[tab_registros]
                            )
                        ]
                    )
                )
            ]
        )

        # Conteúdo da aba "Painel Asaas"
        self.tab_registros_asaas = TabRegistrosAsaas(cpf=self.user_cpf)

        painel_asaas_content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding.only(top=10),
                    content=ft.ResponsiveRow(
                        columns=12,
                        controls=[
                            ft.Column(
                                col={"xs": 12, "sm": 12, "md": 8, "lg": 8},
                                controls=[self.tab_registros_asaas]
                            )
                        ]
                    )
                )
            ]
        )

        self.controls = [
            ft.Tabs(
                selected_index=1,
                length=2,
                expand=True,
                content=[
                    ft.TabBar(
                        ft.Tab(
                            icon=ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
                            label=painel_contas_content,
                        ),
                        ft.Tab(
                            icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                            label=painel_asaas_content,
                        ),
                        ft.TabBarView(
                            expand=True,
                            controls=[
                                painel_contas_content,
                                painel_asaas_content
                            ]
                        )
                    )
                ],
            )
        ]

    def abrir_dialog_pagar(self, e):
        self.page.show_dialog(self.dialog_pagar)

    async def logout(self, e):
        await self.page.push_route("/login")
