import mysql.connector
import time  # Necessário para a lógica de retry


class RelatorioModel:
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

    # ... O resto do seu código
    # =====================================================
    # 🔹 OBTER TOTAIS (CORRIGIDO)
    # =====================================================
    def obter_totais(self):
        """Retorna dois dicionários: totais do dia e do mês."""
        totais_dia = {"Dinheiro": 0, "PIX": 0, "Crédito": 0, "Débito": 0}
        totais_mes = {"Dinheiro": 0, "PIX": 0, "Crédito": 0, "Débito": 0}

        conexao, cursor = self._get_connection(dictionary_cursor=True)
        if not conexao:
            return totais_dia, totais_mes

        # A variável 'hoje' do Python não é mais necessária para esta consulta
        # hoje = datetime.now().date()

        try:
            # === TOTAIS DO DIA (CORRIGIDO) ===
            # Trocamos a data do Python (%s) pela função CURDATE() do MySQL.
            # Isso evita qualquer problema de fuso horário entre a aplicação e o banco.
            cursor.execute("""
                           SELECT total_dinheiro, total_pix, total_credito, total_debito
                           FROM caixa
                           WHERE DATE (data_abertura) = CURDATE()
                           """)  # <-- CORREÇÃO AQUI

            for row in cursor.fetchall():
                totais_dia["Dinheiro"] += row["total_dinheiro"] or 0
                totais_dia["PIX"] += row["total_pix"] or 0
                totais_dia["Crédito"] += row["total_credito"] or 0
                totais_dia["Débito"] += row["total_debito"] or 0

            # === TOTAIS DO MÊS ===
            cursor.execute("""
                           SELECT total_dinheiro, total_pix, total_credito, total_debito
                           FROM caixa
                           WHERE MONTH (data_abertura) = MONTH (CURDATE())
                             AND YEAR (data_abertura) = YEAR (CURDATE())
                           """)
            for row in cursor.fetchall():
                totais_mes["Dinheiro"] += row["total_dinheiro"] or 0
                totais_mes["PIX"] += row["total_pix"] or 0
                totais_mes["Crédito"] += row["total_credito"] or 0
                totais_mes["Débito"] += row["total_debito"] or 0

        except mysql.connector.Error as err:
            print(f"[ERRO SQL] {err}")
        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()

        return totais_dia, totais_mes

    # =====================================================
    # 🔹 ENCERRAR O DIA
    # =====================================================
    def encerrar_dia(self):
        """
        Fecha todos os caixas abertos do dia.
        """
        conexao, cursor = self._get_connection(dictionary_cursor=False)
        if not conexao:
            return False

        try:
            # Fecha os caixas do dia
            cursor.execute("""
                           UPDATE caixa
                           SET status          = 'fechado',
                               data_fechamento = NOW()
                           WHERE DATE(data_abertura) = CURDATE()
                  AND status = 'aberto'
                           """)
            conexao.commit()
            print("[OK] Caixas do dia encerrados com sucesso.")
            return True

        except mysql.connector.Error as err:
            print(f"[ERRO SQL] {err}")
            return False

        finally:
            if cursor: cursor.close()
            if conexao: conexao.close()