from datetime import datetime, timedelta
from models.asaas_api import AsaasAPI

class Asaas:
    """
    Classe para concentrar as regras de negócio e abstrair as requisições
    da AsaasAPI para o resto do projeto. 
    Usa uma instância única da API para aproveitar o Connection Pooling.
    """
    
    # Criamos uma única instância para toda a aplicação
    _api = AsaasAPI()
    _cached_pix_key = None
    
    @staticmethod
    def get_pix_key():
        """
        Retorna a chave Pix ativa da conta, buscando na API apenas se não estiver em cache.
        """
        if Asaas._cached_pix_key:
            return Asaas._cached_pix_key
        
        chaves = Asaas._api.list_pix_keys(limit=1)
        if chaves and "data" in chaves and chaves["data"]:
            Asaas._cached_pix_key = chaves["data"][0]["key"]
            return Asaas._cached_pix_key
        return None
    
    @staticmethod
    def get_customerid(cpf: str):
        """
        Consulta na API o customer id baseado no CPF.
        """
        resposta = Asaas._api.list_clientes(cpfCnpj=cpf, limit=1)
        
        if resposta and "data" in resposta and len(resposta["data"]) > 0:
            return resposta["data"][0].get("id")
        return None
        
    @staticmethod
    def get_cobrancas(customer_id: str, status="PENDING", offset=0, limit=10, ate_data_venc:datetime=None):
        """
        Retorna cobranças usando a instância compartilhada da API.
        """
        if ate_data_venc:
            dueDate_le = ate_data_venc
        else:
            dueDate_le = datetime.now() + timedelta(days=40)

        return Asaas._api.list_cobrancas(
            customer    = customer_id,
            status      = status,
            offset      = offset,
            limit       = limit,
            dueDate_le  = dueDate_le.strftime('%Y-%m-%d')
        )
        
    @staticmethod
    def get_clientes(limit=10, offset=0):
        """
        Lista clientes usando a instância compartilhada da API.
        """
        return Asaas._api.list_clientes(limit=limit, offset=offset)

    @staticmethod
    def get_pix_qr_code(payment_id: str):
        """
        Busca os dados do Pix (QR Code e Payload) para uma cobrança.
        """
        return Asaas._api.get_pix_qr_code(payment_id)

    @staticmethod
    def gerar_pix_estatico(valor: float, descricao: str, id_divida: str = None):
        """
        Orquestra a criação de um Pix Estático:
        1. Coleta a primeira chave Pix ativa da conta (usando cache).
        2. Gera um QR Code estático com validade de 1 minuto (60s).
        """
        # 1. Coleta a chave Pix (usa cache interno)
        address_key = Asaas.get_pix_key()
        
        if not address_key:
            print("Erro: Nenhuma chave Pix encontrada na conta Asaas.")
            return None
        
        descricao_curta = descricao
            
        # 2. Gera o QR Code Estático
        return Asaas._api.create_static_pix_qr_code(
            addressKey=address_key,
            description=descricao_curta,
            value=valor,
            expirationSeconds=60, # 60 segundos
            externalReference=id_divida
        )
