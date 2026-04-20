import customtkinter as ctk
from tkinter import ttk


class EstoqueView(ctk.CTkFrame):
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
            text="📦 Gerenciamento de Estoque",
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
        main_frame.grid_columnconfigure(0, weight=1)  # Frame da Tabela
        main_frame.grid_columnconfigure(1, weight=1)  # Frame do Formulário
        main_frame.grid_rowconfigure(0, weight=1)

        # === FRAME DA TABELA (Esquerda) ===
        frame_tabela = ctk.CTkFrame(main_frame)
        frame_tabela.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        colunas = ("ID", "Nome", "Preço (R$)", "Qtd. Estoque")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings")
        for col in colunas:
            self.tabela.heading(col, text=col)
            if col == "ID" or col == "Qtd. Estoque":
                self.tabela.column(col, anchor="center", width=80)
            elif col == "Preço (R$)":
                self.tabela.column(col, anchor="center", width=100)
            else:
                self.tabela.column(col, anchor="w", width=250)

        self.tabela.pack(fill="both", expand=True, padx=10, pady=10)

        # (Aplica o estilo escuro que você já usa)
        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview", background="#1E1E1E", foreground="white", rowheight=28, fieldbackground="#1E1E1E",
                         font=("Segoe UI", 12))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#2E2E2E")
        estilo.map("Treeview", background=[("selected", "#0078D4")])

        # === FRAME DO FORMULÁRIO (Direita) ===
        frame_form = ctk.CTkFrame(main_frame)
        frame_form.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(frame_form, text="Adicionar Novo Produto", font=("Segoe UI", 18, "bold")).pack(pady=(20, 10))

        self.entry_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome do Produto", width=250)
        self.entry_nome.pack(pady=10, padx=20)

        self.entry_preco = ctk.CTkEntry(frame_form, placeholder_text="Preço de Venda (ex: 25.00)", width=250)
        self.entry_preco.pack(pady=10, padx=20)

        self.entry_qtd = ctk.CTkEntry(frame_form, placeholder_text="Quantidade Inicial (ex: 100)", width=250)
        self.entry_qtd.pack(pady=10, padx=20)

        self.btn_salvar = ctk.CTkButton(frame_form, text="Salvar Novo Produto", command=self.controller.salvar_produto)
        self.btn_salvar.pack(pady=20, padx=20, ipady=5)

        self.btn_deletar = ctk.CTkButton(
            frame_form,
            text="Deletar Produto Selecionado",
            command=self.controller.deletar_produto_selecionado,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        self.btn_deletar.pack(pady=10, padx=20)