import requests
import json
from datetime import datetime


class NotaFiscal:
    """
    Classe responsável por emitir NFC-e (Nota Fiscal do Consumidor Eletrônica)
    no ambiente SANDBOX da PlugNotas.
    ✅ NÃO requer certificado digital
    ✅ NÃO precisa de destinatário
    ⚠️ Exige CSC (Código de Segurança do Contribuinte) da SEFAZ
    """

    def __init__(self):
        # === CONFIGURAÇÃO DO AMBIENTE ===
        self.MODO_SANDBOX = True

        # === DADOS SANDBOX ===
        self.URL_SANDBOX = "https://api.sandbox.plugnotas.com.br/nfce"
        self.TOKEN_SANDBOX = "2da392a6-79d2-4304-a8b7-959572c7e44d"
        self.CNPJ_EMITENTE = "08187168000160"  # CNPJ do ambiente de teste da Tecnospeed

        # === DADOS DO CSC (você deve substituir pelos seus dados da SEFAZ) ===
        self.CSC_ID_SANDBOX = "000001"  # ID de homologação padrão
        self.CSC_TOKEN_SANDBOX = "TOKEN_DE_HOMOLOGACAO_AQUI"  # Substitua pelo token da SEFAZ

    # ========================================================================
    def emitir_nota(self, venda_id, itens, pagamentos, troco=0.0):
        """
        Envia uma NFC-e (sem valor fiscal) para o ambiente Sandbox da PlugNotas.
        - venda_id: identificador interno da venda
        - itens: lista de dicionários com {codigo, descricao, valor, ncm, cfop}
        - pagamentos: lista de dicionários com {meio, valor}
        """

        # === Montagem do JSON ===
        payload = [
            {
                "idIntegracao": f"PDV-{venda_id}-{datetime.now().timestamp()}",
                "natureza": "VENDA",
                "emitente": {
                    "cpfCnpj": self.CNPJ_EMITENTE,
                    "nome": "Tecnospeed LTDA",
                    "razaoSocial": "Tecnospeed LTDA",
                    "email": "contato@tecnospeed.com.br"
                },
                "itens": [],
                "pagamentos": [],
                "responsavelTecnico": {
                    "cpfCnpj": "08187168000160",
                    "nome": "Tecnospeed",
                    "email": "contato@tecnospeed.com.br",
                    "telefone": {"ddd": "44", "numero": "30379500"}
                }
            }
        ]

        # === Adiciona os itens da venda ===
        for item in itens:
            payload[0]["itens"].append({
                "codigo": str(item.get("codigo", "1")),
                "descricao": item.get("descricao", "NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"),
                "ncm": item.get("ncm", "06029090"),
                "cfop": item.get("cfop", "5101"),
                "valorUnitario": {
                    "comercial": float(item["valor"]),
                    "tributavel": float(item["valor"])
                },
                "valor": float(item["valor"]),
                "tributos": {
                    "icms": {
                        "origem": "0",
                        "cst": "00",
                        "baseCalculo": {"modalidadeDeterminacao": 0, "valor": 0},
                        "aliquota": 0,
                        "valor": 0
                    },
                    "pis": {
                        "cst": "99",
                        "baseCalculo": {"valor": 0, "quantidade": 0},
                        "aliquota": 0,
                        "valor": 0
                    },
                    "cofins": {
                        "cst": "07",
                        "baseCalculo": {"valor": 0},
                        "aliquota": 0,
                        "valor": 0
                    }
                }
            })

        # Adiciona pagamentos
        for p in pagamentos:
            payload[0]["pagamentos"].append({
                "aVista": True,
                "meio": p.get("meio", "01"),  # 01=Dinheiro, 17=PIX, 03=Crédito, 04=Débito
                "valor": float(p["valor"])
            })

        # Adiciona o valorTroco se houver troco
        if troco and isinstance(troco, (int, float)) and troco > 0:
            payload[0]["valorTroco"] = round(float(troco), 2)

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": self.TOKEN_SANDBOX
        }

        url_com_csc = f"{self.URL_SANDBOX}?cscid={self.CSC_ID_SANDBOX}&csctoken={self.CSC_TOKEN_SANDBOX}"
        # === Envia requisição ===
        try:
            print("\n[DEBUG] Enviando NFC-e para PlugNotas Sandbox...")
            print(f"URL: {url_com_csc}")
            print(json.dumps(payload, indent=4, ensure_ascii=False))

            response = requests.post(
                url_com_csc,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )

            # === Resposta ===
            if response.status_code in (200, 201):
                resp = response.json()
                print(f"\n[OK] NFC-e enviada com sucesso:")
                print(json.dumps(resp, indent=4, ensure_ascii=False))
                return True, resp

            else:
                print(f"\n[ERRO] Status {response.status_code}: {response.text}")
                return False, response.text

        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Falha de comunicação com API: {e}")
            return False, str(e)

        except Exception as e:
            print(f"[ERRO] Erro inesperado: {e}")
            return False, str(e)
