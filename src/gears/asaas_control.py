from datetime import datetime, timedelta
from gears.asaas_api import AsaasAPI

class Asaas:
    """
    Classe para concentrar as regras de negócio e abstrair as requisições
    da AsaasAPI para o resto do projeto. 
    Usa uma instância única da API para aproveitar o Connection Pooling.
    """
    
    # Criamos uma única instância para toda a aplicação
    _api = AsaasAPI()
    
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
