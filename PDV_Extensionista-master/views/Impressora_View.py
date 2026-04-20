import customtkinter as ctk
from tkinter import messagebox
# Importa as funções do módulo que acabamos de criar
from Utils.Impressao import listar_impressoras, salvar_impressora_padrao, carregar_impressora_padrao


class ConfigImpressoraView(ctk.CTkToplevel):
    """Uma janela popup (Toplevel) para configurar a impressora."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Configurar Impressora")
        self.geometry("450x220")

        # Trava a janela principal enquanto esta estiver aberta
        self.grab_set()
        self.transient(master)  # Mantém esta janela à frente

        self.label = ctk.CTkLabel(self, text="Selecione a Impressora Térmica:", font=("Segoe UI", 16, "bold"))
        self.label.pack(pady=(20, 10))

        # Busca as impressoras instaladas no Windows
        self.lista_impressoras = listar_impressoras()
        if not self.lista_impressoras:
            self.lista_impressoras = ["Nenhuma impressora encontrada"]

        # Pega a impressora já salva ou a primeira da lista
        impressora_salva = carregar_impressora_padrao()
        if impressora_salva not in self.lista_impressoras:
            impressora_salva = self.lista_impressoras[0]

        self.impressora_var = ctk.StringVar(value=impressora_salva)

        self.option_menu = ctk.CTkOptionMenu(self,
                                             variable=self.impressora_var,
                                             values=self.lista_impressoras,
                                             width=300)
        self.option_menu.pack(pady=10, padx=20, fill="x")

        self.btn_salvar = ctk.CTkButton(self, text="Salvar Configuração", command=self.salvar_e_fechar)
        self.btn_salvar.pack(pady=20, ipady=5)

    def salvar_e_fechar(self):
        nome = self.impressora_var.get()
        if nome == "Nenhuma impressora encontrada":
            messagebox.showerror("Erro", "Nenhuma impressora válida selecionada.", parent=self)
            return

        if salvar_impressora_padrao(nome):
            messagebox.showinfo("Sucesso", f"Impressora '{nome}' salva como padrão.", parent=self)
            self.destroy()  # Fecha o popup
        else:
            messagebox.showerror("Erro", "Falha ao salvar a configuração.", parent=self)