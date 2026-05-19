import flet as ft
# from fastapi import FastAPI, Request, HTTPException, Header
# import flet.fastapi as flet_fastapi
# import uvicorn

from views.login import Login
from views.dashboard import Dashboard
from views.managment import Managment
from database.config import seed_basic_data
from gears.db_control import DBControl
# from gears.webhook_control import WebhookControl
from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv("HOST", '0.0.0.0')
PORT = int(os.getenv("PORT", '10000'))
ASSETSPATH = os.getenv("ASSETSPATH", 'assetsmy')
ASAAS_WEBHOOK_TOKEN = os.getenv("ASAAS_WEBHOOK_TOKEN", "")

# app = FastAPI()

# @app.post("/webhook/asaas")
# async def asaas_webhook(request: Request, asaas_access_token: str = Header(None)):
#     # Valida Token (recomendado na documentação do Asaas)
#     if ASAAS_WEBHOOK_TOKEN and asaas_access_token != ASAAS_WEBHOOK_TOKEN:
#         raise HTTPException(status_code=401, detail="Token de autorizacao invalido")
    
#     try:
#         data = await request.json()
#         print(f"Webhook recebido: {data.get('event')}")
#         WebhookControl.processar_evento(data)
#         return {"status": "ok"}
#     except Exception as e:
#         print(f"Erro processando webhook: {e}")
#         raise HTTPException(status_code=400, detail="Erro no processamento do webhook")

async def main(page: ft.Page):
    page.title = "Counts3"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.icon = "favicon.png"
    page.route
    # -- Rehidratação de Sessão --
    if not page.session.store.contains_key("user_cpf"):
        stored_cpf = None #await ft.SharedPreferences().get("user_cpf")
        if stored_cpf:
            usuario = DBControl.get_usuario_por_cpf(stored_cpf)
            if usuario:
                page.session.store.set("user_cpf", stored_cpf)
                page.session.store.set("is_admin", usuario.get("is_admin"))


    async def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        troute = ft.TemplateRoute(page.route)
        
        logado_cpf = page.session.store.get("user_cpf")
        is_admin = page.session.store.get("is_admin")
        
        # Rota Login !!!!!!!!!!
        if troute.match("/") or troute.match("/login"):
            page.views.append(Login())
        
        elif troute.match("/dashboard"):
            if logado_cpf:
                page.views.append(Dashboard(cpf=logado_cpf))
            else:
                await page.push_route("/login")
            
        elif troute.match("/managment"):
            if is_admin:
                page.views.append(Managment())
            else:
                await page.push_route("/login")
        
        else:
            await page.push_route("/login")
            
        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            await page.push_route(top_view.route)
        else:
            await page.push_route("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Inicializa a rota considerando reidratação
    if page.route == "/" or page.route == "":
        logado_cpf = page.session.store.get("user_cpf")
        is_admin = page.session.store.get("is_admin")
        if is_admin:
            await page.push_route("/managment")
        elif logado_cpf:
            await page.push_route("/dashboard")
        else:
            await page.push_route("/login")
    else: # Pagina não existente
        # Ao chamar push_route, o route_change avaliará a segurança
        await page.push_route(page.route)

        # Criar página informativa com mensagem "Página não Existente"

# app.mount("/", flet_fastapi.app(main))

if __name__ == "__main__":
    # Cria os recursos de banco locais e injeta dados básicos se virgem
    # Roda uma única vez na inicialização global do app
    seed_basic_data()
    
    ft.run(main=main, view=ft.AppView.WEB_BROWSER, port=PORT, assets_dir=ASSETSPATH)