from datetime import date, timedelta
from database.config import SessionLocal
from database.models import Registro, Usuario, Categoria, Classificacao

def seed_dividas():
    db = SessionLocal()
    try:
        # Get users
        users = db.query(Usuario).all()
        if not users:
            print("Nenhum usuário encontrado para inserir dívidas.")
            return

        # Sample debt data
        sample_data = [
            {"user_index": 1, "valor": 250.50, "cat_id": 1, "class_id": 1, "desc": "Mensalidade Abril"},
            {"user_index": 1, "valor": 120.00, "cat_id": 2, "class_id": 2, "desc": "Lanche Cantina"},
            {"user_index": 2, "valor": 1500.00, "cat_id": 4, "class_id": 1, "desc": "Compra Big Loja"},
            {"user_index": 2, "valor": 50.00, "cat_id": 8, "class_id": 3, "desc": "Prosperar"},
            {"user_index": 0, "valor": 100.00, "cat_id": 3, "class_id": 1, "desc": "Dízimo Admin"},
        ]

        today = date.today()

        for data in sample_data:
            user = users[data["user_index"] % len(users)]
            
            registro = Registro(
                user_id=user.id,
                type_id=1, # Debt
                category_id=data["cat_id"],
                valor=data["valor"],
                saldo=data["valor"] if data["class_id"] != 3 else 0.0,
                classificacao_id=data["class_id"],
                data_debito=today + timedelta(days=15),
                data_prevista=today + timedelta(days=10)
            )
            db.add(registro)
        
        db.commit()
        print(f"Inseridos {len(sample_data)} registros de dívidas fictícias.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao inserir dívidas: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_dividas()
