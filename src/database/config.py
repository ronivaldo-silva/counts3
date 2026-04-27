import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Carrega as variáveis do arquivo .env
load_dotenv()

# Obtém a variável do banco de dados (Produção)
DATABASE_URL = os.getenv("DATABASE_URL")

# Resiliência: Se não houver banco .env configurado, recua graciosamente para SQLite nativo
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///counts.db"

# Fix for Render/Heroku typically using 'postgres://' which SQLAlchemy doesn't like anymore
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True
)
# Note: check_same_thread=False is needed for SQLite + Multithreading (Flet often runs in threads)
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_basic_data():
    """
    Popula dados básicos essenciais no banco de dados se não existirem.
    - Categorias padrão
    - Classificações padrão
    - Usuário Admin
    
    Esta função é chamada automaticamente no startup da aplicação.
    """
    # Import here to avoid circular dependency
    from models.db_models import Usuario, Categoria, Classificacao
    
    # Instrução Mágica Local: Cria o arquivo .db e as tabelas com colunas caso não existam
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        try:
            # Seed Categorias (Estilo 2.0)
            count_categorias = db.scalar(select(func.count()).select_from(Categoria))
            if count_categorias == 0:
                print("🌱 Seeding Categorias...")
                cats = [
                    Categoria(categoria="Mensalidade", repete=True),
                    Categoria(categoria="Cantina", repete=False),
                    Categoria(categoria="Dízimo", repete=False),
                    Categoria(categoria="Big Loja", repete=False),
                    Categoria(categoria="Cota Preparo", repete=False),
                    Categoria(categoria="Cotas Diversas", repete=False),
                    Categoria(categoria="Doação", repete=False),
                    Categoria(categoria="Prosperar", repete=False),
                    Categoria(categoria="Novo Encanto", repete=False),
                    Categoria(categoria="Outros", repete=False)
                ]
                db.add_all(cats)
                db.commit()
                print("✅ Categorias criadas com sucesso!")
            else:
                print("ℹ️  Categorias já existem no banco.")

            # Seed Classificacao (Estilo 2.0)
            count_classificacoes = db.scalar(select(func.count()).select_from(Classificacao))
            if count_classificacoes == 0:
                print("🌱 Seeding Classificações...")
                classifications = [
                    Classificacao(classificacao="Pendente"),
                    Classificacao(classificacao="Vencido"),
                    Classificacao(classificacao="Pago"),
                    Classificacao(classificacao="Parcial")
                ]
                db.add_all(classifications)
                db.commit()
                print("✅ Classificações criadas com sucesso!")
            else:
                print("ℹ️  Classificações já existem no banco.")

            # Seed Admin User (Estilo 2.0)
            admin_user = db.scalar(select(Usuario).where(Usuario.cpf == "00000000000"))
            if not admin_user:
                print("🌱 Criando usuário Admin...")
                admin = Usuario(
                    cpf="00000000000", 
                    nome="Administrador", 
                    senha="321",  # Em produção, considere usar hash
                    is_admin=True
                )
                db.add(admin)
                db.commit()
                print("✅ Usuário Admin criado! (CPF: 00000000000, Senha: 321)")
            else:
                print("ℹ️  Usuário Admin já existe.")
                
            print("🎉 Seed de dados básicos concluído!")
            
        except Exception as e:
            print(f"❌ Erro ao popular dados básicos: {e}")
            db.rollback()
