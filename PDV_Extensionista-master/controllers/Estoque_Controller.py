from tkinter import messagebox
from models.Produto_Model import ProdutoModel
from Utils.NFCe import NotaFiscal


class EstoqueController:
    def __init__(self, view=None, app_controller=None):
        self.view = view
        self.app_controller = app_controller
        self.model = ProdutoModel()

    def carregar_produtos(self):
        """Pede ao Model a lista de produtos e os exibe na tabela da View."""
        if not self.view:
            return

        # Limpa a tabela antes de carregar
        for item in self.view.tabela.get_children():
            self.view.tabela.delete(item)

        # Busca produtos no Model
        produtos = self.model.listar_todos_produtos()

        # Insere na tabela (View)
        for p in produtos:
            # (id, nome, preco, qtd)
            self.view.tabela.insert('', 'end', values=(
                p['id_produto'],
                p['nome'],
                f"{p['preco_venda']:.2f}",  # Formata para R$
                p['quantidade_estoque']
            ))

    def salvar_produto(self):
        """Pega os dados do formulário, valida e manda para o Model salvar."""
        if not self.view:
            return

        nome = self.view.entry_nome.get().strip()
        preco_str = self.view.entry_preco.get().strip().replace(",", ".")  # Aceita vírgula
        qtd_str = self.view.entry_qtd.get().strip()

        # Validação
        if not nome or not preco_str or not qtd_str:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios.")
            return

        try:
            preco_venda = float(preco_str)
            quantidade = int(qtd_str)
        except ValueError:
            messagebox.showerror("Erro", "Preço e Quantidade devem ser números válidos.")
            return

        if preco_venda <= 0 or quantidade < 0:
            messagebox.showerror("Erro", "Valores numéricos devem ser positivos.")
            return

        # Envia para o Model
        sucesso = self.model.adicionar_novo_produto(nome, preco_venda, quantidade)

        if sucesso:
            messagebox.showinfo("Sucesso", f"Produto '{nome}' cadastrado!")
            # Limpa o formulário
            self.view.entry_nome.delete(0, 'end')
            self.view.entry_preco.delete(0, 'end')
            self.view.entry_qtd.delete(0, 'end')
            # Recarrega a lista
            self.carregar_produtos()
        else:
            messagebox.showerror("Erro", f"Produto '{nome}' já existe no banco de dados.")

    def deletar_produto_selecionado(self):
        """Deleta o produto que está selecionado na tabela."""
        if not self.view:
            return

        # Pega o item selecionado
        try:
            item_selecionado = self.view.tabela.focus()
            if not item_selecionado:
                messagebox.showerror("Erro", "Selecione um produto na tabela para deletar.")
                return

            # Pega os dados da linha (o ID é o primeiro valor)
            dados = self.view.tabela.item(item_selecionado, "values")
            id_produto = dados[0]
            nome_produto = dados[1]

            # Pede confirmação
            if not messagebox.askyesno("Confirmar Exclusão",
                                       f"Tem certeza que deseja deletar o produto:\n\n{nome_produto} (ID: {id_produto})?"):
                return

            # Manda para o Model deletar
            resultado = self.model.deletar_produto(id_produto)

            if resultado == True:
                messagebox.showinfo("Sucesso", "Produto deletado com sucesso.")
                self.carregar_produtos()  # Atualiza a tabela
            elif resultado == "em_venda":
                messagebox.showerror("Erro",
                                     "Este produto não pode ser excluído pois já faz parte de vendas registradas.")
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao deletar o produto.")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")