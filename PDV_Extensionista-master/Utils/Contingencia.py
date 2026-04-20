import json
import os

ARQUIVO = "contingencia_nfc.json"


def salvar_em_contingencia(venda_dados):
    """Salva uma venda no arquivo de pendentes."""
    pendentes = []

    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            pendentes = json.load(f)

    pendentes.append(venda_dados)

    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(pendentes, f, indent=4, ensure_ascii=False)

    print("[CONTINGÊNCIA] Venda salva offline.")


def carregar_pendentes():
    if not os.path.exists(ARQUIVO):
        return []
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def limpar_pendentes(vendas_enviadas):
    """Remove apenas as notas que foram enviadas com sucesso."""
    if not os.path.exists(ARQUIVO):
        return

    with open(ARQUIVO, "r", encoding="utf-8") as f:
        pendentes = json.load(f)

    novos = [v for v in pendentes if v not in vendas_enviadas]

    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(novos, f, indent=4, ensure_ascii=False)
