from gears.db_control import DBControl

class WebhookControl:
    
    @staticmethod
    def processar_evento(data: dict):
        """
        Processa os eventos recebidos do webhook do Asaas.
        Faz a validação do status do pagamento e atualiza no banco.
        """
        event = data.get("event")
        payment = data.get("payment", {})
        
        # Verifica se o evento é de confirmação de recebimento/pagamento
        if event in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            external_reference = payment.get("externalReference")
            description = payment.get("description", "")
            
            if external_reference:
                # Verifica se é um pagamento total
                if description and "Pgto Total" in description:
                    try:
                        divida_id = int(external_reference.strip())
                        DBControl.quitar_divida_total_user(divida_id)
                        print(f"[Webhook] Dívida total {divida_id} quitada com sucesso.")
                    except ValueError:
                        print(f"[Webhook] Erro: ID de divida inválido em externalReference '{external_reference}'")
                else:
                    # O externalReference contém os IDs dos registros (dívidas) separados por vírgula
                    ids = external_reference.split(",")
                    for id_str in ids:
                        try:
                            registro_id = int(id_str.strip())
                            # Atualiza o status do registro para quitado
                            sucesso, mensagem = DBControl.quitar_registro(registro_id)
                            print(f"[Webhook] Registro {registro_id}: {mensagem}")
                        except ValueError:
                            print(f"[Webhook] Erro: ID de registro inválido em externalReference '{id_str}'")
            else:
                print("[Webhook] Pagamento recebido, mas sem externalReference associado.")
        else:
            print(f"[Webhook] Evento '{event}' não requer atualização de registros ou não é suportado.")
