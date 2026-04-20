from tkinter import messagebox
from models.Login_Model import LoginModel


class GerenciamentoController:
    def __init__(self, view=None, app_controller=None):
        self.view = view
        self.app_controller = app_controller
        # Este controller usa o Login_Model, pois é lá que estão as funções
        self.model = LoginModel()
        self.id_usuario_logado = app_controller.usuario_logado['id_usuario']

    def carregar_usuarios(self):
        """Busca usuários no Model e os exibe na tabela da View."""
        if not self.view:
            return

        for item in self.view.tabela.get_children():
            self.view.tabela.delete(item)

        usuarios = self.model.listar_todos_usuarios()

        for u in usuarios:
            self.view.tabela.insert('', 'end', values=(
                u['id_usuario'],
                u['nome'],
                u['login'],
                u['cargo']
            ))

    def salvar_usuario(self):
        """Pega os dados do formulário e manda para o Model salvar."""
        if not self.view:
            return

        nome = self.view.entry_nome.get().strip()
        login = self.view.entry_login.get().strip()
        senha = self.view.entry_senha.get().strip()
        cargo = self.view.cargo_var.get()

        if not nome or not login or not senha:
            messagebox.showerror("Erro", "Nome, Login e Senha são obrigatórios.")
            return

        # Chama a função de cadastro do Login_Model
        resultado =self.model.cadastrar_usuario_com_cargo(nome, login, senha, cargo)

        if resultado == True:
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' cadastrado!")
            self.view.entry_nome.delete(0, 'end')
            self.view.entry_login.delete(0, 'end')
            self.view.entry_senha.delete(0, 'end')
            self.carregar_usuarios()  # Recarrega a lista
        elif resultado == "login_existe":
            messagebox.showerror("Erro", f"O login '{login}' já está em uso.")
        else:
            messagebox.showerror("Erro", "Falha ao cadastrar usuário.")

    def deletar_usuario_selecionado(self):
        """Deleta o usuário selecionado na tabela."""
        if not self.view:
            return

        try:
            item_selecionado = self.view.tabela.focus()
            if not item_selecionado:
                messagebox.showerror("Erro", "Selecione um usuário na tabela para deletar.")
                return

            dados = self.view.tabela.item(item_selecionado, "values")
            id_usuario = int(dados[0])
            nome_usuario = dados[1]

            # Proteção: Não deixa o usuário se auto-deletar
            if id_usuario == self.id_usuario_logado:
                messagebox.showerror("Ação Bloqueada", "Você não pode deletar a si mesmo.")
                return

            if not messagebox.askyesno("Confirmar Exclusão",
                                       f"Tem certeza que deseja deletar o usuário:\n\n{nome_usuario} (ID: {id_usuario})?"):
                return

            resultado = self.model.deletar_usuario(id_usuario)

            if resultado == True:
                messagebox.showinfo("Sucesso", "Usuário deletado com sucesso.")
                self.carregar_usuarios()
            elif resultado == "com_registros":
                messagebox.showerror("Erro",
                                     "Este usuário não pode ser excluído, pois possui vendas ou caixas associados.")
            else:
                messagebox.showerror("Erro", "Ocorreu um erro ao deletar o usuário.")

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")