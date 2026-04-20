import re
from tkinter import messagebox, simpledialog

from Utils.NFCe import NotaFiscal
from models.Produto_Model import ProdutoModel
from models.Caixa_Model import CaixaModel
from views.Caixa_View import CaixaView

from views.Impressora_View import ConfigImpressoraView
import Utils.Impressao as Impressao
from datetime import datetime


class CaixaController:
    def __init__(self, root, app_controller=None, usuario_logado=None):
        self.app_controller = app_controller
        self.model_caixa = CaixaModel()
        self.model_produto = ProdutoModel()
        self.usuario_logado = usuario_logado
        self.id_usuario = self.usuario_logado['id_usuario'] if self.usuario_logado else None
        self.view = CaixaView(root, self, app_controller)

        # 1. Tente obter um caixa JÁ ABERTO para este usuário.
        #    (Estou assumindo que 'get_caixa_atual' faz isso:
        #     procura um caixa com status='aberto' para este id_usuario)
        try:
            self.caixa_id = self.model_caixa.get_caixa_atual(self.id_usuario)
        except Exception as e:
            messagebox.showerror("Erro de Banco", f"Erro ao verificar caixa atual:\n{e}")
            # Decida o que fazer aqui, talvez voltar ao login
            if self.app_controller:
                self.app_controller.mostrar_login()
            return  # Impede a execução do resto do código

        # 2. Se um ID foi retornado, significa que já existe um caixa aberto.
        if self.caixa_id:
            # Apenas informamos que o caixa foi "recarregado" na sessão
            messagebox.showinfo("Caixa Reaberto",
                                f"Caixa (ID: {self.caixa_id}) já estava aberto e foi recarregado.")

        # 3. Se self.caixa_id for None, significa que NÃO há caixa aberto.
        #    Portanto, DEVEMOS ABRIR UM NOVO.
        else:
            # Perguntar o valor de abertura
            valor_abertura = simpledialog.askfloat(
                "Abrir Caixa",
                f"Usuário: {self.usuario_logado['nome']}\n\n"
                "Nenhum caixa aberto encontrado.\n"
                "Qual o valor inicial em caixa (fundo de troco)?",
                parent=self.view.master
            )

            # 4. Verificar se o usuário clicou em 'Cancelar'
            if valor_abertura is None:
                messagebox.showwarning("Abertura Cancelada",
                                       "O caixa não foi aberto. Voltando para a tela de login.")
                if self.app_controller:
                    self.app_controller.mostrar_login()
                return  # Sai da função

            # 5. Se o usuário inseriu um valor, tentamos abrir o caixa
            #    Assumimos que 'abrir_caixa' CRIA o registro no banco e retorna o ID
            try:
                self.caixa_id = self.model_caixa.abrir_caixa(self.id_usuario, valor_abertura)
            except Exception as e:
                messagebox.showerror("Erro de Banco", f"Erro ao criar novo caixa:\n{e}")
                self.caixa_id = None  # Garante que o ID é nulo após o erro

            # 6. Verificar se a abertura (criação) no banco foi bem-sucedida
            if self.caixa_id:
                messagebox.showinfo("Caixa Aberto",
                                    f"Novo caixa (ID: {self.caixa_id}) foi aberto com R${valor_abertura:.2f}")
            else:
                # Se 'abrir_caixa' falhou e retornou None
                messagebox.showerror("Erro Crítico",
                                     "Não foi possível criar um novo caixa. Verifique o console ou logs.")
                if self.app_controller:
                    self.app_controller.mostrar_login()
    # --------------------------
    # Sugestões / pesquisa
    # --------------------------
    def mostrar_sugestoes(self, event=None):
        termo = self.view.entry_pesquisa.get().strip()
        if "*" in termo:
            partes = termo.split("*", 1)
            termo = partes[1].strip()
        self.view.listbox_sugestoes.delete(0, 'end')
        if termo == '':
            self.view.listbox_sugestoes.place_forget()
            return

        # usar model_produto.pesquisar
        resultados = self.model_produto.pesquisar(termo)
        if resultados:
            for r in resultados:
                # resultado é dict (id_produto, nome, preco_venda, quantidade_estoque)
                id_produto = r.get("id_produto") if isinstance(r, dict) else r[0]
                nome = r.get("nome") if isinstance(r, dict) else r[1]
                preco = r.get("preco_venda") if isinstance(r, dict) else r[2]
                self.view.listbox_sugestoes.insert('end', f'{id_produto} - {nome} - R${preco}')
            x = self.view.entry_pesquisa.winfo_rootx() - self.view.winfo_rootx()
            y = (self.view.entry_pesquisa.winfo_rooty() - self.view.winfo_rooty()) + self.view.entry_pesquisa.winfo_height()
            self.view.listbox_sugestoes.place(x=x, y=y, width=self.view.entry_pesquisa.winfo_width())
        else:
            self.view.listbox_sugestoes.place_forget()

    def selecionar_sugestoes(self, event=None):
        if not self.view.listbox_sugestoes.curselection():
            return
        index = self.view.listbox_sugestoes.curselection()
        texto = self.view.listbox_sugestoes.get(index)
        self.view.entry_pesquisa.delete(0, 'end')
        self.view.entry_pesquisa.insert(0, texto)
        self.view.listbox_sugestoes.delete(0, 'end')

    def selecionar_sugestao(self, event=None):
        texto = self.view.entry_pesquisa.get().strip()
        qtd = 1
        if "*" in texto:
            partes = texto.split("*", 1)
            try:
                qtd = int(partes[0])
                texto = partes[1].strip()
            except ValueError:
                qtd = 1

        produto = None
        # pesquisar por id ou nome usando model_produto
        if texto.isdigit():
            produto = self.model_produto.buscar_produto_por_id(int(texto))
        else:
            resultados = self.model_produto.pesquisar(texto)
            if resultados:
                # pegar o primeiro resultado (pode ser dict)
                r = resultados[0]
                if isinstance(r, dict):
                    produto = {
                        "id_produto": r.get("id_produto"),
                        "nome": r.get("nome"),
                        "preco_venda": r.get("preco_venda"),
                        "quantidade_estoque": r.get("quantidade_estoque")
                    }
                else:
                    produto = {"id_produto": r[0], "nome": r[1], "preco_venda": r[2]}

        if not produto:
            print("Produto não encontrado:", texto)
            return

        # adaptar para o formato que adicionar_tabela espera (id, nome, preco_venda)
        produto_padrao = {
            "id": produto.get("id_produto") or produto.get("id") or produto.get("id_produto"),
            "nome": produto.get("nome"),
            "preco_venda": produto.get("preco_venda")
        }

        self.adicionar_tabela(produto_padrao, qtd)
        self.view.entry_pesquisa.delete(0, "end")
        self.view.listbox_sugestoes.delete(0, "end")
        self.view.listbox_sugestoes.place_forget()

    # --------------------------
    # UI helpers
    # --------------------------
    def ativar_dinheiro(self):
        if self.view.pag_dinheiro.get():
            self.view.entry_recebido.configure(state='normal')
        else:
            self.view.entry_recebido.configure(state='readonly')
            self.view.entry_recebido.delete(0, 'end')
            self.view.entry_troco.configure(state='normal')
            self.view.entry_troco.delete(0, 'end')
            self.view.entry_troco.insert(0, 'R$0')
            self.view.entry_troco.configure(state='readonly')

    def adicionar_tabela(self, produto, qtd=1):
        id_produto = produto["id"]
        nome = produto["nome"]
        # converte para inteiro (você mencionou que não quer centavos)
        preco_venda = int(float(produto["preco_venda"]))
        subtotal = preco_venda * qtd
        for item in self.view.tabela.get_children():
            valores = self.view.tabela.item(item, "values")
            if str(valores[0]) == str(id_produto):
                qtd_existente = int(valores[3])
                nova_qtd = qtd_existente + qtd
                self.view.tabela.item(item, values=(id_produto, nome, preco_venda, nova_qtd))
                self.atualizar_total(preco_venda * qtd)
                return
        total_item = preco_venda * qtd
        self.view.tabela.insert('', 'end', values=(id_produto, nome, preco_venda, qtd))
        self.atualizar_total(total_item)

    def atualizar_total(self, valor):
        total = self.view.entry_total.get().strip()
        total = re.sub(r'^R\$', '', total)
        if total == '':
            total = '0'
        if re.fullmatch(r'[\d+\-*/(). ]+', total):
            try:
                resultado = eval(total, {"__builtins__": None}, {})
            except Exception:
                resultado = 0
        else:
            resultado = 0
        novo_total = resultado + int(valor)
        self.view.entry_total.configure(state='normal')
        self.view.entry_total.delete(0, 'end')
        self.view.entry_total.insert(0, f'R${novo_total}')
        self.view.entry_total.configure(state='readonly')

    def venda_rapida(self):
        if self.view.check_venda_rapida.get():
            self.view.entry_total.configure(state='normal')
            if self.view.pag_dinheiro.get():
                self.view.entry_recebido.configure(state='normal')
            self.view.entry_total.bind("<Return>", self.calcular_total_manual)
        else:
            self.view.entry_total.configure(state='readonly')
            self.view.entry_recebido.configure(state='readonly')
            self.view.entry_total.unbind("<Return>")

    def calcular_total_manual(self, event=None):
        texto = re.sub(r'[^0-9+\-*/().]', '', self.view.entry_total.get())
        try:
            resultado = eval(re.sub(r'[^0-9+\-*/().]', '', texto))
            self.view.entry_total.delete(0, 'end')
            self.view.entry_total.insert(0, f'R${int(resultado)}')
        except Exception:
            pass

    # =============================================================
    # FINALIZAR VENDA (AJUSTADO PARA MODELS)
    # =============================================================
    def finalizar_venda(self):
        formas = []
        if self.view.pag_dinheiro.get(): formas.append("Dinheiro")
        if self.view.pag_pix.get(): formas.append("Pix")
        if self.view.pag_credito.get(): formas.append("Crédito")
        if self.view.pag_debito.get(): formas.append("Débito")
        if not formas:
            messagebox.showwarning("Atenção", "Selecione uma forma de pagamento antes de finalizar!")
            return
        try:
            total_str = self.view.entry_total.get().replace('R$', '').strip()
            total = float(total_str)
            if total <= 0:
                messagebox.showwarning("Atenção", "Nenhum valor para finalizar!")
                return
        except ValueError:
            messagebox.showwarning("Atenção", "Nenhum valor para finalizar!")
            return

        # Pega os valores de troco e recebido ANTES
        try:
            troco_str = re.sub(r'[^0-9.]', '', self.view.entry_troco.get()) or '0'
            recebido_str = re.sub(r'[^0-9.]', '', self.view.entry_recebido.get()) or '0'
            troco = float(troco_str)
            recebido = float(recebido_str)
        except Exception:
            troco = 0
            recebido = 0

        pagamentos = {}

        if len(formas) > 1:
            restante = total
            for f in formas:
                valor = simpledialog.askfloat(
                    title="Dividir Pagamento",
                    prompt=f"Total: R${total:.2f}\n\nQuanto será pago em {f}?\nRestante: R${restante:.2f}",
                    parent=self.view.master
                )
                if valor is None:
                    messagebox.showinfo("Cancelado", "Divisão de pagamento cancelada.")
                    return
                pagamentos[f] = valor
                restante -= valor
            if abs(sum(pagamentos.values()) - total) > 0.01:
                messagebox.showerror("Erro", "A soma dos valores não confere com o total!")
                return

        elif len(formas) == 1 and formas[0] == "Dinheiro":
            if recebido > 0 and recebido >= total:
                pagamentos["Dinheiro"] = recebido
            else:
                pagamentos["Dinheiro"] = total
        else:
            pagamentos[formas[0]] = total

        itens_para_cupom = []
        for item in self.view.tabela.get_children():
            valores_str = self.view.tabela.item(item, "values")
            try:
                itens_para_cupom.append((
                    int(valores_str[0]), str(valores_str[1]), float(valores_str[2]), int(valores_str[3])
                ))
            except Exception as e:
                print(f"Erro ao ler item da tabela para cupom: {e}")

        # (Retirar do estoque) — usa model_produto.retirar_do_estoque
        for item in itens_para_cupom:
            id_produto, nome, preco, qtd = item
            try:
                self.model_produto.retirar_do_estoque(id_produto, int(qtd))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar estoque do produto {nome}: {e}")
                return

        # (Limpar tabela)
        for item in self.view.tabela.get_children():
            self.view.tabela.delete(item)

        resumo = "\n".join([f"{f}: R${v:.2f}" for f, v in pagamentos.items()])
        messagebox.showinfo("Venda Finalizada", f"Venda finalizada com sucesso!\n\n{resumo}\n\nTotal: R${total:.2f}")

        # (Impressão do Cupom)
        try:
            texto_cupom = self._gerar_texto_cupom(pagamentos, total, itens_para_cupom, troco)
            sucesso, msg = Impressao.imprimir_cupom(texto_cupom)
            if not sucesso:
                messagebox.showwarning("Erro de Impressão",
                                       f"A venda foi salva, mas falhou ao imprimir o cupom.\n\nErro: {msg}\n\nVerifique a impressora.",
                                       parent=self.view.master)
        except Exception as e:
            messagebox.showerror("Erro Fatal de Impressão", f"Ocorreu um erro ao tentar gerar o cupom: {e}",
                                 parent=self.view.master)

        # (Atualizar totais do caixa) usando model_caixa.atualizar_totais_caixa
        for forma, valor in pagamentos.items():
            if forma == "Dinheiro" and troco > 0:
                valor_a_salvar = float(valor) - float(troco)
            else:
                valor_a_salvar = float(valor)

            atualizou = self.model_caixa.atualizar_totais_caixa(self.caixa_id, forma, valor_a_salvar)
            if not atualizou:
                print(f"ERRO - Falha ao atualizar total para {forma} no caixa {self.caixa_id}")

        # Reset UI
        self.view.entry_total.configure(state='normal')
        self.view.entry_total.delete(0, 'end')
        self.view.entry_total.insert(0, 'R$0')
        self.view.entry_total.configure(state='readonly')
        self.view.entry_troco.configure(state='normal')
        self.view.entry_troco.delete(0, 'end')
        self.view.entry_troco.insert(0, 'R$0')
        self.view.entry_troco.configure(state='readonly')
        self.view.entry_recebido.configure(state='normal')
        self.view.entry_recebido.delete(0, 'end')
        self.view.entry_recebido.insert(0, 'R$0')
        self.view.entry_recebido.configure(state='readonly')
        self.view.pag_dinheiro.set(False)
        self.view.pag_pix.set(False)
        self.view.pag_credito.set(False)
        self.view.pag_debito.set(False)
        self.view.venda_rapida_var.set(False)

        # === NFC-e (mantive sua lógica) ===
        nf = NotaFiscal()
        itens_api = []
        if not itens_para_cupom:
            itens_api.append({"codigo": "1", "descricao": "VENDA MANUAL", "valor": total})
        else:
            itens_api = [
                {"codigo": i[0], "descricao": i[1], "valor": (float(i[2]) * int(i[3]))}
                for i in itens_para_cupom
            ]

        pagamentos_api = []
        for forma, valor in pagamentos.items():
            meio = "01"
            if forma.lower() == "pix":
                meio = "17"
            elif forma.lower() == "crédito" or forma.lower() == "credito":
                meio = "03"
            elif forma.lower() == "débito" or forma.lower() == "debito":
                meio = "04"
            pagamentos_api.append({"meio": meio, "valor": valor})

        troco_final_para_api = 0
        if len(formas) == 1 and formas[0] == "Dinheiro":
            troco_final_para_api = troco

        sucesso, resposta = nf.emitir_nota(
            venda_id=self.caixa_id,
            itens=itens_api,
            pagamentos=pagamentos_api,
            troco=troco_final_para_api
        )

        if sucesso:
            messagebox.showinfo("NFC-e", "Nota fiscal enviada com sucesso!")
        else:
            messagebox.showwarning("Erro NFC-e", f"Falha ao emitir nota:\n{resposta}")

    # ---------------------------
    # Cancelar venda / sangria / etc
    # ---------------------------
    def cancelar_venda(self):
        try:
            for item in self.view.tabela.get_children():
                self.view.tabela.delete(item)
            self.view.entry_total.configure(state='normal')
            self.view.entry_total.delete(0, 'end')
            self.view.entry_total.insert(0, 'R$0')
            self.view.entry_total.configure(state='readonly')
            self.view.entry_recebido.configure(state='normal')
            self.view.entry_recebido.delete(0, 'end')
            self.view.entry_recebido.insert(0, 'R$0')
            self.view.entry_recebido.configure(state='readonly')
            self.view.entry_troco.configure(state='normal')
            self.view.entry_troco.delete(0, 'end')
            self.view.entry_troco.insert(0, 'R$0')
            self.view.entry_troco.configure(state='readonly')
            self.view.pag_dinheiro.set(False)
            self.view.pag_pix.set(False)
            self.view.pag_credito.set(False)
            self.view.pag_debito.set(False)
            self.view.venda_rapida_var.set(False)
            print("Venda cancelada. Campos limpos.")
        except Exception as e:
            print(f"Erro ao cancelar venda: {e}")
            messagebox.showerror("Erro", "Não foi possível cancelar a venda.")

    def calcular_troco(self):
        try:
            if not self.view.pag_dinheiro.get():
                self.view.entry_troco.configure(state='normal')
                self.view.entry_troco.delete(0, 'end')
                self.view.entry_troco.insert(0, 'R$0')
                self.view.entry_troco.configure(state='readonly')
                return
            total = float(re.sub(r'[^0-9.]', '', self.view.entry_total.get()) or 0)
            recebido = float(re.sub(r'[^0-9.]', '', self.view.entry_recebido.get()) or 0)
            troco = max(recebido - total, 0)
            self.view.entry_troco.configure(state='normal')
            self.view.entry_troco.delete(0, 'end')
            self.view.entry_troco.insert(0, f'R${troco:.0f}')
            self.view.entry_troco.configure(state='readonly')
        except Exception:
            pass

    def formatar_recebido(self):
        valor = self.view.entry_recebido.get().strip().replace("R$", "").replace(",", ".")
        if valor:
            try:
                valor = float(valor)
                self.view.entry_recebido.delete(0, 'end')
                self.view.entry_recebido.insert(0,
                                                f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            except ValueError:
                pass

    def realizar_sangria(self):
        valor = simpledialog.askfloat(
            "Sangria de Caixa",
            "Qual o valor que está sendo retirado do caixa?",
            parent=self.view.master
        )
        if valor is None or valor <= 0:
            return
        motivo = simpledialog.askstring(
            "Motivo da Sangria",
            f"Qual o motivo da retirada de R${valor:.2f}?\n(Ex: 'malote', 'cofre', 'troco')",
            parent=self.view.master
        )
        if motivo is None or motivo.strip() == "":
            return
        sucesso = self.model_caixa.registrar_sangria(
            self.caixa_id,
            self.id_usuario,
            valor,
            motivo.strip()
        )
        if sucesso:
            messagebox.showinfo("Sucesso", f"Sangria de R${valor:.2f} registrada com sucesso.")
        else:
            messagebox.showerror("Erro", "Não foi possível registrar a sangria. Verifique o console.")

    def abrir_config_impressora(self):
        config_window = ConfigImpressoraView(self.view.master)
        config_window.wait_window()

    def _gerar_texto_cupom(self, pagamentos, total, itens_venda, troco):
        loja = "NOME DA SUA LOJA"
        cnpj = "CNPJ: XX.XXX.XXX/0001-XX"
        endereco = "Rua X, 123 - Bairro - Cidade/UF"
        LARGURA = 48
        texto = f"{loja.center(LARGURA)}\n"
        texto += f"{cnpj.center(LARGURA)}\n"
        texto += f"{endereco.center(LARGURA)}\n"
        texto += "-" * LARGURA + "\n"
        texto += "              CUPOM NAO FISCAL              \n"
        texto += "-" * LARGURA + "\n"
        data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        texto += f"{data_hora.ljust(LARGURA // 2)} Caixa: {str(self.caixa_id).rjust(LARGURA // 2 - 7)}\n"
        if self.usuario_logado:
            texto += f"Vendedor: {self.usuario_logado['nome']}\n"
        texto += "-" * LARGURA + "\n"

        if not itens_venda:
            texto += "VENDA MANUAL".ljust(25) + f"R$ {total:.2f}".rjust(LARGURA - 25) + "\n"
        else:
            texto += "PRODUTO                   QTD  VL. UNIT.   VL. TOTAL\n"
            for item in itens_venda:
                nome = item[1][:23].ljust(23)
                qtd = str(item[3]).center(5)
                vl_unit = f"{item[2]:.2f}".rjust(9)
                vl_total = f"{(item[2] * item[3]):.2f}".rjust(10)
                texto += f"{nome} {qtd} {vl_unit} {vl_total}\n"

        texto += "=" * LARGURA + "\n"
        texto += f"TOTAL A PAGAR:".ljust(25) + f"R$ {total:.2f}".rjust(LARGURA - 25) + "\n\n"
        texto += "Forma(s) de Pagamento:\n"
        for forma, valor in pagamentos.items():
            texto += f" - {forma}:".ljust(25) + f"R$ {valor:.2f}".rjust(LARGURA - 25) + "\n"
        if troco > 0:
            texto += f"Troco (Dinheiro):".ljust(25) + f"R$ {troco:.2f}".rjust(LARGURA - 25) + "\n"
        texto += "\n\n"
        texto += "Obrigado, volte sempre!".center(LARGURA) + "\n\n"
        texto += "\n\n\n\n\n"
        return texto
