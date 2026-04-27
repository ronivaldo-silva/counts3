import flet as ft
from gears.db_control import DBControl
from models.db_models import Registro
from datetime import date, timedelta

class ConfirmDialog(ft.AlertDialog):
    def __init__(self,registro:Registro, tipo_acao: str):
        super().__init__()
        self.data = registro

        self.on_confirm = None
        self.tipo_acao:str = tipo_acao

        self.title_icon = self.__build_icon()
        self.title_text = self.__build_text()

        self.title = ft.Row(
            controls=[
                self.title_icon,
                self.title_text
            ]
        )

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(f'CPF: {self.data.usuario.cpf}'),
                        ft.Text(f'Nome: {self.data.usuario.nome}'),
                        ft.Text(f'Categoria: {self.data.categoria_rel.categoria}'),
                        ft.Text(f'Valor: {self.data.valor}'),
                    ]
                )
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

        self.actions = [self.btn_cancel, self.btn_confirm ]
        self.actions_alignment = ft.MainAxisAlignment.END
        self.actions_margin = ft.Margin.only(left=5,right=5)

    def _confirm(self,e):
        if self.on_confirm:
            self.on_confirm()
        self.page.pop_dialog()

    def _cancel(self,e):
        self.page.pop_dialog()
    
    def __build_icon(self):
        if self.tipo_acao == "Excluir":
            return ft.Icon(ft.Icons.DELETE, color=ft.Colors.RED_300)
        elif self.tipo_acao == "Quitar":
            return ft.Icon(ft.Icons.MONEY, color=ft.Colors.GREEN_300)

    def __build_text(self):
        return ft.Text(f" Deseja {self.tipo_acao} ? ")

class DatePicker(ft.Row):
    def __init__(self, descricao:str=None, value:date = date.today()):
        super().__init__()
        self.width = 250
        self.alignment = ft.MainAxisAlignment.SPACE_BETWEEN

        self.descricao = ft.Text(f'{descricao}:', weight=ft.FontWeight.BOLD)
        self.date_picker = ft.DatePicker(value=value, on_change=self.set_date)
        self.current_date = value
        self.date_show = ft.Text(value=self.current_date.strftime('%d/%m/%Y'))

        self.gatilho = ft.IconButton(
            icon=ft.Icons.CALENDAR_TODAY,
            on_click=self.pick_date
        )

        self.controls = [self.descricao, self.date_show, self.gatilho]

    async def pick_date(self,e):
        self.page.show_dialog(self.date_picker)
    
    def set_date(self,e):
        self.current_date = self.date_picker.value.date()
        self.date_show.value = self.current_date.strftime('%d/%m/%Y')

    def set_value(self, new_date:date):
        self.current_date = new_date
        self.date_picker.value = new_date
        self.date_show.value = new_date.strftime('%d/%m/%Y')

class FormRegistro(ft.AlertDialog):
    def __init__(self, id_registro: int = None):
        super().__init__()
        # Elementos
        self.id_registro = id_registro
        self.data:Registro = DBControl.get_registro_por_id(id_registro) if id_registro else None
        self.input_date_debit = DatePicker(descricao='Debito')
        self.input_date_debit.gatilho.icon_color = ft.Colors.BLUE_300
        self.input_date_prev = DatePicker(descricao='Previsão',value=(date.today() + timedelta(days=30)))
        self.input_date_prev.gatilho.icon_color = ft.Colors.ORANGE_300
        self.on_save = None

        self.switch_pago = ft.Switch(
            label="Pendente",
            key=1,
            value = False,
            active_track_color=ft.Colors.GREEN_200,
            inactive_track_color=ft.Colors.RED_200,
            thumb_color=ft.Colors.BLUE_300,
            on_change=self.__classificador,
            )
        self.__classificador_init()

        self.input_cpf = ft.Dropdown(
            label="CPF",
            editable=True,
            enable_filter=True,
            menu_height=200,
            options=[
                ft.DropdownOption(text=f"{usuario.cpf}•{usuario.nome}", key=usuario.cpf) 
                for usuario in DBControl.get_all_usuarios()
            ]
        )

        self.input_categoria = ft.Dropdown(
            label="Categoria",
            editable=True,
            enable_filter=True,
            menu_height=200,
            options=[
                ft.DropdownOption(text=categoria.categoria, key=categoria.id) 
                for categoria in DBControl.get_all_categorias()
            ],
        )

        self.input_valor = ft.TextField(label="Valor", prefix='R$ ',keyboard_type=ft.KeyboardType.NUMBER)
        
        if self.id_registro != None:
            # coletar dados de Registro com id
            registro = DBControl.get_registro_por_id(self.id_registro)
            if registro.data_debito:
                self.input_date_debit.set_value(registro.data_debito)
            if registro.data_prevista:
                self.input_date_prev.set_value(registro.data_prevista)
            self.input_cpf.value = registro.usuario.cpf
            self.input_categoria.value = str(registro.category_id)
            self.input_valor.value = f"{registro.valor:.2f}"

        if self.id_registro: # UPDATE
            self.title = ft.Column(
                controls=[
                    ft.Row( controls= [ft.Icon(ft.Icons.MONEY_SHARP, color=ft.Colors.RED_300), ft.Text("Alterar Dívida", size=16,weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                ]
            )
        else: # CREATE
            self.title = ft.Column(
                controls=[
                    ft.Row( controls= [ft.Icon(ft.Icons.MONEY_SHARP, color=ft.Colors.RED_300), ft.Text("Nova Dívida", size=16,weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(thickness=1, color=ft.Colors.BLUE_300),
                ]
        )
        
        self.content = ft.Container(
            content=ft.Column(
                controls=[
                    self.input_cpf,
                    self.input_categoria,
                    self.input_date_debit,
                    self.input_date_prev,
                    self.input_valor,
                    self.switch_pago
                ]
            )
        )

        self.actions = [
            ft.TextButton("Cancelar", on_click=lambda e: self.page.pop_dialog()),
            ft.TextButton("Salvar", on_click=self.__save, autofocus=True),
        ]

    def __save(self, e: ft.ControlEvent):
        cpf = self.input_cpf.value
        categoria_id = self.input_categoria.value
        classificacao_id = self.switch_pago.key
        valor_str = self.input_valor.value
        
        if not self.input_cpf.text or not self.input_categoria.text or not valor_str:
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Por favor, preencha todos os campos obrigatórios!"),
                    bgcolor=ft.Colors.RED_700
                )
            )
            return
            
        try:
            valor = float(valor_str.replace(",", "."))
        except ValueError:
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Valor inválido!"),
                    bgcolor=ft.Colors.RED_700
                )
            )
            return
            
        # extract date objects
        data_debito = self.input_date_debit.current_date
        data_prevista = self.input_date_prev.current_date
        if hasattr(data_debito, 'date'):
            data_debito = data_debito.date()
        if hasattr(data_prevista, 'date'):
            data_prevista = data_prevista.date()
        
        usuario = DBControl.get_usuario_por_cpf(cpf)
        if not usuario:
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("Usuário não encontrado!"),
                    bgcolor=ft.Colors.RED_700
                )
            )
            return
            
        if self.id_registro:
            sucesso, msg = DBControl.atualizar_registro(
                id_registro=self.id_registro,
                user_id=usuario['id'],
                category_id=int(categoria_id),
                valor=valor,
                classificacao_id=int(classificacao_id),
                data_debito=data_debito,
                data_prevista=data_prevista
            )
        else:
            sucesso, msg = DBControl.criar_registro(
                user_id=usuario['id'],
                category_id=int(categoria_id),
                valor=valor,
                data_debito=data_debito,
                data_prevista=data_prevista
            )
            
            self.page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(msg),
                    bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700
                )
            )

        if sucesso and self.on_save:
            self.on_save()
            self.page.pop_dialog()
        self.page.pop_dialog()

    def __classificador_init(self):
        if self.data:
            if self.data.classificacao_id == 3: # Caso pago
                self.switch_pago.value = True
                self.switch_pago.key = 3
            self.switch_pago.label = self.data.classificacao_rel.classificacao

    def __classificador(self,e:ft.Event[ft.Switch]=None):
        if self.switch_pago.value:
            self.switch_pago.key = 3
            self.switch_pago.label = "Pago"
        else:
            if self.input_date_prev.current_date > date.today():
                self.switch_pago.key = 1
                self.switch_pago.label = "Pendente"
            else:
                self.switch_pago.key = 2
                self.switch_pago.label = "Vencido"


    async def date_picker(self,e):
        self.page.show_dialog(self.dialog_date)

class ActionPanel(ft.Container):
    def __init__(self):
        super().__init__()
        self.new_divida_dialog = FormRegistro()

        self.btn_new = ft.IconButton(
            icon=ft.Icons.ADD,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_300,
            tooltip="Nova Dívida",
            on_click=self.show_dialog,
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
    async def show_dialog(self, e):
        self.page.show_dialog(self.new_divida_dialog)

class CardRegistro(ft.Card):
    """Cartão que exibe os dados de um Registro (dívida) com seu usuário relacionado."""

    def __init__(self, registro: Registro):
        super().__init__()
        self.data = registro

        self.edit_divida_dialog = FormRegistro(self.data.id)
        self.edit_divida_dialog.on_save = self.auto_update

        self.delete_dialog = ConfirmDialog(self.data, "Excluir")
        self.quit_dialog = ConfirmDialog(self.data, "Quitar")
        self.quit_dialog.on_confirm = self.quitar_divida
        self.delete_dialog.on_confirm = self.delete_divida

        self.titulo = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True)
        self.info = ft.Row(tight=True, alignment=ft.MainAxisAlignment.START, wrap=True, spacing=8)
        
        self.btn_delete = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_300, tooltip="Excluir", on_click=self.confirm_delete)
        self.btn_edit   = ft.IconButton(icon=ft.Icons.EDIT,   icon_color=ft.Colors.BLUE_300, tooltip="Editar", on_click=self.editar_divida)
        self.btn_quitar = ft.IconButton(icon=ft.Icons.MONEY, icon_color=ft.Colors.GREEN_300, tooltip="Quitar", on_click=self.confirm_quit)

        # --- Dados vindos dos relacionamentos carregados ---
        self.__definir_valores(registro)

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
                    controls=[self.btn_quitar, self.btn_edit, self.btn_delete],
                ),
            ],
        )

    def __definir_valores(self, registro: Registro):
        cpf       = registro.usuario.cpf
        nome      = registro.usuario.nome
        valor     = f"R$ {registro.valor:,.2f}"
        saldo     = f"R$ {registro.saldo:,.2f}"
        categoria = registro.categoria_rel.categoria
        status    = registro.classificacao_rel.classificacao
        data_debito = registro.data_debito.strftime("%d/%m/%Y")
        data_previsao = registro.data_prevista.strftime("%d/%m/%Y")

        ref_color = {
            'Pendente':ft.Colors.ORANGE_300,
            'Vencido' :ft.Colors.RED_300,
            'Pago'    :ft.Colors.GREEN_300
        }

        ref_icon = {
            'Pendente':ft.Icons.CIRCLE_OUTLINED,
            'Vencido' :ft.Icons.ERROR_OUTLINE,
            'Pago'    :ft.Icons.DONE
        }

        # --- Linha 1: Nome | CPF | Categoria---
        self.titulo.controls = [
            ft.Text(nome, weight=ft.FontWeight.BOLD, size=14, selectable=True),
            ft.Text("|", color=ft.Colors.BLUE_300, weight=ft.FontWeight.BOLD),
            ft.Text(cpf, size=12, color=ft.Colors.BLUE_300, selectable=True),
            ft.Text("|", color=ft.Colors.ORANGE_300, weight=ft.FontWeight.BOLD),
            ft.Text(categoria, size=12, color=ft.Colors.ORANGE_300, selectable=True),
        ]

        # --- Linha 2: Valor - Saldo - Vencimento ---
        self.info.controls = [
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.ORANGE_300),
                height=30,
                content=ft.Row(
                    tight=True,
                    width=120,
                    controls= [
                        ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=ft.Colors.RED_300),
                        ft.Text(valor, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ],
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ref_color.get(status, ft.Colors.BLUE_300)),
                height=30,
                width=120,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ref_icon.get(status), color=ref_color.get(status)),
                        ft.Text(status, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)]
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.ORANGE_300),
                height=30,
                width=150,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.MONEY, size=14, color=ft.Colors.BLUE_400),
                        ft.Text(f"Débito:{data_debito}", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ],
                )
            ),
            ft.Container(
                bgcolor=ft.Colors.SURFACE_BRIGHT,
                padding=ft.Padding.symmetric(horizontal=5, vertical=2),
                border_radius=ft.BorderRadius.all(8),
                border=ft.Border.all(1, ft.Colors.ORANGE_300),
                height=30,
                width=150,
                content=ft.Row(
                    tight=True,
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=14, color=ft.Colors.ORANGE_400),
                        ft.Text(f'Previsão:{data_previsao}', size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_54)
                    ],
                )
            )
        ]
        
        if status == "Pago":
            self.btn_quitar.disabled = True
            self.btn_quitar.icon_color = ft.Colors.BLACK_38
        else:
            self.btn_quitar.disabled = False
            self.btn_quitar.icon_color = ft.Colors.GREEN_300

    async def editar_divida(self, e):
        self.page.show_dialog(self.edit_divida_dialog)
    
    async def confirm_delete(self):
        self.page.show_dialog(self.delete_dialog)
    
    async def confirm_quit(self):
        self.page.show_dialog(self.quit_dialog)
    
    def auto_update(self):
        # atualizar dados por id
        self.data = DBControl.get_registro_por_id(self.data.id)
        self.__definir_valores(self.data)
        self.update()

    def delete_divida(self):
        DBControl.deletar_registro(self.data.id)
        self.parent.controls.remove(self)
        self.parent.update()
    
    def quitar_divida(self):
        DBControl.quitar_registro(self.data.id)
        self.auto_update()

class TabRegistros(ft.Column):
    """Coluna com scroll que lista todas as dívidas (Registros) do banco."""

    def __init__(self):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.ALWAYS
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
        return [CardRegistro(registro=reg) for reg in registros]
