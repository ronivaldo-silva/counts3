import os
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class AsaasAPI:
    """
    Classe para interagir com a API do Asaas (Clientes e Cobranças).
    As configurações BASEURL e TOKEN são obtidas do arquivo .env da raiz do projeto.
    """

    def __init__(self):
        self.base_url = os.getenv("BASEURL")
        self.token = os.getenv("TOKEN")
        
        if not self.base_url:
            raise ValueError("BASEURL não encontrado no arquivo .env")
        if not self.token:
            raise ValueError("TOKEN não encontrado no arquivo .env")
            
        # Iniciamos uma Sessão para aproveitar o Connection Pooling (Performance)
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "access_token": self.token
        })

    def _request(self, method, endpoint, data=None, params=None):
        """
        Método interno para realizar as requisições usando a sessão persistente.
        """
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        
        if data:
            data = {k: v for k, v in data.items() if v is not None}
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        # Usamos self.session em vez de requests puro
        response = self.session.request(method, url, json=data, params=params)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Erro HTTP na API Asaas ({response.status_code}): {response.text}")
            raise e
        except ValueError:
            # Em alguns casos como DELETE com 204 No Content ou similar, pode não ser JSON
            return response.text

    # ==========================================
    # CLIENTES (Customers)
    # ==========================================
    
    def list_clientes(self, name=None, email=None, cpfCnpj=None, groupName=None, externalReference=None, offset=0, limit=10):
        """
        Lista clientes.
        """
        params = {
            "name": name,
            "email": email,
            "cpfCnpj": cpfCnpj,
            "groupName": groupName,
            "externalReference": externalReference,
            "offset": offset,
            "limit": limit
        }
        return self._request("GET", "/customers", params=params)

    def get_cliente(self, customer_id):
        """
        Recupera os detalhes de um único cliente pelo ID.
        """
        return self._request("GET", f"/customers/{customer_id}")

    def create_cliente(self, name, cpfCnpj, email=None, phone=None, mobilePhone=None, 
                       address=None, addressNumber=None, complement=None, province=None, 
                       postalCode=None, externalReference=None, notificationDisabled=None, 
                       additionalEmails=None, municipalInscription=None, stateInscription=None, 
                       observations=None, groupName=None):
        """
        Cria um novo cliente. Name e cpfCnpj são obrigatórios.
        """
        data = {
            "name": name,
            "cpfCnpj": cpfCnpj,
            "email": email,
            "phone": phone,
            "mobilePhone": mobilePhone,
            "address": address,
            "addressNumber": addressNumber,
            "complement": complement,
            "province": province,
            "postalCode": postalCode,
            "externalReference": externalReference,
            "notificationDisabled": notificationDisabled,
            "additionalEmails": additionalEmails,
            "municipalInscription": municipalInscription,
            "stateInscription": stateInscription,
            "observations": observations,
            "groupName": groupName
        }
        return self._request("POST", "/customers", data=data)

    def update_cliente(self, customer_id, **kwargs):
        """
        Atualiza dados de um cliente existente.
        Permite enviar qualquer atualização de parâmetro suportado pela API livremente.
        """
        return self._request("POST", f"/customers/{customer_id}", data=kwargs)

    def delete_cliente(self, customer_id):
        """
        Remove um cliente. Retorna o json de confirmação da operação (ex: deleted: true).
        """
        return self._request("DELETE", f"/customers/{customer_id}")

    # ==========================================
    # COBRANÇAS (Payments)
    # ==========================================
    
    def list_cobrancas(self, customer=None, customerGroupName=None, billingType=None, 
                       status=None, subscription=None, installment=None, externalReference=None, 
                       paymentDate=None, anticipated=None, anticipable=None,
                       dateCreated_ge=None, dateCreated_le=None, dueDate_ge=None, dueDate_le=None,
                       offset=0, limit=10):
        """
        Lista e filtra cobranças na plataforma.
        """
        params = {
            "customer": customer,
            "customerGroupName": customerGroupName,
            "billingType": billingType,
            "status": status,
            "subscription": subscription,
            "installment": installment,
            "externalReference": externalReference,
            "paymentDate": paymentDate,
            "anticipated": anticipated,
            "anticipable": anticipable,
            "dateCreated[ge]": dateCreated_ge,
            "dateCreated[le]": dateCreated_le,
            "dueDate[ge]": dueDate_ge, # data de vencimento inicial
            "dueDate[le]": dueDate_le, # data de vencimento final
            "offset": offset,
            "limit": limit
        }
        return self._request("GET", "/payments", params=params)

    def get_cobranca(self, payment_id):
        """
        Recupera detalhes de uma cobrança específica.
        """
        return self._request("GET", f"/payments/{payment_id}")

    def create_cobranca(self, customer, billingType, value, dueDate, description=None, 
                        externalReference=None, installmentCount=None, installmentValue=None, 
                        discount=None, interest=None, fine=None, postalService=None, 
                        split=None, callback=None):
        """
        Cria uma nova cobrança. 
        Parâmetros como discount, interest, fine e split esperam dicionários/listas mapeando as propriedades do Asaas.
        """
        data = {
            "customer": customer,
            "billingType": billingType, # Ex: BOLETO, CREDIT_CARD, PIX, UNDEFINED
            "value": value,
            "dueDate": dueDate,
            "description": description,
            "externalReference": externalReference,
            "installmentCount": installmentCount,
            "installmentValue": installmentValue,
            "discount": discount,
            "interest": interest,
            "fine": fine,
            "postalService": postalService,
            "split": split,
            "callback": callback
        }
        return self._request("POST", "/payments", data=data)

    def update_cobranca(self, payment_id, **kwargs):
        """
        Atualiza uma cobrança que já existe.
        Pode ser enviado livremente os campos usando kwargs (ex: value=150.0, dueDate='2024-12-10').
        """
        return self._request("POST", f"/payments/{payment_id}", data=kwargs)

    def delete_cobranca(self, payment_id):
        """
        Remove/Cancela /Estorna uma cobrança. Retorna um json confirmando o status do delete.
        """
        return self._request("DELETE", f"/payments/{payment_id}")

    def get_pix_qr_code(self, payment_id):
        """
        Gera e retorna os dados do QR Code para pagamentos via Pix.
        Endpoint: /payments/{id}/pixQrCode
        """
        return self._request("GET", f"/payments/{payment_id}/pixQrCode")
