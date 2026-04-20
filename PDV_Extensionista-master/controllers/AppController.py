from tkinter import messagebox #importação da caixa de diálogo

#importação view
from views.Login_View import LoginView
from views.Cadastro_View import CadastroView
from views.Estoque_View import EstoqueView
from views.Gerenciamento_View import GerenciamentoView
from views.Relatório_View import RelatorioView

#importação controller
from controllers.Caixa_Controller import CaixaController
from controllers.Estoque_Controller import EstoqueController
from controllers.Gerenciamento_Controller import GerenciamentoController
from controllers.Relatório_Controller import RelatorioController

#importação model
from models.Login_Model import LoginModel
from models.Produto_Model import ProdutoModel
from models.Relatório_Model import RelatorioModel


class AppController:
    def __init__(self, root):
        self.root = root  # master
        self.frame_atual = None  # transsição de frames
        self.login_model = LoginModel()  # instância do LoginModel
        self.usuario_logado = None  # Guarda os dados do usuário após o login
        self.mostrar_login()
        self.registrar_atalhos()


    def limpar_tela(self):
        #Destrói o frame atual para exibir um novo
        if self.frame_atual:
            self.frame_atual.pack_forget()
            self.frame_atual.destroy()

    def mostrar_login(self):
        #"Exibe a tela de login.
        self.limpar_tela()
        self.frame_atual = LoginView(self.root, self)
        self.frame_atual.pack(fill='both', expand=True)

    def mostrar_cadastro(self):
        #Exibe a tela de cadastro de usuário.
        self.limpar_tela()
        self.frame_atual = CadastroView(self.root, self)
        self.frame_atual.pack(fill='both', expand=True)

    def mostrar_caixa(self):
        #Exibe a tela principal do PDV (Caixa).
        self.limpar_tela()

        caixa_controller = CaixaController(self.root, self, self.usuario_logado)

        self.frame_atual = caixa_controller.view
        self.frame_atual.pack(fill='both', expand=True)

    def mostrar_relatorio(self):
        """Exibe a tela de Relatórios."""
        self.limpar_tela()

        relatorio_model = RelatorioModel()

        relatorio_controller = RelatorioController(
            view=None,
            model=RelatorioModel(),
            usuario_logado=self.usuario_logado  # <-- garante que o relatório saiba quem é
        )

        self.frame_atual = RelatorioView(self.root, relatorio_controller, self)
        relatorio_controller.view = self.frame_atual
        self.frame_atual.pack(fill='both', expand=True)

    def mostrar_estoque(self):
        """Exibe a tela de Gerenciamento de Estoque."""
        self.limpar_tela()

        estoque_model = ProdutoModel()

        estoque_controller = EstoqueController(
            view=None,
            app_controller=self
        )

        view = EstoqueView(self.root, estoque_controller, self)
        estoque_controller.view = view

        self.frame_atual = view
        self.frame_atual.pack(fill='both', expand=True)

        estoque_controller.carregar_produtos()

    def mostrar_gerenciamento(self):
        """Exibe a tela de Gerenciamento de Usuários (Apenas Admin)."""
        self.limpar_tela()

        if not self.usuario_logado or self.usuario_logado.get('cargo') != 'Admin':
            messagebox.showerror("Acesso Negado", "Você precisa ser um Administrador para acessar esta área.")
            self.mostrar_caixa()
            return

        gerenciamento_controller = GerenciamentoController(view=None, app_controller=self)

        self.frame_atual = GerenciamentoView(self.root, gerenciamento_controller, self)
        gerenciamento_controller.view = self.frame_atual

        self.frame_atual.pack(fill='both', expand=True)

        gerenciamento_controller.carregar_usuarios()

    def realizar_login(self):
        """Valida o login e senha."""
        login = self.frame_atual.user.get()
        senha = self.frame_atual.password.get()

        if not login or not senha:
            messagebox.showwarning("Erro", "Preencha todos os campos.")
            return

        usuario = self.login_model.verificar_login(login, senha)

        if usuario:
            self.usuario_logado = usuario
            messagebox.showinfo("Login", f"Bem-vindo, {usuario['nome']}!")
            self.mostrar_caixa()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    def realizar_cadastro(self):
        """Cadastra um novo usuário."""
        nome = self.frame_atual.nome.get()
        login = self.frame_atual.user.get()
        senha = self.frame_atual.password.get()
        rep_senha = self.frame_atual.repassword.get()

        if not nome or not login or not senha or not rep_senha:
            messagebox.showwarning("Erro", "Preencha todos os campos.")
            return

        if senha != rep_senha:
            messagebox.showerror("Erro", "As senhas não conferem.")
            return

        resultado = self.login_model.cadastrar_usuario(nome, login, senha)

        if resultado == True:
            messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso! Faça o login.")
            self.mostrar_login()
        elif resultado == "login_existe":
            messagebox.showwarning("Erro", "Este nome de usuário (login) já existe.")
        else:
            messagebox.showerror("Erro", "Falha ao cadastrar usuário. Tente novamente.")

    def registrar_atalhos(self):
        print("[ATALHOS] Atalhos registrados: F1, F2, F3, F4, F5")

        self.root.bind("<F1>", lambda e: self.atalho_frente_caixa())
        self.root.bind("<F2>", lambda e: self.atalho_estoque())
        self.root.bind("<F3>", lambda e: self.atalho_relatorio())
        self.root.bind("<F4>", lambda e: self.atalho_gerenciamento())
        self.root.bind("<F5>", lambda e: self.atalho_voltar_login())
        self.root.bind("<F10>", lambda e: self.ativar_contigencia())

    def atalho_frente_caixa(self):
        if self.usuario_logado:
            self.mostrar_caixa()
        else:
            print("[ATALHO] Usuário não logado")

    def atalho_estoque(self):
        if self.usuario_logado:
            self.mostrar_estoque()
        else:
            print("[ATALHO] Usuário não logado")

    def atalho_relatorio(self):
        if self.usuario_logado:
            self.mostrar_relatorio()
        else:
            print("[ATALHO] Usuário não logado")

    def atalho_gerenciamento(self):
        if self.usuario_logado and self.usuario_logado["cargo"] == "Admin":
            self.mostrar_gerenciamento()
        else:
            print("[ATALHO] Acesso negado ou usuário não logado")

    def atalho_voltar_login(self):
        self.usuario_logado = None
        self.mostrar_login()