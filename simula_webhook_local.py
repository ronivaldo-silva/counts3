import requests
import json

url = "http://localhost:10000/webhook/asaas"
headers = {
    "Content-Type": "application/json",
    "asaas-access-token": "8d2f7cbca20e11894d7ab2f80c65de3b8893d7c5"
}

payload = {
    "event": "PAYMENT_CONFIRMED",
    "payment": {
        "id": "pay_simulated_9999",
        "customer": "cus_0000000000",
        "value": 1,
        "netValue": 1,
        "originalValue": 1,
        "status": "CONFIRMED",
        "description": "Pgto: Big Loja",
        "billingType": "PIX",
        "externalReference": "cs3-152",
        "pixTransaction": "00020126760014br.gov.bcb.pix01362fe9f5c4-3671-4543-87e7-bad41e4952ac0214Pgto: Big Loja52040000530398654041.005802BR5925CENTRO ESPIRITA BENEFICEN6006Manaus62290525NUCLEOME00000654796986ASA630498C8"
    }
}

try:
    print(f"Enviando POST para {url}...")
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Resposta: {response.text}")
except requests.exceptions.ConnectionError:
    print("O servidor local (localhost:10000) não parece estar rodando no momento.")
except Exception as e:
    print(f"Erro ao enviar requisição: {e}")
