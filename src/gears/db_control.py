from sqlalchemy import select, text
from sqlalchemy.orm import joinedload, make_transient
from database.config import SessionLocal, engine
from models.db_models import Usuario, Registro, Categoria, Classificacao
from datetime import date

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
            stmt = select(Usuario).where(Usuario.deleted == False)
            
            usuarios = db.scalars(stmt).all()
            for u in usuarios:
                db.expunge(u)
        
        return usuarios

    @staticmethod
    def get_usuario_por_id(id_usuario: int):
        with SessionLocal() as db:
            stmt = select(Usuario).where(Usuario.id == id_usuario)
            usuario = db.scalar(stmt)
            if usuario:
                db.expunge(usuario)
            return usuario

    @staticmethod
    def atualizar_usuario(id_usuario: int, cpf: str, nome: str, senha: str, is_admin: bool, actived: bool):
        try:
            with SessionLocal() as db:
                usuario = db.scalar(select(Usuario).where(Usuario.id == id_usuario))
                if usuario:
                    usuario.cpf = cpf
                    usuario.nome = nome
                    if senha:
                        usuario.senha = senha
                    usuario.is_admin = is_admin
                    usuario.actived = actived
                    db.commit()
                    return True, "Usuário atualizado com sucesso!"
                return False, "Usuário não encontrado."
        except Exception as e:
            return False, f"Erro ao atualizar usuário: {str(e)}"

    @staticmethod
    def criar_usuario_completo(cpf: str, nome: str, senha: str, is_admin: bool, actived: bool):
        try:
            with SessionLocal() as db:
                existe = db.scalar(select(Usuario).where(Usuario.cpf == cpf))
                if existe:
                    return False, "CPF já cadastrado."
                novo_usuario = Usuario(
                    cpf=cpf,
                    nome=nome,
                    senha=senha,
                    is_admin=is_admin,
                    actived=actived
                )
                db.add(novo_usuario)
                db.commit()
                return True, "Usuário cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"

    @staticmethod
    def deletar_usuario(id_usuario: int):
        try:
            with SessionLocal() as db:
                usuario = db.scalar(select(Usuario).where(Usuario.id == id_usuario))
                if usuario:
                    usuario.deleted = True # soft delete
                    db.commit()
                    return True, "Usuário deletado com sucesso!"
                return False, "Usuário não encontrado."
        except Exception as e:
            return False, f"Erro ao deletar usuário: {str(e)}"
            
    @staticmethod
    def toggle_status_usuario(id_usuario: int):
        try:
            with SessionLocal() as db:
                usuario = db.scalar(select(Usuario).where(Usuario.id == id_usuario))
                if usuario:
                    usuario.actived = not usuario.actived
                    db.commit()
                    return True, "Status alterado com sucesso!"
                return False, "Usuário não encontrado."
        except Exception as e:
            return False, f"Erro ao alterar status: {str(e)}"

    @staticmethod
    def get_all_categorias():
        with SessionLocal() as db:
            stmt = select(Categoria)
            categorias = db.scalars(stmt).all()
            for c in categorias:
                db.expunge(c)
        return categorias

    @staticmethod
    def get_all_classificacoes():
        with SessionLocal() as db:
            stmt = select(Classificacao)
            classificacoes = db.scalars(stmt).all()
            for c in classificacoes:
                db.expunge(c)
        return classificacoes

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
    def criar_registro(user_id: int, category_id: int, valor: float, data_debito: date, data_prevista: date, type_id: int = 0):
        try:
            with SessionLocal() as db:
                novo_registro = Registro(
                    user_id=user_id,
                    type_id=type_id,
                    category_id=category_id,
                    valor=valor,
                    data_debito=data_debito,
                    data_prevista=data_prevista,
                    saldo=valor, # Initialize balance as full value
                    classificacao_id=1 # Pendente by default
                )
                db.add(novo_registro)
                db.commit()
                return True, "Registro criado com sucesso!"
        except Exception as e:
            return False, f"Erro ao criar registro: {str(e)}"

    @staticmethod
    def atualizar_registro(id_registro: int, user_id: int, category_id: int, valor: float, data_debito: date, data_prevista: date, classificacao_id: int):
        try:
            with SessionLocal() as db:
                registro = db.scalar(select(Registro).where(Registro.id == id_registro))
                if registro:
                    registro.user_id = user_id
                    registro.category_id = category_id
                    registro.valor = valor
                    registro.data_debito = data_debito
                    registro.data_prevista = data_prevista
                    registro.classificacao_id = classificacao_id
                    db.commit()
                    return True, "Registro atualizado com sucesso!"
                return False, "Registro não encontrado."
        except Exception as e:
            return False, f"Erro ao atualizar registro: {str(e)}"
    
    @staticmethod
    def quitar_registro(id_registro: int):
        try:
            with SessionLocal() as db:
                registro = db.scalar(select(Registro).where(Registro.id == id_registro))
                if registro:
                    registro.classificacao_id = 3
                    db.commit()
                    return True, "Registro quitado com sucesso!"
                return False, "Registro não encontrado."
        except Exception as e:
            return False, f"Erro ao quitar registro: {str(e)}"
    
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
            
    @staticmethod
    def get_estatisticas_dividas_usuario(user_id: int):
        with SessionLocal() as db:
            stmt = select(Registro).where(
                Registro.user_id == user_id,
                Registro.classificacao_id.in_([1, 2])
            )
            registros = db.scalars(stmt).all()
            total = sum(r.valor for r in registros)
            datas = [r.data_prevista for r in registros if r.data_prevista] + [r.data_debito for r in registros if r.data_debito]
            data_antiga = min(datas) if datas else None
            return total, data_antiga
            
    @staticmethod
    def get_registros_por_cpf(cpf: str, pendente: bool = False, vencimento: date = None):
        """
        Recupera os registros do banco de dados filtrando pelo CPF do usuário.
        """
        with SessionLocal() as db:
            stmt = (
                select(Registro)
                .join(Usuario, Registro.user_id == Usuario.id)
                .options(
                    joinedload(Registro.usuario),
                    joinedload(Registro.categoria_rel),
                    joinedload(Registro.classificacao_rel)
                )
                .where(Usuario.cpf == cpf, Usuario.deleted == False)
                .order_by(Registro.data_debito.desc().nulls_last())
            )
            
            if pendente:
                stmt = stmt.where(Registro.classificacao_id == 1)
            if vencimento:
                stmt = stmt.where(Registro.data_prevista <= vencimento)
            
            registros = db.scalars(stmt).unique().all()
            for reg in registros:
                db.expunge(reg)
                
            return list(registros)
    
            
    @staticmethod
    def get_registros_por_cpf_deprecated(cpf: str, pendente: bool = False, vencimento: date = None):
        """
        Recupera os registros do banco de dados filtrando pelo CPF do usuário.
        """
        with SessionLocal() as db:
            stmt = (
                select(Registro, Categoria)
                .join(Usuario, Registro.user_id == Usuario.id)
                .join(Categoria, Registro.category_id == Categoria.id)
                .join(Classificacao, Registro.classificacao_id == Classificacao.id)
                .where(Usuario.cpf == cpf, Usuario.deleted == False)
                .order_by(Registro.data_debito.asc().nulls_last())
            )
            if pendente:
                stmt = stmt.where(Registro.pendente == True)
            if vencimento:
                stmt = stmt.where(Registro.data_prevista <= vencimento)
            
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
    
    @staticmethod
    def get_registro_por_id(id: int):
        """
        Retorna um Registro do banco com eager load dos relacionamentos
        (usuario, categoria_rel, classificacao_rel), seguro para uso fora da sessão.
        """
        with SessionLocal() as db:
            stmt = (
                select(Registro)
                .options(
                    joinedload(Registro.usuario),
                    joinedload(Registro.categoria_rel),
                    joinedload(Registro.classificacao_rel),
                )
                .where(Registro.id == id)
            )
            registro = db.scalar(stmt)
            if registro:
                db.expunge(registro)
            return registro
    
    @staticmethod
    def deletar_registro(id_registro: int):
        try:
            with SessionLocal() as db:
                registro = db.scalar(select(Registro).where(Registro.id == id_registro))
                if registro:
                    db.delete(registro)
                    db.commit()
                    return True, "Registro deletado com sucesso!"
                return False, "Registro não encontrado."
        except Exception as e:
            return False, f"Erro ao deletar registro: {str(e)}"
