"""
fastapi_app.py
==============
Ponto central do FastAPI para o projeto Counts3.

Responsabilidades:
  - Definir o app FastAPI com lifespan (startup/shutdown).
  - Expor o endpoint POST /webhook/asaas para receber confirmações do Asaas.
  - Montar o app Flet na raiz "/" para servir a interface web.

Execução em modo web (produção):
  cd src
  uvicorn main:app --host 0.0.0.0 --port 10000

Execução local (desenvolvimento):
  flet run main.py
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

import flet.fastapi as flet_fastapi

from dotenv import load_dotenv

# Imports internos do projeto
from database.config import seed_basic_data
from gears.webhook_control import WebhookControl

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger("counts3.webhook")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

ASAAS_WEBHOOK_TOKEN: str = os.getenv("ASAAS_WEBHOOK_TOKEN", "")
ASSETS_PATH: str = os.getenv("ASSETSPATH", "assets")
PORT: int = int(os.getenv("PORT", "10000"))


# ---------------------------------------------------------------------------
# Lifespan — executa seed na inicialização do servidor
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida da aplicação FastAPI.
    O bloco antes do 'yield' é o startup; após o 'yield' é o shutdown.
    """
    import sys
    # Força UTF-8 no stdout/stderr para suportar emojis no Windows (cp1252 não suporta)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    logger.info("Iniciando servidor Counts3...")
    seed_basic_data()
    logger.info("Banco de dados pronto.")
    yield
    logger.info("Servidor Counts3 encerrado.")


# ---------------------------------------------------------------------------
# App FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Counts3 API",
    description="API do sistema de gestão financeira Counts3 com suporte a webhooks do Asaas.",
    version="0.85.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Endpoint de Health Check do Webhook
# ---------------------------------------------------------------------------
@app.get("/webhook/asaas/health", tags=["Webhook"])
async def webhook_health():
    """
    Verifica se o endpoint de webhook está ativo e acessível.
    Útil para testar a conectividade antes de configurar no painel Asaas.
    """
    return {
        "status": "ok",
        "service": "Counts3 Webhook",
        "token_configurado": bool(ASAAS_WEBHOOK_TOKEN),
    }


# ---------------------------------------------------------------------------
# Endpoint Principal do Webhook — POST /webhook/asaas
# ---------------------------------------------------------------------------
@app.post("/webhook/asaas", tags=["Webhook"])
async def asaas_webhook(
    request: Request,
    asaas_access_token: str = Header(None, alias="asaas-access-token"),
):
    """
    Recebe notificações de eventos do Asaas.

    O Asaas envia um POST com JSON contendo:
      - event: tipo do evento (ex: "PAYMENT_RECEIVED", "PAYMENT_CONFIRMED")
      - payment: objeto com dados da cobrança, incluindo 'externalReference'

    O campo 'externalReference' é o ID da dívida/dividas_by_user que foi
    preenchido no momento da criação do QR Code Pix em Asaas.gerar_pix_estatico().

    Retorno:
      HTTP 200 {"received": True} — Asaas interpreta qualquer 2xx como confirmação.
      HTTP 401 — Token inválido (Asaas irá retentar o envio).
    """
    # --- Validação do Token de Segurança ---
    if ASAAS_WEBHOOK_TOKEN:
        if asaas_access_token != ASAAS_WEBHOOK_TOKEN:
            logger.warning(
                "❌ Webhook recebido com token inválido. "
                f"Esperado: ***{ASAAS_WEBHOOK_TOKEN[-4:]} | "
                f"Recebido: {str(asaas_access_token)[:4]}***"
            )
            raise HTTPException(
                status_code=401,
                detail="Token de autorização inválido.",
            )

    # --- Parse do Payload ---
    try:
        data: dict = await request.json()
    except Exception as e:
        logger.error(f"❌ Erro ao parsear JSON do webhook: {e}")
        raise HTTPException(
            status_code=400,
            detail="Payload inválido: JSON malformado.",
        )

    event: str = data.get("event", "DESCONHECIDO")
    payment: dict = data.get("payment", {})
    external_reference: str = payment.get("externalReference", "N/A")
    payment_id: str = payment.get("id", "N/A")

    logger.info(
        f"📨 Webhook recebido | Evento: {event} | "
        f"PaymentID: {payment_id} | ExternalRef: {external_reference}"
    )

    # --- Processamento do Evento ---
    try:
        await run_in_threadpool(WebhookControl.processar_evento, data)
    except Exception as e:
        # Loga o erro mas retorna 200 para evitar retentativas infinitas do Asaas
        logger.error(f"❌ Erro ao processar evento '{event}': {e}", exc_info=True)
        # Retorna 200 mesmo assim — Asaas reenviaria infinitamente se retornássemos 5xx
        return JSONResponse(
            status_code=200,
            content={
                "received": True,
                "warning": f"Evento recebido mas processamento falhou: {str(e)}",
            },
        )

    logger.info(f"✅ Evento '{event}' processado com sucesso.")
    return JSONResponse(
        status_code=200,
        content={"received": True},
    )


# ---------------------------------------------------------------------------
# Montagem do App Flet em "/ui"
# — separado dos endpoints FastAPI para que /webhook/asaas não seja interceptado
# — O Flet montado em "/" sobrepõe TODOS os endpoints FastAPI com Method Not Allowed
# ---------------------------------------------------------------------------
def criar_flet_app(main_callable):
    """
    Monta o app Flet no FastAPI e retorna o app pronto para o uvicorn.
    Chamado pelo main.py após importar a função 'main' do Flet.
    
    IMPORTANTE: O app Flet é montado na raiz ('/'), mas como é feito DEPOIS
    da definição das rotas FastAPI (como POST /webhook/asaas), as rotas da API
    terão prioridade.
    """
    # Resolve the directory containing main.py (src/)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, ASSETS_PATH)
    
    app.mount(
        "/",
        flet_fastapi.app(
            main_callable,
            assets_dir=assets_dir,
        ),
    )

    return app
