import customtkinter as ctk


class CadastroView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="Cadastro de Usuário", font=("Arial", 22, "bold")).pack(pady=20)

        # === CAMPO NOME ADICIONADO ===
        self.nome = ctk.CTkEntry(self, placeholder_text="Nome Completo")
        self.nome.pack(pady=10)

        self.user = ctk.CTkEntry(self, placeholder_text="Usuário (Login)")
        self.user.pack(pady=10)

        self.password = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.password.pack(pady=10)

        self.repassword = ctk.CTkEntry(self, placeholder_text="Repetir Senha", show="*")
        self.repassword.pack(pady=10)

        # === COMANDO ATUALIZADO ===
        ctk.CTkButton(self, text="Cadastrar", command=self.controller.realizar_cadastro).pack(pady=10)
        ctk.CTkButton(self, text="Voltar", command=self.controller.mostrar_login).pack(pady=10)