from tkinter import messagebox
import Utils.Impressao as Impressao
from datetime import datetime

class RelatorioController:
    def __init__(self, view=None, model=None, usuario_logado=None):
        self.view = view
        self.model = model
        self.usuario_logado = usuario_logado  # Salva o usuário

    def atualizar_relatorio(self):
        totais_dia, totais_mes = self.model.obter_totais()
        if self.view:
            self.view.atualizar_dados(totais_dia, totais_mes)

    def _gerar_relatorio_fechamento(self, totais_dia, totais_mes):
        LARGURA = 48
        texto = "RELATORIO DE FECHAMENTO DE CAIXA".center(LARGURA) + "\n"
        texto += "=" * LARGURA + "\n"
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        texto += f"Data/Hora: {data_hora}\n"

        if self.usuario_logado:
            texto += f"Fechado por: {self.usuario_logado['nome']}\n"

        texto += "=" * LARGURA + "\n\n"
        texto += "--- TOTAIS DO DIA (Caixas Abertos) ---\n"

        total_dia_geral = 0
        for forma, valor in totais_dia.items():
            texto += f" {forma}:".ljust(25) + f"R$ {valor:.2f}".rjust(LARGURA - 25) + "\n"
            total_dia_geral += valor

        texto += "-" * LARGURA + "\n"
        texto += " TOTAL DO DIA:".ljust(25) + f"R$ {total_dia_geral:.2f}".rjust(LARGURA - 25) + "\n"
        texto += "=" * LARGURA + "\n\n"

        texto += "--- TOTAIS DO MES (Acumulado) ---\n"
        total_mes_geral = 0
        for forma, valor in totais_mes.items():
            texto += f" {forma}:".ljust(25) + f"R$ {valor:.2f}".rjust(LARGURA - 25) + "\n"
            total_mes_geral += valor

        texto += "-" * LARGURA + "\n"
        texto += " TOTAL DO MES:".ljust(25) + f"R$ {total_mes_geral:.2f}".rjust(LARGURA - 25) + "\n"
        texto += "=" * LARGURA + "\n\n\n\n\n"
        return texto

    def encerrar_dia(self):
        totais_dia, totais_mes = self.model.obter_totais()
        sucesso = self.model.encerrar_dia()

        if sucesso:
            try:
                texto_relatorio = self._gerar_relatorio_fechamento(totais_dia, totais_mes)
                impr_sucesso, msg = Impressao.imprimir_cupom(texto_relatorio)

                if not impr_sucesso:
                    messagebox.showwarning(
                        "Erro de Impressão",
                        f"O caixa foi fechado, mas falhou ao imprimir o relatório.\n\nErro: {msg}\n\nVerifique a impressora.",
                        parent=self.view.master
                    )
                else:
                    messagebox.showinfo(
                        "Sucesso",
                        "Caixa encerrado e relatório enviado para a impressora."
                    )
            except Exception as e:
                messagebox.showerror(
                    "Erro Fatal de Impressão",
                    f"O caixa foi fechado, mas ocorreu um erro ao gerar o relatório: {e}",
                    parent=self.view.master
                )
            self.atualizar_relatorio()
        else:
            self.view.exibir_mensagem("⚠ Erro ao encerrar o caixa.")
