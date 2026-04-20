import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, controller):
        print("[LoginView] __init__ iniciado.")
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="Login", font=("Arial", 22, "bold")).pack(pady=20)
        self.user = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.user.pack(pady=10)
        self.password = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.password.pack(pady=10)

        # === COMANDO ATUALIZADO ===
        ctk.CTkButton(self, text="Entrar", command = self.controller.realizar_login).pack(pady=10)
        ctk.CTkButton(self, text="Cadastrar", command = self.controller.mostrar_cadastro).pack(pady=10)