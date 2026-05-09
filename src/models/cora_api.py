import os
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

class CoraAPI:
    """
    Biblioteca de integração direta com a API da Cora.
    Realiza a autenticação via Bearer token (access_token)
    """

    def __init__(self):
        self.base_url = os.getenv("CORA_BASEURL", "https://api.stage.cora.com.br")
        self.token = os.getenv("CORA_TOKEN")

        if not self.token:
            print("[Aviso] CORA_TOKEN não encontrado no arquivo .env. A autenticação com a Cora irá falhar.")
            
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            })

    def criar_qr_code_pix(self, dados: dict, idempotency_key: str = None) -> dict:
        """
        Emissão de QR code Pix v2
        Gera um QR code Pix através da API de invoices.
        
        :param dados: Dicionário payload conforme as especificações da API Cora.
        :param idempotency_key: Chave de idempotência (UUID) para evitar duplicidade de registros.
        :return: JSON de resposta da API com os dados da Invoice / QR Code, ou None em caso de falha.
        """
        url = f"{self.base_url}/v2/invoices"
        
        if not idempotency_key:
            idempotency_key = str(uuid.uuid4())
            
        headers = {
            "Idempotency-Key": idempotency_key
        }

        try:
            response = self.session.post(url, json=dados, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[CoraAPI] Erro ao criar QR Code Pix: {e}")
            if e.response is not None:
                try:
                    print(f"[CoraAPI] Detalhes do erro: {e.response.json()}")
                except ValueError:
                    print(f"[CoraAPI] Detalhes do erro (texto): {e.response.text}")
            return None
