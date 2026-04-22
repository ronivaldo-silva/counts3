from sqlalchemy import select, text
from sqlalchemy.orm import joinedload, make_transient
from database.config import SessionLocal, engine
from database.models import Usuario, Registro, Categoria, Classificacao

class DBControl:
    """
    Classe centralizadora de comandos e consultas ao banco de dados,
    atuando como uma camada de negócio/serviço.
    """
    
    @staticmethod
    def verificar_conexao():
        """
        Verifica a conexão com o banco de dados.
        Retorna uma tupla (sucesso: bool, mensagem: str).
        """
        try:
            with engine.connect() as conn:
                if engine.dialect.name == "sqlite":
                    version = conn.scalar(text("SELECT sqlite_version()"))
                    versao_curta = f"SQLite {version}" if version else "SQLite Online"
                else:
                    version = conn.scalar(text("SELECT version()"))
                    versao_curta = version.split(",")[0] if version else "Online"
                return True, versao_curta
        except Exception as e:
            print(f"Erro na conexão com Banco de Dados: {e}")
            return False, str(e)

    @staticmethod
    def get_all_usuarios():
        with SessionLocal() as db:
            stmt = select(Usuario)
            
            usuarios = db.scalar(stmt)
        
        return usuarios

    @staticmethod
    def get_usuario_por_cpf(cpf: str):
        """
        Verifica a existência do usuário apenas pelo CPF.
        Retorna dicionário com dados se existir (incluindo a senha), ou None se não existir.
        """
        with SessionLocal() as db:
            stmt = select(Usuario).where(
                Usuario.cpf == cpf, 
                Usuario.deleted == False
            )
            usuario = db.scalar(stmt)
            if usuario:
                return {
                    "id": usuario.id,
                    "cpf": usuario.cpf,
                    "nome": usuario.nome,
                    "senha": usuario.senha, # Para conferir se já tem senha ou não
                    "is_admin": usuario.is_admin,
                    "actived": usuario.actived,
                    "deleted": usuario.deleted
                }
            return None

    @staticmethod
    def atualizar_senha_usuario(cpf: str, nova_senha: str):
        """
        Atualiza a senha do usuário existente filtrando pelo CPF.
        Retorna True em caso de sucesso.
        """
        with SessionLocal() as db:
            stmt = select(Usuario).where(
                Usuario.cpf == cpf, 
                Usuario.deleted == False
            )
            usuario = db.scalar(stmt)
            if usuario:
                usuario.senha = nova_senha
                db.commit()
                return True
            return False

    @staticmethod
    def autenticar_usuario(cpf: str, senha: str):
        """
        Tenta autenticar um usuário filtrando por CPF, senha e 
        certificando-se de que não está deletado.
        Retorna um dicionário com dados do usuário se verdadeiro, ou None.
        (Nesse momento, retornaremos o próprio objeto do BD atachado, mas idealmente
        retornar dados serializados via schemas).
        """
        with SessionLocal() as db:
            stmt = select(Usuario).where(
                Usuario.cpf == cpf, 
                Usuario.senha == senha,
                Usuario.deleted == False
            )
            usuario = db.scalar(stmt)
            
            # Ao sair do 'with SessionLocal() as db', o objeto 'usuario' fica desconectado
            # (detached) do SQLAlchemy. Para usá-lo livremente sem LazyLoad errors,
            # retornaremos apenas as props essenciais num dicionário, ou podemos retornar o 
            # objeto dependendo de como Flet for mapear. Vamos retornar propriedades seguras.
            if usuario:
                return {
                    "id": usuario.id,
                    "cpf": usuario.cpf,
                    "nome": usuario.nome,
                    "is_admin": usuario.is_admin,
                    "actived": usuario.actived,
                    "deleted": usuario.deleted
                }
            return None

    @staticmethod
    def criar_usuario(cpf: str, nome: str, senha: str = None, is_admin: bool = False):
        try:
            with SessionLocal() as db:
                existe = db.scalar(select(Usuario).where(Usuario.cpf == cpf))
                if existe:
                    return False, "CPF já cadastrado."
                
                novo_usuario = Usuario(
                    cpf=cpf,
                    nome=nome,
                    senha=senha,
                    is_admin=is_admin
                )
                db.add(novo_usuario)
                db.commit()
                return True, "Usuário cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
            
    @staticmethod
    def get_registros_por_cpf(cpf: str):
        """
        Recupera os registros do banco de dados filtrando pelo CPF do usuário.
        """
        with SessionLocal() as db:
            stmt = (
                select(Registro, Categoria)
                .join(Usuario, Registro.user_id == Usuario.id)
                .join(Categoria, Registro.category_id == Categoria.id)
                .where(Usuario.cpf == cpf, Usuario.deleted == False)
                .order_by(Registro.data_debito.desc().nulls_last())
            )
            resultados = db.execute(stmt).all()
            
            registros_formatados = []
            for reg, cat in resultados:
                # Tenta formatar a data que estiver disponível
                data_exibicao = "N/A"
                if reg.data_debito:
                    data_exibicao = reg.data_debito.strftime("%d/%m/%Y")
                elif reg.data_prevista:
                    data_exibicao = reg.data_prevista.strftime("%d/%m/%Y")
                elif reg.data_entrada:
                    data_exibicao = reg.data_entrada.strftime("%d/%m/%Y")
                
                titulo = f"Registro #{reg.id} - {cat.categoria}"

                registros_formatados.append({
                    "id": reg.id,
                    "titulo": titulo,
                    "valor": reg.valor,
                    "data_divida": data_exibicao,
                    "categoria": cat.categoria,
                    "type_id": reg.type_id,
                    "saldo": reg.saldo
                })
            return registros_formatados

    # Adicione futuras consultas aqui (ex: salvar_transacao, etc.)

    @staticmethod
    def get_todos_registros() -> list[Registro]:
        """
        Retorna todos os Registros do banco com eager load dos relacionamentos
        (usuario, categoria_rel, classificacao_rel), seguros para uso fora da sessão.
        """
        with SessionLocal() as db:
            stmt = (
                select(Registro)
                .options(
                    joinedload(Registro.usuario),
                    joinedload(Registro.categoria_rel),
                    joinedload(Registro.classificacao_rel),
                )
                .order_by(Registro.data_debito.desc().nulls_last())
            )
            registros = db.scalars(stmt).unique().all()
            # Expunge para desacoplar os objetos da sessão, mantendo os dados já carregados
            for reg in registros:
                db.expunge(reg)
            return registros