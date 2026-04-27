import flet as ft
from views.login import Login
from views.dashboard import Dashboard
from views.managment import Managment
from database.config import seed_basic_data

async def main(page: ft.Page):
    # Cria os recursos de banco locais e injeta dados básicos se virgem
    seed_basic_data()

    page.title = "Counts3"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.route = "/"

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        troute = ft.TemplateRoute(page.route)
        
        # Rota Login
        if troute.match("/") or troute.match("/login"):
            page.views.append(Login())
        
        elif troute.match("/dashboard/:cpf"):
            page.views.append(Dashboard(cpf=troute.cpf))
            
        elif troute.match("/managment"):
            page.views.append(Managment())
        
        else:
            # Fallback para rotas desconhecidas (opcional, leva pro login)
            page.views.append(Login())
            
        page.update()

    async def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Inicializa a rota
    if page.route == "/":
        await page.push_route("/login")
    else:
        await page.push_route(page.route)

if __name__ == "__main__":
    ft.run(main=main)
