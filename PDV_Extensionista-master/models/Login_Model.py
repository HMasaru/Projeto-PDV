import mysql.connector
import hashlib
import time  # Necessário para a lógica de retry


class LoginModel:
    def __init__(self):
        # APENAS DEFINIMOS AS CREDENCIAIS AQUI. NÃO CONECTAMOS.
        self.db_config = {
            "host": "127.0.0.1",
            "port": 33066,
            "user": "zanatta",
            "password": "pdvpassword123",
            "database": "pdv"
        }
        # IMPORTANTE: Remova self.conn e self.cursor do __init__!

    # === FUNÇÃO CENTRAL COM LÓGICA DE RETRY E CORREÇÃO DO ERRO 2013 ===
    def _get_connection(self, dictionary_cursor=True):
        """Tenta conectar com retries para dar tempo ao container Docker."""

        MAX_TRIES = 5
        DELAY = 3

        for attempt in range(MAX_TRIES):
            try:
                # Agora, self.db_config existe e é acessível
                conexao = mysql.connector.connect(**self.db_config)
                cursor = conexao.cursor(dictionary=dictionary_cursor)
                return conexao, cursor  # Sucesso!

            except mysql.connector.Error as err:
                if attempt < MAX_TRIES - 1:
                    print(
                        f"[LoginModel] Tentativa {attempt + 1}/{MAX_TRIES}: Falha ao conectar. Esperando {DELAY}s. Erro: {err}")
                    time.sleep(DELAY)
                else:
                    print(f"[LoginModel] Erro fatal após {MAX_TRIES} tentativas. Verifique o Docker. Erro: {err}")
                    return None, None

            except Exception as e:
                # Isso deve capturar o AttributeError se ele voltar, mas não deveria ocorrer mais.
                print(f"[LoginModel] Erro inesperado: {e}")
                return None, None

        return None, None

    def _hash_senha(self, senha):
        """Cria um hash SHA-256 da senha (padrão do init.sql)."""
        return hashlib.sha256(senha.encode()).hexdigest()

    def verificar_login(self, login, senha):
        """Verifica o login e senha no banco."""
        conexao, cursor = self._get_connection()
        if not conexao: return None

        try:
            senha_hash = self._hash_senha(senha)
            query = "SELECT * FROM usuario WHERE login = %s AND senha = %s"
            cursor.execute(query, (login, senha_hash))
            usuario = cursor.fetchone()
            return usuario
        except Exception as e:
            print(f"Erro ao verificar login: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    def cadastrar_usuario(self, nome, login, senha, cargo='Funcionario'):
        """Cadastra um novo usuário."""
        conexao, cursor = self._get_connection()
        if not conexao: return False

        try:
            check_query = "SELECT login FROM usuario WHERE login = %s"
            cursor.execute(check_query, (login,))
            if cursor.fetchone():
                return "login_existe"

            senha_hash = self._hash_senha(senha)
            insert_query = """
                           INSERT INTO usuario (nome, login, senha, cargo)
                           VALUES (%s, %s, %s, %s) \
                           """
            cursor.execute(insert_query, (nome, login, senha_hash, cargo))
            conexao.commit()
            return True
        except Exception as e:
            print(f"Erro ao cadastrar usuário: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    def listar_todos_usuarios(self):
        """Lista todos os usuários do banco de dados."""
        conexao, cursor = self._get_connection(dictionary_cursor=True)
        if not conexao: return []

        try:
            query = "SELECT id_usuario, nome, login, cargo FROM usuario ORDER BY nome"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar usuários: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    def deletar_usuario(self, id_usuario):
        """Deleta um usuário do banco de dados."""
        conexao, cursor = self._get_connection()
        if not conexao: return False

        try:
            cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
            conexao.commit()
            return True
        except mysql.connector.Error as err:
            if err.errno == 1451:
                return "com_registros"
            print(f"Erro ao deletar usuário: {err}")
            return False
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

    def cadastrar_usuario_com_cargo(self, nome, login, senha, cargo):
        """Função mantida por compatibilidade com o Gerenciamento_Controller.py."""
        return self.cadastrar_usuario(nome, login, senha, cargo)