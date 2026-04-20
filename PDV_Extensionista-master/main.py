import customtkinter as ctk #importação do módulo ctk
from controllers.AppController import AppController

if __name__ == '__main__':
    #configura para o modo dark com tema verde da tela principal que é a d de login
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('green')

    root = ctk.CTk() #cria a janela
    root.geometry('800x500')
    root.title('Sistema PDV')

    AppController(root)
    root.mainloop()





