import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class RelatorioView(ctk.CTkFrame):
    def __init__(self, master, relatorio_controller, app_controller):
        super().__init__(master)
        self.app_controller = app_controller
        self.relatorio_controller = relatorio_controller
        self.pack(fill="both", expand=True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # === CABEÇALHO ===
        header = ctk.CTkFrame(self, height=70, fg_color="#1C1C1C", corner_radius=10)
        header.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="📊 Relatório de Vendas",
            font=("Segoe UI", 24, "bold"),
            text_color="#FFFFFF"
        ).pack(side="left", padx=20, pady=10)

        ctk.CTkButton(
            header,
            text="Encerrar Dia",
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            corner_radius=10,
            height=45,
            width=150,
            command=self.relatorio_controller.encerrar_dia
        ).pack(side="right", padx=20, pady=10)

        ctk.CTkButton(
            header,
            text="Voltar ao Caixa",
            corner_radius=10,
            height=45,
            width=150,
            command=self.app_controller.mostrar_caixa
        ).pack(side="right", padx=(0, 5), pady=10)

        # === CONTAINER PRINCIPAL ===
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        # === CARDS DE RESUMO ===
        frame_cards = ctk.CTkFrame(main_frame, fg_color="#252525", corner_radius=12)
        frame_cards.pack(fill="x", padx=5, pady=(10, 20))

        self.cards = {}
        cores = {"Dinheiro": "#4CAF50", "PIX": "#2196F3", "Crédito": "#FFC107", "Débito": "#9C27B0", "Total": "#607D8B"}

        for i, (titulo, cor) in enumerate(cores.items()):
            card = ctk.CTkFrame(frame_cards, fg_color=cor, corner_radius=10, width=150, height=100)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 15, "bold")).pack(pady=(10, 0))
            valor_label = ctk.CTkLabel(card, text="R$0,00", font=("Segoe UI", 20, "bold"))
            valor_label.pack(pady=(5, 5))
            self.cards[titulo] = valor_label
            frame_cards.grid_columnconfigure(i, weight=1)

        # === GRÁFICOS ===
        frame_graficos = ctk.CTkFrame(main_frame, fg_color="#1E1E1E", corner_radius=12)
        frame_graficos.pack(fill="both", expand=True, padx=5, pady=10)
        frame_graficos.columnconfigure((0, 1), weight=1)
        frame_graficos.rowconfigure(0, weight=1)

        # --- GRÁFICO DIÁRIO ---
        grafico_dia = ctk.CTkFrame(frame_graficos, corner_radius=12, fg_color="#2B2B2B")
        grafico_dia.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        ctk.CTkLabel(grafico_dia, text="📅 Vendas do Dia", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        self.canvas_dia = self._criar_grafico_barra(grafico_dia)

        # --- GRÁFICO MENSAL ---
        grafico_mes = ctk.CTkFrame(frame_graficos, corner_radius=12, fg_color="#2B2B2B")
        grafico_mes.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        ctk.CTkLabel(grafico_mes, text="📈 Distribuição Mensal", font=("Segoe UI", 16, "bold")).pack(pady=(10, 5))
        self.canvas_mes = self._criar_grafico_pizza(grafico_mes)

        # === ATUALIZA DADOS AO ABRIR A TELA ===
        self.relatorio_controller.view = self
        self.relatorio_controller.atualizar_relatorio()

    # === FUNÇÕES AUXILIARES PARA GRÁFICOS ===
    def _criar_grafico_barra(self, parent):
        fig = Figure(figsize=(5, 3), dpi=100, facecolor="#2B2B2B")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2B2B2B")
        ax.tick_params(colors="white")
        ax.set_title("Totais por Pagamento", color="white", fontsize=12)
        bars = ax.bar(["Dinheiro", "PIX", "Crédito", "Débito"], [0, 0, 0, 0],
                      color=["#4CAF50", "#2196F3", "#FFC107", "#9C27B0"])
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return (fig, ax, bars, canvas)

    def _criar_grafico_pizza(self, parent):
        fig = Figure(figsize=(5, 3), dpi=100, facecolor="#2B2B2B")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2B2B2B")
        wedges, texts = ax.pie([1], labels=["Sem dados"], colors=["#555"], textprops={"color": "white"})
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return (fig, ax, wedges, canvas)

    # === ATUALIZAÇÃO DOS DADOS ===
    def atualizar_dados(self, totais_dia, totais_mes):
        total_geral_dia = sum(v or 0 for v in totais_dia.values())
        for k, v in self.cards.items():
            if k == "Total":
                v.configure(text=f"R${total_geral_dia:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            elif k in totais_dia:
                valor = totais_dia.get(k) or 0
                v.configure(text=f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Gráfico diário
        _, ax, bars, canvas = self.canvas_dia
        ax.clear()
        valores_dia = [v or 0 for v in totais_dia.values()]
        ax.bar(totais_dia.keys(), valores_dia,
               color=["#4CAF50", "#2196F3", "#FFC107", "#9C27B0"])
        ax.set_facecolor("#2B2B2B")
        ax.tick_params(colors="white")
        ax.set_title("Totais por Pagamento - Hoje", color="white", fontsize=12)
        canvas.draw()

        # Gráfico mensal
        _, ax, _, canvas = self.canvas_mes
        ax.clear()
        total_geral_mes = sum(v or 0 for v in totais_mes.values())
        if total_geral_mes > 0:
            ax.pie([v or 0 for v in totais_mes.values()],
                   labels=totais_mes.keys(),
                   autopct="%1.1f%%",
                   textprops={"color": "white"},
                   colors=["#4CAF50", "#2196F3", "#FFC107", "#9C27B0"])
        else:
            ax.pie([1], labels=["Sem dados"], colors=["#555"], textprops={"color": "white"})
        canvas.draw()

    def exibir_mensagem(self, texto):
        popup = ctk.CTkToplevel(self)
        popup.title("Aviso")
        popup.geometry("300x150")
        ctk.CTkLabel(popup, text=texto, font=("Segoe UI", 14, "bold")).pack(expand=True)
        ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=10)
