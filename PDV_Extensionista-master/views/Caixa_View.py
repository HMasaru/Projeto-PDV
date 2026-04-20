import customtkinter as ctk
from tkinter import ttk, Listbox, END

class CaixaView(ctk.CTkFrame):
    def __init__(self, master, caixa_controller, app_controller):
        super().__init__(master)
        self.caixa_controller = caixa_controller
        self.app_controller = app_controller
        self.pack(fill="both", expand=True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ===== MENU SUPERIOR =====
        menu_frame = ctk.CTkFrame(self, height=50)
        menu_frame.pack(fill="x", pady=(5, 10), padx=10)

        botoes_menu = ["Frente de Caixa", "Estoque", "Gerenciamento", "Sangria", "Relatório"]
        for texto in botoes_menu:
            if texto == "Relatório":
                ctk.CTkButton(menu_frame, text=texto, height=35, corner_radius=8,
                              command=self.app_controller.mostrar_relatorio).pack(side="left", padx=5)

            elif texto == "Estoque":
                ctk.CTkButton(menu_frame, text=texto, height=35, corner_radius=8,
                              command=self.app_controller.mostrar_estoque).pack(side="left", padx=5)

            elif texto == "Gerenciamento":
                ctk.CTkButton(menu_frame, text=texto, height=35, corner_radius=8,
                              command=self.app_controller.mostrar_gerenciamento).pack(side="left", padx=5)

            # === ALTERAÇÃO AQUI ===
            elif texto == "Sangria":
                ctk.CTkButton(menu_frame, text=texto, height=35, corner_radius=8,
                              command=self.caixa_controller.realizar_sangria).pack(side="left",
                                                                                   padx=5)  # Adiciona o command
            # ======================

            else:  # "Frente de Caixa"
                ctk.CTkButton(menu_frame, text=texto, height=35, corner_radius=8).pack(side="left", padx=5)

        ctk.CTkButton(menu_frame, text="⚙ Impressora", height=35, corner_radius=8,
                      command=self.caixa_controller.abrir_config_impressora).pack(side="right", padx=5)
        # ===== FRAME DE PESQUISA =====
        frame_pesquisa = ctk.CTkFrame(self)
        frame_pesquisa.pack(fill="x", padx=20, pady=(0, 5))

        self.entry_pesquisa = ctk.CTkEntry(
            frame_pesquisa,
            placeholder_text="Pesquise o produto ou código...",
            height=35,
            font=("Segoe UI", 14)
        )
        self.entry_pesquisa.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_pesquisa.bind('<KeyRelease>', self.caixa_controller.mostrar_sugestoes)
        self.entry_pesquisa.bind('<Return>', self.caixa_controller.selecionar_sugestao)

        self.venda_rapida_var = ctk.BooleanVar()
        self.check_venda_rapida = ctk.CTkCheckBox(frame_pesquisa, text="Venda Rápida", variable=self.venda_rapida_var, command=self.caixa_controller.venda_rapida)
        self.check_venda_rapida.pack(side="left", padx=10)

        # ===== LISTBOX DE SUGESTÕES =====
        self.frame_sugestoes = ctk.CTkFrame(self)
        self.frame_sugestoes.pack(fill="x", padx=20, pady=(0, 10))

        self.listbox_sugestoes = Listbox(
            self.frame_sugestoes,
            height=6,
            font=('Segoe UI', 13),
            bg="#2b2b2b",
            fg="white",
            selectbackground="#0078D4",
            relief="flat"
        )
        self.listbox_sugestoes.pack(fill="x", padx=2, pady=2)
        self.listbox_sugestoes.bind("<<ListboxSelect>>", self.caixa_controller.selecionar_sugestao)

        # ===== TABELA DE PRODUTOS =====
        frame_tabela = ctk.CTkFrame(self)
        frame_tabela.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        colunas = ("ID", "Produto", "R$", "Qtd")
        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=10)
        for col in colunas:
            self.tabela.heading(col, text=col)
            self.tabela.column(col, anchor="center", width=120)
        self.tabela.pack(fill="both", expand=True, pady=5)

        estilo = ttk.Style()
        estilo.theme_use("default")
        estilo.configure("Treeview",
                         background="#1E1E1E",
                         foreground="white",
                         rowheight=28,
                         fieldbackground="#1E1E1E",
                         font=("Segoe UI", 12))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"), background="#2E2E2E")
        estilo.map("Treeview", background=[("selected", "#0078D4")])

        # ===== ÁREA DE PAGAMENTO =====
        frame_pagamento = ctk.CTkFrame(self)
        frame_pagamento.pack(fill="x", padx=20, pady=(5, 0))

        frame_metodo = ctk.CTkFrame(frame_pagamento)
        frame_metodo.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(frame_metodo, text="Forma de Pagamento", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(5, 10))
        self.pag_dinheiro = ctk.BooleanVar()
        self.pag_pix = ctk.BooleanVar()
        self.pag_credito = ctk.BooleanVar()
        self.pag_debito = ctk.BooleanVar()
        ctk.CTkCheckBox(frame_metodo, text="Dinheiro", variable=self.pag_dinheiro, command=caixa_controller.ativar_dinheiro).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(frame_metodo, text="PIX", variable=self.pag_pix).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(frame_metodo, text="Crédito", variable=self.pag_credito).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(frame_metodo, text="Débito", variable=self.pag_debito).pack(anchor="w", pady=2)

        frame_valores = ctk.CTkFrame(frame_pagamento)
        frame_valores.pack(side="right", fill="x")

        ctk.CTkLabel(frame_valores, text="Total:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="e", padx=(10, 5), pady=5)
        self.entry_total = ctk.CTkEntry(frame_valores, width=150, justify="right", state='readonly')
        self.entry_total.grid(row=0, column=1, pady=5)

        ctk.CTkLabel(frame_valores, text="Recebido:", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, sticky="e", padx=(10, 5), pady=5)
        self.entry_recebido = ctk.CTkEntry(frame_valores, width=150, justify="right", state='readonly')
        self.entry_recebido.grid(row=1, column=1, pady=5)
        self.entry_recebido.bind("<FocusOut>", lambda e: self.caixa_controller.formatar_recebido())

        ctk.CTkLabel(frame_valores, text="Troco:", font=("Segoe UI", 14, "bold")).grid(row=2, column=0, sticky="e", padx=(10, 5), pady=5)
        self.entry_troco = ctk.CTkEntry(frame_valores, width=150, justify="right", state='readonly')
        self.entry_troco.grid(row=2, column=1, pady=5)

        self.entry_recebido.bind('<KeyRelease>', lambda e: self.caixa_controller.calcular_troco())

        # ===== BOTÕES =====
        frame_botoes = ctk.CTkFrame(self)
        frame_botoes.pack(fill="x", padx=20, pady=(15, 10))

        self.btn_finalizar = ctk.CTkButton(frame_botoes, text="Finalizar Venda", height=40, width=160, corner_radius=10, fg_color="#0078D4", command=caixa_controller.finalizar_venda)
        self.btn_finalizar.pack(side="right", padx=5)
        self.btn_cancelar = ctk.CTkButton(frame_botoes, text="Cancelar", height=40, width=160, corner_radius=10, fg_color="#D32F2F", command=caixa_controller.cancelar_venda)
        self.btn_cancelar.pack(side="right", padx=5)

    # Quando clicar em uma sugestão
    def on_select_sugestao(self, event):
        selecao = self.listbox_sugestoes.curselection()
        if selecao:
            texto = self.listbox_sugestoes.get(selecao)
            self.entry_pesquisa.delete(0, END)
            self.entry_pesquisa.insert(0, texto)
            self.listbox_sugestoes.delete(0, END)
