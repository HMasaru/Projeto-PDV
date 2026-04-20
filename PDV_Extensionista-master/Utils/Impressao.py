import win32print
import win32ui
import os
import textwrap  # Para formatar o texto

CONFIG_FILE = "printer_config.txt"


def listar_impressoras():
    """Retorna uma lista de todas as impressoras instaladas no Windows."""
    try:
        # Lista impressoras locais e de rede
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        # Retorna apenas os nomes (o nome está no índice 2)
        return [p[2] for p in printers]
    except Exception as e:
        print(f"Erro ao listar impressoras: {e}")
        return []


def salvar_impressora_padrao(nome_impressora):
    """Salva o nome da impressora escolhida em um arquivo de configuração."""
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(nome_impressora)
        return True
    except Exception as e:
        print(f"Erro ao salvar configuração: {e}")
        return False


def carregar_impressora_padrao():
    """Lê o nome da impressora salva no arquivo de configuração."""
    try:
        if not os.path.exists(CONFIG_FILE):
            # Tenta pegar a impressora padrão do Windows se nenhuma estiver salva
            return win32print.GetDefaultPrinter()
        with open(CONFIG_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Erro ao carregar config: {e}")
        return None


def imprimir_cupom(texto_cupom):
    """Envia o texto formatado para a impressora configurada."""
    nome_impressora = carregar_impressora_padrao()
    if not nome_impressora:
        print("Impressora não configurada.")
        return False, "Impressora não configurada"

    try:
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(nome_impressora)
        hDC.StartDoc("Cupom PDV")
        hDC.StartPage()

        # Define a fonte. Impressoras térmicas funcionam melhor com fontes monoespaçadas.
        font = win32ui.CreateFont({
            "name": "Courier New",  # Fonte de largura fixa
            "height": 20,  # Tamanho da fonte (ajuste conforme o seu cupom)
            "weight": 400
        })
        hDC.SelectObject(font)

        # Imprime o texto linha por linha
        y = 20  # Posição Y inicial
        for linha in texto_cupom.split('\n'):
            hDC.TextOut(10, y, linha)  # (x, y, texto)
            y += 25  # Move para a próxima linha (ajuste se a fonte for maior/menor)

        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()  # Libera o recurso da impressora
        return True, "Impressão enviada com sucesso"
    except Exception as e:
        msg = f"Erro ao imprimir: {e}"
        print(msg)
        # Tenta limpar o DC em caso de falha
        try:
            hDC.DeleteDC()
        except:
            pass
        return False, msg