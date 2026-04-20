import customtkinter as ctk
from tkinter import ttk


class GerenciamentoView(ctk.CTkFrame):
    def __init__(self, master, controller, app_controller):
        super().__init__(master)
        self.controller = controller
        self.app_controller = app_controller
        self.pack(fill="both", expand=True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # === CABEÇALHO ===
        header = ctk.CTkFrame(self, height=70, fg_color="#1C1C1C", corner_radius=10)
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="👤 Gerenciamento de Usuários",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkButton(
            header,
            text="Voltar ao Caixa",
            corner_radius=10,
            height=45,
            width=150,
            command=self.app_controller.mostrar_caixa
        ).pack(side="right", padx=20, pady=10)

        # === CONTAINER PRINCIPAL (dividido em 2) ===
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)  # Tabela
        main_frame.grid_columnconfigure(1, weight=1)  # Formulário
        main_frame.grid_rowconfigure(0, weight=1)

        # === FRAME DA TABELA (Esquerda) ===
        frame_tabela = ctk.CTkFrame(main_frame)
        frame_tabela.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        colunas = ("ID", "Nome", "Login", "Cargo")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        for col in colunas:
            self.tabela.heading(col, text=col)
            if col == "ID":
                self.tabela.column(col, anchor="center", width=50)
            else:
                self.tabela.column(col, anchor="w", width=180)

        self.tabela.pack(fill="both", expand=True, padx=10, pady=10)

        # Estilo
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#1E1E1E", foreground="white", rowheight=28, fieldbackground="#1E1E1E",
                         font=("Segoe UI", 12))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#2E2E2E")
        estilo.map("Treeview", background=[("selected", "#0078D4")])

        self.btn_deletar = ctk.CTkButton(
            frame_tabela,
            text="Deletar Usuário Selecionado",
            command=self.controller.deletar_usuario_selecionado,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        self.btn_deletar.pack(pady=10, padx=10, fill="x")

        # === FRAME DO FORMULÁRIO (Direita) ===
        frame_form = ctk.CTkFrame(main_frame)
        frame_form.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(frame_form, text="Adicionar Novo Usuário", font=("Segoe UI", 18, "bold")).pack(pady=(20, 10))

        self.entry_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome Completo", width=250)
        self.entry_nome.pack(pady=10, padx=20)

        self.entry_login = ctk.CTkEntry(frame_form, placeholder_text="Login (usuário)", width=250)
        self.entry_login.pack(pady=10, padx=20)

        self.entry_senha = ctk.CTkEntry(frame_form, placeholder_text="Senha", width=250, show="*")
        self.entry_senha.pack(pady=10, padx=20)

        # Opção de Cargo (Admin ou Funcionário)
        self.cargo_var = ctk.StringVar(value="Funcionario")
        ctk.CTkLabel(frame_form, text="Cargo:").pack(pady=(10, 0))
        ctk.CTkSegmentedButton(frame_form,
                               values=["Funcionario", "Admin"],
                               variable=self.cargo_var).pack(pady=5)

        self.btn_salvar = ctk.CTkButton(frame_form, text="Salvar Novo Usuário", command=self.controller.salvar_usuario)
        self.btn_salvar.pack(pady=20, padx=20, ipady=5)