from models.cora_api import CoraAPI
import uuid
import re

class CoraControl:
    """
    Controlador central para orquestrar as ações na API da Cora,
    formatando os dados do sistema para a estrutura exigida pela CoraAPI.
    """

    @staticmethod
    def gerar_cobranca_qr_code(nome_cliente: str, email_cliente: str, documento_cliente: str, 
                               nome_servico: str, valor_centavos: int, data_vencimento: str, id_referencia: str = None) -> dict:
        """
        Orquestra a geração de um QR Code Pix na Cora montando o payload necessário e chamando a biblioteca CoraAPI.
        
        :param nome_cliente: Nome do cliente (máximo 60 caracteres).
        :param email_cliente: E-mail do cliente (obrigatório, máximo 60 caracteres).
        :param documento_cliente: CPF ou CNPJ do cliente.
        :param nome_servico: Nome/Descrição do que está sendo cobrado.
        :param valor_centavos: Valor inteiro representando centavos (ex: R$ 10,01 -> 1001).
        :param data_vencimento: Data de vencimento formato AAAA-MM-DD.
        :param id_referencia: Código opcional definido pelo sistema para a fatura (code).
        :return: Retorna o dicionário com a resposta da API (incluindo o emv/PIX) ou None.
        """
        api = CoraAPI()
        
        # Limpar documento_cliente para deixar apenas números
        doc_limpo = re.sub(r'\D', '', documento_cliente)
        tipo_doc = "CPF" if len(doc_limpo) == 11 else "CNPJ"

        # Se id_referencia não foi passado, geramos um provisório.
        if not id_referencia:
            id_referencia = f"sys_{uuid.uuid4().hex[:8]}"

        payload = {
            "code": id_referencia,
            "customer": {
                "name": nome_cliente[:60],
                "email": email_cliente[:60] if email_cliente else "padrao@counts.com.br",
                "document": {
                    "identity": doc_limpo,
                    "type": tipo_doc
                }
            },
            "services": [
                {
                    "name": "Cobrança Counts",
                    "description": nome_servico[:100],
                    "amount": valor_centavos
                }
            ],
            "payment_terms": {
                "due_date": data_vencimento
            },
            # Para criar um QR code de pagamento é preciso inserir apenas a opção de "PIX"
            "payment_forms": ["PIX"]
        }

        # Chama a biblioteca que lida com o request
        resposta = api.criar_qr_code_pix(dados=payload)
        return resposta
