# models/Caixa_Model.py

import mysql.connector
import time
import sys  # Para tratar erros


class CaixaModel:
    def __init__(self):
        self.db_config = {
            "host": "127.0.0.1",
            "port": 33066,  # Porta corrigida
            "user": "zanatta",
            "password": "pdvpassword123",  # Senha corrigida
            "database": "pdv"
        }

    # === FUNÇÃO DE CONEXÃO COM RETRY (CORRIGIDA) ===
    # O parâmetro 'dictionary=False' resolve o erro do argumento inesperado.
    def _get_connection(self, dictionary=False):
        """Tenta conectar com retries."""

        MAX_TRIES = 5
        DELAY = 3

        for attempt in range(MAX_TRIES):
            try:
                conn = mysql.connector.connect(**self.db_config)
                cursor = conn.cursor(dictionary=dictionary)
                return conn, cursor
            except mysql.connector.Error as err:
                if attempt < MAX_TRIES - 1:
                    print(
                        f"[CaixaModel] Tentativa {attempt + 1}/{MAX_TRIES}: Falha ao conectar. Esperando {DELAY}s. Erro: {err}")
                    time.sleep(DELAY)
                else:
                    print(f"[CaixaModel] Erro fatal após {MAX_TRIES} tentativas. Verifique o Docker. Erro: {err}")
                    # Usamos sys.exit para interromper a execução em caso de falha crítica de conexão
                    sys.exit(1)
            except Exception as e:
                print(f"[CaixaModel] Erro inesperado: {e}")
                sys.exit(1)

        return None, None  # Deve ser inalcançável

    # ===============================================

    # ---------------------------------------------
    # Abrir Caixa
    # ---------------------------------------------
    def abrir_caixa(self, id_usuario, valor_inicial=0):
        conn, cursor = self._get_connection()
        if not conn: return None
        try:
            cursor.execute("""
                           INSERT INTO caixa (id_usuario_abertura, data_abertura, valor_inicial, status,
                                              valor_final, total_dinheiro, total_pix, total_credito, total_debito)
                           VALUES (%s, NOW(), %s, 'aberto', 0, 0, 0, 0, 0)
                           """, (id_usuario, valor_inicial))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"[ERRO] Falha ao abrir caixa: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # ---------------------------------------------
    # Buscar Caixa Aberto (por usuário)
    # ---------------------------------------------
    def get_caixa_atual(self, id_usuario):
        # A chamada está correta: self._get_connection(dictionary=True)
        conn, cursor = self._get_connection(dictionary=True)
        if not conn: return None

        try:
            cursor.execute("""
                           SELECT id_caixa
                           FROM caixa
                           WHERE id_usuario_abertura = %s
                             AND status = 'aberto'
                           ORDER BY data_abertura DESC LIMIT 1
                           """, (id_usuario,))

            row = cursor.fetchone()
            return row.get("id_caixa") if row else None
        except Exception as e:
            print(f"[ERRO] Falha ao buscar caixa atual: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    # =====================================================
    # CRIAR UM NOVO CAIXA PADRÃO
    # =====================================================
    def criar_caixa_padrao(self, id_usuario, valor_inicial=0):
        conexao, cursor = self._get_connection()

        cursor.execute("""
                       INSERT INTO caixa (id_usuario_abertura,
                                          data_abertura,
                                          valor_inicial,
                                          status,
                                          valor_final,
                                          total_dinheiro,
                                          total_pix,
                                          total_credito,
                                          total_debito)
                       VALUES (%s, NOW(), %s, 'aberto', 0, 0, 0, 0, 0)
                       """, (id_usuario, valor_inicial))

        conexao.commit()
        last_id = cursor.lastrowid

        cursor.close()
        conexao.close()

        return last_id

    # ---------------------------------------------
    # Atualizar Totais por Forma de Pagamento
    # ---------------------------------------------
    def atualizar_totais_caixa(self, id_caixa, tipo_pagamento, valor):
        conn, cursor = self._get_connection()

        mapa = {
            "Dinheiro": "total_dinheiro",
            "PIX": "total_pix",
            "Crédito": "total_credito",
            "Débito": "total_debito"
        }

        coluna = mapa.get(tipo_pagamento)
        if not coluna:
            print(f"[ERRO] Tipo inválido: {tipo_pagamento}")
            return False

        cursor.execute(f"""
            UPDATE caixa
            SET {coluna} = {coluna} + %s,
                valor_final = valor_final + %s
            WHERE id_caixa = %s
        """, (valor, valor, id_caixa))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    # ---------------------------------------------
    # Registrar Sangria
    # ---------------------------------------------
    def registrar_sangria(self, id_caixa, id_usuario, valor, motivo):
        conn, cursor = self._get_connection()

        cursor.execute("""
            INSERT INTO sangria (id_caixa, id_usuario, data_hora, valor, motivo)
            VALUES (%s, %s, NOW(), %s, %s)
        """, (id_caixa, id_usuario, valor, motivo))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    # ---------------------------------------------
    # Relatório Diário
    # ---------------------------------------------
    def gerar_relatorio_caixa(self, id_caixa):
        conn, cursor = self._get_connection(dictionary=True)

        cursor.execute("""
            SELECT *
            FROM caixa
            WHERE id_caixa = %s
        """, (id_caixa,))

        dados = cursor.fetchone()
        cursor.close()
        conn.close()
        return dados

    # ---------------------------------------------
    # Relatório Mensal
    # ---------------------------------------------
    def gerar_relatorio_mensal(self, mes, ano):
        conn, cursor = self._get_connection(dictionary=True)

        cursor.execute("""
            SELECT 
                SUM(total_dinheiro) AS total_dinheiro,
                SUM(total_pix) AS total_pix,
                SUM(total_credito) AS total_credito,
                SUM(total_debito) AS total_debito,
                SUM(valor_final) AS total_geral
            FROM caixa
            WHERE MONTH(data_abertura) = %s AND YEAR(data_abertura) = %s
        """, (mes, ano))

        dados = cursor.fetchone()
        cursor.close()
        conn.close()
        return dados

    def fechar_caixa(self, id_caixa, valor_final):
        conexao, cursor = self._get_connection()

        cursor.execute("""
                       UPDATE caixa
                       SET status          = 'fechado',
                           valor_final     = %s,
                           data_fechamento = NOW()
                       WHERE id_caixa = %s
                       """, (valor_final, id_caixa))

        conexao.commit()
        cursor.close()
        conexao.close()
