import mysql.connector
import hashlib
import time  # Necessário para a lógica de retry


class ProdutoModel:
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

    # O resto das funções (pesquisar, buscar_produto_por_id, etc.) deve usar self._get_connection()
    # ...
    # ---------------------------------------------
    # Buscar Produto por ID
    # ---------------------------------------------
    def buscar_produto_por_id(self, id_produto):
        conn, cursor = self._get_connection(dictionary=True)

        cursor.execute("""
            SELECT id_produto, nome, preco_venda, quantidade_estoque
            FROM produto
            WHERE id_produto = %s
        """, (id_produto,))

        produto = cursor.fetchone()
        cursor.close()
        conn.close()
        return produto

    # ---------------------------------------------
    # Pesquisar
    # ---------------------------------------------
    def pesquisar(self, termo):
        termo = f"%{termo}%"
        conn, cursor = self._get_connection(dictionary=True)

        cursor.execute("""
            SELECT id_produto, nome, preco_venda, quantidade_estoque
            FROM produto
            WHERE nome LIKE %s OR id_produto LIKE %s
        """, (termo, termo))

        lista = cursor.fetchall()
        cursor.close()
        conn.close()
        return lista

    # ---------------------------------------------
    # Retirar Estoque
    # ---------------------------------------------
    def retirar_do_estoque(self, id_produto, quantidade):
        conn, cursor = self._get_connection()

        cursor.execute("""
            UPDATE produto
            SET quantidade_estoque = quantidade_estoque - %s
            WHERE id_produto = %s
        """, (quantidade, id_produto))

        conn.commit()
        cursor.close()
        conn.close()
