import flet as ft
from gears.db_control import DBControl
from gears.asaas_control import Asaas
from models.db_models import Registro
from datetime import datetime
import asyncio

# --- Registros do Banco ---
class RegistroCard(ft.Card):
    """Cartão que exibe os dados de uma dívida comum."""
    def __init__(self, registro: Registro, on_pagar_click):
        super().__init__()
        self.data: Registro = registro
        self.on_pagar_click = on_pagar_click
        
        self.elevation = 2
        self.margin = ft.Margin.only(bottom=10)
        
        # Elementos do cabeçalho
        self.titulo = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True)
        self.info = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True, spacing=8)

        self.btn_pagar = ft.TextButton(
            on_click=self._pagar,
            content=ft.Row([ft.Icon(ft.Icons.PAYMENT,), ft.Text("Pagar")], tight=True),
            style=ft.ButtonStyle(
                    color=ft.Colors.GREEN_600,
                    bgcolor=ft.Colors.WHITE,
                    side=ft.BorderSide(1, ft.Colors.GREEN_600),
                    elevation=2,
                )
            )
        
        self.btn_recibo = ft.IconButton(
            icon=ft.Icons.RECEIPT,
            icon_color=ft.Colors.BLUE_300,
            tooltip="Recibo",
        )

        self.__definir_valores()

        self.content = ft.Column(
            tight=True,
            spacing=4,
            controls=[
                ft.Container(
                    padding=ft.Padding.only(left=10, right=10, top=10, bottom=5),
                    content=ft.Column(
                        tight=True,
                        spacing=5,
                        controls=[
                            self.titulo,
                            self.info,
                        ],
                    ),
                ),
                ft.Divider(height=1, thickness=0.5),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    margin=ft.Margin.only(left=10, right=10, top=5, bottom=5),
                    controls=[
                        self.btn_pagar, 
                        #self.btn_recibo
                    ],
                ),
            ],
        )

    def __definir_valores(self):
        categoria = self.data.categoria_rel.categoria
        classificacao = self.data.classificacao_rel.classificacao
        valor = f"R$ {self.data.valor:,.2f}"
        data_divida = self.data.data_debito.strftime("%d/%m/%Y")

        cor = ft.Colors.GREEN_300 if classificacao == "Pago" else ft.Colors.RED_300
        
        self.titulo.controls = [
            ft.Text(categoria, weight=ft.FontWeight.BOLD, size=15, selectable=True),
            ft.Text("|", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
            ft.Text(classificacao, size=13, color=cor, selectable=True),
        ]

        self.info.controls = [
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.RED_300),
                height=32,
                content=ft.Row(
                    tight=True,
                    controls= [
                        ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.RED_400),
                        ft.Text(valor, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                    ],
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.ORANGE_300),
                height=32,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.ORANGE_400),
                        ft.Text(f"Vence: {data_divida}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                    ],
                )
            )
        ]
        
    def _pagar(self, e):
        if self.on_pagar_click:
            self.on_pagar_click(self.data)


class RegistroTotalCard(ft.Card):
    """Cartão que exibe a soma total das dívidas, formatado similar ao RegistroCard."""
    def __init__(self, dados: dict, on_pagar_click):
        super().__init__()
        self.dados = dados
        self.on_pagar_click = on_pagar_click
        
        self.elevation = 4
        self.margin = ft.Margin.only(top=10, bottom=20)
        
        # Elementos do cabeçalho
        self.titulo = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True)
        self.info = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True, spacing=8)

        self.btn_pagar = ft.TextButton(
            on_click=self._pagar,
            content=ft.Row([ft.Icon(ft.Icons.PAYMENTS,), ft.Text("Pagar Tudo")], tight=True),
            style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_900,
                    bgcolor=ft.Colors.WHITE,
                    side=ft.BorderSide(1, ft.Colors.BLUE_600),
                    elevation=2,
                )
            )

        self.__definir_valores()

        self.content = ft.Column(
            tight=True,
            spacing=4,
            controls=[
                ft.Container(
                    padding=ft.Padding.only(left=10, right=10, top=10, bottom=5),
                    content=ft.Column(
                        tight=True,
                        spacing=5,
                        controls=[
                            self.titulo,
                            self.info,
                        ],
                    ),
                ),
                ft.Divider(height=1, thickness=0.5),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    margin=ft.Margin.only(left=10, right=10, top=5, bottom=5),
                    controls=[
                        self.btn_pagar, 
                    ],
                ),
            ],
        )

    def __definir_valores(self):
        valor_total = f"R$ {self.dados.get('valor', 0):,.2f}"
        texto_titulo = self.dados.get('titulo', "Total Acumulado")
        subtitulo = self.dados.get('subtitulo', "Pendências")
        itens = self.dados.get('itens', 0)
        
        self.titulo.controls = [
            ft.Icon(ft.Icons.MONETIZATION_ON, color=ft.Colors.BLUE_900, size=20),
            ft.Text(texto_titulo, weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.BLUE_900),
            ft.Text("|", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
            ft.Text(subtitulo, size=13, color=ft.Colors.BLUE_700),
        ]

        self.info.controls = [
            ft.Container(
                bgcolor=ft.Colors.BLUE_900,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border_radius=ft.BorderRadius.all(8),
                content=ft.Row(
                    tight=True,
                    controls= [
                        ft.Icon(ft.Icons.ATTACH_MONEY, size=20, color=ft.Colors.WHITE),
                        ft.Text(valor_total, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
                    ],
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.BLUE_300),
                height=32,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.LIST_ALT, size=16, color=ft.Colors.BLUE_400),
                        ft.Text(f"{itens} itens", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                    ],
                )
            )
        ]

    def _pagar(self, e):
        if self.on_pagar_click:
            self.on_pagar_click(self.dados)


class TabRegistros(ft.Column):
    def __init__(self, cpf: str):
        super().__init__()
        self.cpf = cpf
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.spacing = 10
        self.dividas_pendentes = []
        self.on_dividas_loaded = None
        self.carregar_dividas()

    def carregar_dividas(self):
        dividas_reais = DBControl.get_registros_por_cpf(self.cpf, pendente=True)
        self.dividas_pendentes = dividas_reais if dividas_reais else []
        
        self.controls = []
        
        if not dividas_reais:
            self.controls.append(
                ft.Container(
                    padding=20,
                    content=ft.Text("Você não possui dívidas pendentes.", italic=True, color=ft.Colors.GREY_500)
                )
            )
        else:
            total_valor = 0
            for d in dividas_reais:
                total_valor += d.valor
                # Filtrar apenas o que o usuário precisa pagar ou visualizar
                self.controls.append(RegistroCard(registro=d, on_pagar_click=self.pagar_divida))
            
            # Adiciona o card de resumo total ao final da lista
            self.controls.append(
                RegistroTotalCard(
                    dados={
                        "valor": total_valor,
                        "itens": len(dividas_reais),
                        "titulo": "Resumo das Obrigações",
                        "subtitulo": "Total Pendente"
                    },
                    on_pagar_click=self.pagar_tudo
                )
            )
        
        if self.on_dividas_loaded:
            self.on_dividas_loaded()

    def atualizar(self):
        self.carregar_dividas()
        self.update()

    def pagar_tudo(self, dados: dict):
        valor_total = dados.get("valor", 0)
        if valor_total <= 1:
            return

        # Mostra um indicador de carregamento
        loading_dialog = ft.AlertDialog(
            content=ft.Row([ft.ProgressRing(), ft.Text(" Gerando QR Code do Total...")], tight=True),
        )
        self.page.show_dialog(loading_dialog)

        descricao = f"Pgto.Total"[:37]
        try:
            resultado = Asaas.gerar_pix_estatico(
                valor=valor_total,
                descricao=descricao,
                id_divida="777"
            )
            self.page.pop_dialog()
        except:
            self.page.pop_dialog()
            self.page.show_dialog(ft.SnackBar(ft.Text("Erro ao gerar QR Code do Total."), bgcolor=ft.Colors.RED_300))
            return

        img_base64 = resultado.get("encodedImage")
        payload = resultado.get("payload")
        
        async def copiar_payload(e):
            try:
                await ft.Clipboard().set(payload)
                self.page.show_dialog(ft.SnackBar(ft.Text("PIX Total copiado com sucesso!"), bgcolor=ft.Colors.GREEN_600))
            except:
                self.page.show_dialog(ft.SnackBar(ft.Text("Erro ao copiar PIX!"), bgcolor=ft.Colors.RED_600))

        # Reutilizando o padrão de diálogo do sistema
        title = ft.Row(
            controls=[
                ft.Icon(ft.Icons.PIX, color=ft.Colors.GREEN_600),
                ft.Text("Pagar Total via Pix", size=16, weight=ft.FontWeight.BOLD)
            ]
        )
        qrcode_pix = ft.Image(src=img_base64, width=200, height=200)
        self.txt_pix = ft.Text(value=payload, selectable=True, color=ft.Colors.BLUE_600)

        btn_copy = ft.TextButton(
            on_click=copiar_payload,
            content=ft.Row([ft.Icon(ft.Icons.COPY,), ft.Text("Copiar")], tight=True), 
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_600,
                bgcolor=ft.Colors.WHITE,
                side=ft.BorderSide(1, ft.Colors.BLUE_600),
                elevation=2,
            )
        )

        btn_cancel = ft.TextButton(
            on_click=lambda e: self.page.pop_dialog(),
            content=ft.Row([ft.Icon(ft.Icons.CANCEL,), ft.Text("Fechar")], tight=True), 
            style=ft.ButtonStyle(
                color=ft.Colors.RED_300,
                bgcolor=ft.Colors.WHITE,
                side=ft.BorderSide(1, ft.Colors.RED_300),
                elevation=2,
            )
        )

        pop_up = ft.AlertDialog(
            title=title,
            content=ft.Column(
                width=300,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                controls=[qrcode_pix, self.txt_pix]
            ),
            actions=[btn_copy, btn_cancel]
        )

        self.page.show_dialog(pop_up)

    def pagar_divida(self, data: Registro):
        # Mostra um indicador de carregamento
        loading_dialog = ft.AlertDialog(
            content=ft.Row([ft.ProgressRing(), ft.Text(" Gerando QR Code...")], tight=True),
        )
        self.page.show_dialog(loading_dialog)

        # Gera o Pix Estático via Asaas
        # Usamos o ID da dívida como externalReference (embutido na descrição para static)
        try:
            resultado = Asaas.gerar_pix_estatico(
                valor=data.valor,
                descricao=f"Pgto: {data.categoria_rel.categoria}",
                id_divida=str(data.id)
            )
            self.page.pop_dialog() # Fecha o loading
        except:
            self.page.pop_dialog() # Fecha o loading
            self.page.show_dialog(ft.SnackBar(ft.Text("Erro ao gerar QR Code Pix."), bgcolor=ft.Colors.RED_300))
            return

        # Prepara elementos do diálogo
        img_base64 = resultado.get("encodedImage")
        payload = resultado.get("payload")
        
        async def copiar_payload(e):
            try:
                await ft.Clipboard().set(payload)
                self.page.show_dialog(
                    ft.SnackBar(ft.Text("PIX copiado com sucesso!"), bgcolor=ft.Colors.GREEN_600)
                )
            except:
                self.page.show_dialog(
                    ft.SnackBar(ft.Text("Erro ao copiar PIX!"), bgcolor=ft.Colors.RED_600)
                )


        dialogo = ft.AlertDialog(
            title=ft.Row([ft.Icon(ft.Icons.PIX, color=ft.Colors.GREEN_600), ft.Text("Pagar via Pix")], tight=True),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Image(src=img_base64, width=200, height=200),
                    ft.Text("Aponte o app do seu banco ou copie o código abaixo:", size=12, text_align=ft.TextAlign.CENTER),
                    ft.Text("Válido por 10 minutos.", size=11, italic=True, color=ft.Colors.GREY_600)
                ]
            ),
            actions=[
                ft.TextButton("Copiar Código", on_click=copiar_payload),
                ft.TextButton("Fechar", on_click=lambda e: self.page.pop_dialog())
            ]
        )

        # Titulo Building
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PIX, color=ft.Colors.GREEN_600),
                ft.Text(f"Pagar {data.categoria_rel.categoria} via Pix", size=16, weight=ft.FontWeight.BOLD)
            ]
        )

        # Corpo / Meio Building
        qrcode_pix = ft.Image(src=img_base64, width=200, height=200)
        self.txt_pix = ft.Text(value=payload, selectable=True, color=ft.Colors.BLUE_600)

        # Botões de Ação Building
        btn_copy = ft.TextButton(
                on_click=copiar_payload,
                content=ft.Row([ft.Icon(ft.Icons.COPY,), ft.Text("Copiar")], tight=True), 
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_600,
                    bgcolor=ft.Colors.WHITE,
                    side=ft.BorderSide(1, ft.Colors.BLUE_600),
                    elevation=2,
                )
            )

        btn_cancel = ft.TextButton(
                on_click=lambda e: self.page.pop_dialog(),
                content=ft.Row([ft.Icon(ft.Icons.CANCEL,), ft.Text("Fechar")], tight=True), 
                style=ft.ButtonStyle(
                    color=ft.Colors.RED_300,
                    bgcolor=ft.Colors.WHITE,
                    side=ft.BorderSide(1, ft.Colors.RED_300),
                    elevation=2,
                )
            )

        pop_up = ft.AlertDialog(
            title=title,
            content=ft.Column(
                width=300,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                controls=[qrcode_pix,self.txt_pix]
            ),
            actions=[btn_copy,btn_cancel]
        )

        self.page.show_dialog(pop_up)


# --- Registros do Asaas ---
class RegistroAsaasCard(ft.Card):
    """Cartão que exibe os dados de uma cobrança Asaas."""
    def __init__(self, data_response: dict):
        super().__init__()
        self.data = data_response
        self.id = self.data['id']
        self._pix_qrcode = None
        self._pix_payload:str = None

        self.elevation = 2
        self.margin = ft.Margin.only(bottom=10)

        # Dialog de pagamento Asaas
        self.img_qr_code = ft.Image(src="", width=200, height=200)
        self.bt_cop_payload = ft.IconButton(icon=ft.Icons.COPY, tooltip="Copiar Pix Copia e Cola", on_click=self.copiar_payload)
        self.bt_link_pagar = ft.IconButton(icon=ft.Icons.LINK, tooltip="Pagar online (Cartão/Boleto)", url=data_response.get('invoiceUrl', ''))
        self.bt_link_boleto = ft.IconButton(icon=ft.Icons.ARTICLE_ROUNDED, tooltip="Baixar Boleto", url=data_response.get('bankSlipUrl', ''))
        
        self.dialog_pay = ft.AlertDialog(
            title=ft.Text(f"Pagamento: {data_response.get('description', 'Cobrança')}", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                controls=[
                    ft.Text("Escaneie o QR Code ou use as opções abaixo:"),
                    self.img_qr_code
                ],
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

        # Layout do Cartão
        self.titulo = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True)
        self.info = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True, spacing=8)
        
        # self.btn_pagar = ft.IconButton(
        #     icon=ft.Icons.PAYMENT, 
        #     icon_color=ft.Colors.BLUE_400, 
        #     tooltip="Opções de Pagamento Asaas", 
        #     on_click=self.open_dialog_pagar
        # )
        self.btn_pagar = ft.TextButton(
            on_click=self.open_dialog_pagar,
            tooltip="Opções de Pagamento Asaas", 
            content=ft.Row([ft.Icon(ft.Icons.PAYMENT,), ft.Text("Pagar")], tight=True),
            style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_600,
                    bgcolor=ft.Colors.WHITE,
                    side=ft.BorderSide(1, ft.Colors.BLUE_600),
                    elevation=2,
                )
            )

        self.__definir_valores()

        self.content = ft.Column(
            tight=True,
            spacing=4,
            controls=[
                ft.Container(
                    content=ft.Column(
                        margin=ft.Margin.only(left=10, right=10, top=5, bottom=5),
                        tight=True,
                        controls=[
                            self.titulo,
                            ft.Container(height=5),
                            self.info,
                        ],
                    ),
                ),
                ft.Divider(height=1, thickness=0.5),
                ft.Row(
                    margin=ft.Margin.only(top=5, bottom=5, left=10, right=10),
                    alignment=ft.MainAxisAlignment.END,
                    controls=[self.btn_pagar],
                ),
            ],
        )

    def __definir_valores(self):
        desc = self.data.get('description', 'Cobrança Asaas')
        status = self.data.get('status', 'Pendente')
        
        # Tenta formatar a data
        venc_str = self.data.get('dueDate', 'N/A')
        try:
            venc_str = datetime.strptime(venc_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            pass
            
        valor = f"R$ {self.data.get('value', 0):,.2f}"

        ref_status = {
            'PENDING': 'Pendente',
            'OVERDUE': 'Vencido',
            'RECEIVED': 'Pago',
        }

        ref_color = {
            'PENDING': ft.Colors.AMBER_400,
            'OVERDUE': ft.Colors.RED_400,
            'RECEIVED': ft.Colors.GREEN_400,
        }

        ref_icon = {
            'PENDING': ft.Icons.SCHEDULE,
            'OVERDUE': ft.Icons.ERROR_OUTLINE,
            'RECEIVED': ft.Icons.CHECK_CIRCLE,
        }
        
        st_text = ref_status.get(status, status)
        st_color = ref_color.get(status, ft.Colors.BLUE_400)
        st_icon = ref_icon.get(status, ft.Icons.INFO_OUTLINE)

        self.titulo.controls = [
            ft.Text("Asaas", weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.BLUE_600),
            ft.Text("|", color=ft.Colors.GREY_400, weight=ft.FontWeight.BOLD),
            ft.Text(desc, size=14, selectable=True),
        ]

        self.info.controls = [
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.RED_300),
                height=32,
                content=ft.Row(
                    tight=True,
                    controls= [
                        ft.Icon(ft.Icons.ATTACH_MONEY, size=16, color=ft.Colors.RED_400),
                        ft.Text(valor, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                    ],
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, st_color),
                height=32,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(st_icon, size=16, color=st_color),
                        ft.Text(st_text, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                    ]
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.ORANGE_300),
                height=32,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=ft.Colors.ORANGE_400),
                        ft.Text(f"Vence: {venc_str}", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                    ],
                )
            )
        ]

    async def open_dialog_pagar(self, e):
        self.page.show_dialog(self.dialog_pay)
        
        if not self._pix_qrcode:
            # Busca os dados da API
            response = Asaas.get_pix_qr_code(self.id)
            if response and response.get('success'):
                self._pix_qrcode = f"data:image/png;base64,{response['encodedImage']}"
                self._pix_payload = response['payload']
                self.img_qr_code.src = self._pix_qrcode
                self.img_qr_code.update()
            else:
                self.img_qr_code.src = ""
                self.img_qr_code.update()
    
    async def copiar_payload(self, e):
        if not self._pix_payload:
            return
        await ft.Clipboard().set(self._pix_payload)
        self.page.show_dialog(ft.SnackBar(content=ft.Text("Pix Copia e Cola copiado!"), bgcolor=ft.Colors.GREEN_300))


class TabRegistrosAsaas(ft.Column):
    def __init__(self, cpf: str):
        super().__init__()
        self.cpf = cpf
        self.expand = True
        self.scroll = ft.ScrollMode.ADAPTIVE
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10
        self.customer_id = None
        self.__offset = 0
        self.__limit = 10
        self.controls = []
        
    def did_mount(self):
        self.page.run_task(self.carregar_cobrancas_async)

    def atualizar(self):
        self.controls.clear()
        self.controls.append(ft.ProgressRing())
        self.update()
        self.__offset = 0
        self.page.run_task(self.carregar_cobrancas_async)

    async def carregar_cobrancas_async(self):
        if not self.cpf:
            self.controls = [ft.Text("CPF inválido.", italic=True)]
            self.update()
            return
        
        try:
            # Pega o ID na API em background
            self.customer_id = Asaas.get_customerid(self.cpf)
            
            if not self.customer_id:
                self.controls = [ft.Text("Cliente não possui registros Asaas.", italic=True)]
                self.update()
                return
            
            # Limpa controls caso tenha o progress ring
            self.controls.clear()
            
            has_more = True
            while has_more:
                try:
                    resposta_pagamentos = Asaas.get_cobrancas(
                        customer_id=self.customer_id,
                        # status="PENDING",
                        offset=self.__offset,
                        limit=self.__limit,
                        ate_data_venc=datetime(2026, 12, 31),
                    )
                except Exception as e:
                    self.controls.append(ft.Text(f"Erro ao buscar na API Asaas: {str(e)}", color=ft.Colors.RED))
                    self.update()
                    return
                
                if resposta_pagamentos and resposta_pagamentos.get("data"):
                    # Processa e adiciona na lista
                    for pag in resposta_pagamentos["data"]:
                        self.controls.append(RegistroAsaasCard(data_response=pag))
                        
                    self.page.update()
                    has_more = resposta_pagamentos.get("hasMore", False)
                    self.__offset += self.__limit
                    await asyncio.sleep(0.1)
                else:
                    has_more = False
                    
            if len(self.controls) == 0:
                self.controls.append(ft.Container(padding=20, content=ft.Text("Nenhuma cobrança Asaas pendente.", italic=True, color=ft.Colors.GREY_500)))
                self.update()
            else:
                self.controls.sort(key=lambda x: x.data.get("dueDate"))
                self.update()
                
        except Exception as e:
            self.controls = [ft.Text(f"Erro interno: {str(e)}", color=ft.Colors.RED)]
            self.update()

# --- View Principal ---
class Dashboard(ft.View):
    """View do painel de controle do usuário, unificando dívidas comuns e Asaas."""
    def __init__(self, cpf: str = ""):
        super().__init__()
        self.route = f"/dashboard/{cpf}"
        self.user_cpf = cpf
        self.user_data = None
        
        self.padding = 0

        titulo_texto = "Painel do Usuário"
        nome_usuario = "Usuário"

        if self.user_cpf:
            self.user_data = DBControl.get_usuario_por_cpf(self.user_cpf)
            if self.user_data:
                nome_usuario = self.user_data.get('nome', 'Usuário')
                titulo_texto = f"Olá, {nome_usuario}"

        # Cabeçalho
        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.DASHBOARD),
            leading_width=40,
            title=ft.Text(titulo_texto, weight=ft.FontWeight.W_500),
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH, 
                    tooltip="Atualizar Dados",
                    on_click=self.atualizar_tudo
                ),
                ft.IconButton(
                    icon=ft.Icons.LOGOUT, 
                    tooltip="Sair", 
                    on_click=self.logout
                ),
                ft.Container(width=10) # espaçamento
            ]
        )

        # Instanciar as abas
        self.tab_comuns = TabRegistros(cpf=self.user_cpf)
        self.tab_asaas = TabRegistrosAsaas(cpf=self.user_cpf)

        # Estrutura com Tabs
        self.abas = ft.TabBar(
            indicator_color=ft.Colors.AMBER_300,
            tabs=[
                ft.Tab(label="Obrigações Pecuniárias", icon=ft.Icons.HOME_WORK),
                ft.Tab(label="Mensalidades Boletos", icon=ft.Icons.RECEIPT_LONG),
            ],
        )

        self.abas_views = ft.TabBarView(
            margin=ft.Margin.all(10),
            expand=True,
            controls=[
                ft.Container(
                    padding=ft.Padding.all(10),
                    content=self.tab_comuns
                ),
                ft.Container(
                    padding=ft.Padding.all(10),
                    content=self.tab_asaas
                )
            ]
        )

        self.tab_bars = ft.Tabs(
                selected_index=0,
                length=2,
                align=ft.Alignment.TOP_CENTER,
                expand=True,
                content=ft.Column(
                    expand=True,
                    width=800,
                    controls=[
                        self.abas,
                        self.abas_views
                    ]
                )
            )

        self.controls = [self.tab_bars]

    def atualizar_tudo(self, e):
        """Dispara a atualização para ambas as listagens."""
        if self.tab_bars.selected_index == 0:
            self.tab_comuns.atualizar()
        else:
            self.tab_asaas.atualizar()
        self.page.update()

    async def logout(self, e):
        self.page.session.store.clear()
        await ft.SharedPreferences().remove("user_cpf")
        await self.page.push_route("/login")
