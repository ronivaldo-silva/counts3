import flet as ft

from views.login import Login
from views.dashboard import Dashboard
from views.managment import Managment
from database.config import seed_basic_data
from gears.db_control import DBControl
from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv("HOST", '0.0.0.0')
PORT = int(os.getenv("PORT", '10000'))
ASSETSPATH = os.getenv("ASSETSPATH", 'assets')
WEBVIEW = os.getenv("WEBVIEW", ft.AppView.WEB_BROWSER)

# ---------------------------------------------------------------------------
# Função principal do Flet (lógica de roteamento da UI)
# ---------------------------------------------------------------------------
async def main(page: ft.Page):
    page.title = "Counts3"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.icon = "favicon.png"
    page.route = '/'
    # -- Rehidratação de Sessão --
    if not page.session.store.contains_key("user_cpf"):
        stored_cpf = None
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
    else:
        await page.push_route(page.route)


# ---------------------------------------------------------------------------
# Modo WEB (produção) — app FastAPI exportado para o uvicorn
#
# Para rodar:
#   cd src
#   uvicorn main:app --host 0.0.0.0 --port 10000
#
# O endpoint de webhook ficará disponível em:
#   POST  http://host:port/webhook/asaas
#   GET   http://host:port/webhook/asaas/health
# ---------------------------------------------------------------------------
from gears.fastapi_app import criar_flet_app
app = criar_flet_app(main)


# ---------------------------------------------------------------------------
# Modo LOCAL (desenvolvimento) — execução via 'flet run main.py'
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    seed_basic_data()
    ft.run(main=main, view=WEBVIEW, port=PORT, assets_dir=ASSETSPATH)