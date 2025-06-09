import os
import threading
import time
import tkinter as tk
from datetime import datetime

import bot_telegram
import config
import jr_utils.jr_utils_box

from jr_utils import jrlogging

from tkinter import messagebox, ttk
from PIL import Image, ImageTk

VERSION = "2306.20_bot"
TEXT_ACTIVADO_BOT = ("Bot de Telegram DESACTIVADO", "Bot de Telegram ACTIVADO",
                     "... Desactivando...")

logger = jrlogging.configurar_logger(
    log_nombre="otsaila_bot",
    log_fichero="__Otsaila_bot__.log",
    log_nivel=config.ini.get("General", "nivel_log")
)


class App(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._hilo_bot = None

        self.master = master
        self._ancho = 500
        self._alto = 300
        # Evita el botón x cerrar de Windows
        self.master.protocol("WM_DELETE_WINDOW", self._btncerrar_ventana)

        x_ventana = self.master.winfo_screenwidth() // 2 - self._ancho // 2
        y_ventana = self.master.winfo_screenheight() // 2 - self._alto // 2
        posicion = f"{self._ancho}x{self._alto}+{x_ventana}+{y_ventana}"
        self.master.geometry(posicion)
        self.master.title(
            f"Otsaila Lanzador del BOT -- [Vers.{VERSION}], (c) JrSoft 2023")
        self.master.resizable(width=False, height=False)
        self._crear_widgets()
        self._iniciar_menu_principal()

    def _btncerrar_ventana(self):
        self._menu_principal.exit()

    def _crear_widgets(self):
        # icono de la ventana
        self.master.iconbitmap(r"images\otsaila_logo_color.ico")

        # Panel superior
        # self._pan_izq = tk.PanedWindow(master=self.master,
        # height=800, bg="#62b526", relief="sunken", borderwidth=1)
        self._pan_sup = ttk.Frame(master=self.master)
        # self._pan_izq.configure(bg="red", relief="groove")
        self._pan_sup.pack(side="top", anchor="n", expand=True, fill="both",
                           padx=3, pady=1)

        # Logo central
        fich_imagen = os.path.join(os.getcwd(),
                                   r"images\Otsaila_logo_color.png")
        self._img_logo = ImageTk.PhotoImage(
            Image.open(fich_imagen).resize((200, 200)))
        self._lbl_logo = tk.Label(master=self._pan_sup, image=self._img_logo)
        self._lbl_logo.pack(side="top", anchor="n", expand=False, fill="none",
                            padx=4, pady=10)

        # Panel inferior
        self._pan_inf = ttk.Frame(master=self.master, height=40)
        # self._pan_inf.configure(bg="red", relief="groove")
        self._pan_inf.pack(fill="both", anchor="n", padx=1, pady=1)

        # Luz roja de activación del bot de Telegram
        fich_imagen = os.path.join(config.PATH_RAIZ_APP, r"images\Red_on.png")
        self._img_luz_on = ImageTk.PhotoImage(
            Image.open(fich_imagen).resize((30, 30)))
        self._lbl_luz_on = ttk.Label(master=self._pan_inf,
                                     image=self._img_luz_on)
        self._lbl_luz_on.place(x=3, y=2)
        fich_imagen = os.path.join(config.PATH_RAIZ_APP, r"images\Red_off.png")
        self._img_luz_off = ImageTk.PhotoImage(
            Image.open(fich_imagen).resize((30, 30)))
        self._lbl_luz_off = tk.Label(master=self._pan_inf,
                                     image=self._img_luz_off)
        self._lbl_luz_off.place(x=3, y=2)

        # Etiqueta con el texto del estado del bot
        self._lbl_estado_bot = ttk.Label(master=self._pan_inf,
                                         text=TEXT_ACTIVADO_BOT[0])
        self._lbl_estado_bot.place(x=42, y=9)
        self.pack()

    def _iniciar_menu_principal(self):
        self._menu_principal = Menu(self.master,
                                    callback=self._on_seleccion_menu)
        self.master.configure(menu=self._menu_principal)

        # Captura la pulsación del botón CERRAR ventana Windows (2 versiones)
        # self.master.protocol('WM_DELETE_WINDOW', lambda: 0)      # versión 1
        self.master.protocol("WM_DELETE_WINDOW",
                             self._menu_principal.exit)  # version 2

    def _on_seleccion_menu(self, opcion_menu: str):
        """Callback invocada por las opciones del menú principal"""
        if opcion_menu in ("activar", "desactivar"):
            self.cmd_activar_bot(accion=opcion_menu)

    def cmd_activar_bot(self, accion: str):
        if accion == "activar":
            if self._hilo_bot:
                # Si ya existía el hilo es que ya se ha ejecutado
                msg = "No se puede volver a activar el BOT...\n" \
                      "Si necesita volver a usarlo, " \
                      "debe cerrar y reiniciar Otsaila."
                logger.debug(msg)
                messagebox.showinfo(config.NOMBRE_APP, msg)
                return
            else:
                bot_telegram.definir_comandos_bot()
                logger.debug("¡¡Iniciando el bot!!")
                self._hilo_bot = threading.Thread(
                    name=config.ini.get("General", "hilo_bot_telegram"),
                    target=bot_telegram.bucle_principal_bot)
                self._hilo_bot.start()

            msg = "El bot ha sido INICIADO...\n" + \
                datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S")
            logger.debug(msg)
            bot_telegram.bot.send_message(
                config.ini.get("General", "user_joki"), msg
            )
            jr_utils.jr_utils_box.notificacion(
                titulo="INICIALIZACIÓN DEL BOT DE OTSAILA", mensaje=msg
            )
            self._menu_principal.menu_bot.entryconfig(0, state=tk.DISABLED)
            self._menu_principal.menu_bot.entryconfig(1, state=tk.NORMAL)
            self._lbl_luz_on.lift()
            self._lbl_estado_bot.configure(text=TEXT_ACTIVADO_BOT[1])
            # bot_telegram.definir_comandos_bot(activar=True)

        elif accion == "desactivar":
            self._lbl_estado_bot.configure(text=TEXT_ACTIVADO_BOT[2])
            self.update()
            bot_telegram.parar_bot()
            msg = "El bot ha sido PARADO...\n" + \
                datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S")
            logger.debug(msg)
            bot_telegram.bot.send_message(
                config.ini.get("General", "user_joki"), msg
            )
            jr_utils.jr_utils_box.notificacion(
                titulo="SE HA PARADO EL BOT DE OTSAILA", mensaje=msg
            )

            self._menu_principal.menu_bot.entryconfig(0, state=tk.NORMAL)
            self._menu_principal.menu_bot.entryconfig(1, state=tk.DISABLED)
            self._lbl_luz_off.lift()
            self._lbl_estado_bot.configure(text=TEXT_ACTIVADO_BOT[0])
            bot_telegram.definir_comandos_bot(activar=False)

        else:
            raise ValueError(
                f"Se esperaba 'activar' o 'desactivar, pero se "
                f"recibió '{accion}'...")
        return


class Menu(tk.Menu):
    """
    Clase MenuPrin que contiene el menú principal de la aplicación
    El atributo 'callback' sirve que la clase llamante pueda recibir los
    eventos de opciones pulsadas medienta 'callback'
    """

    def __init__(self, parent, callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self._funcion_callback = callback
        self.menu_bot = tk.Menu(self.parent, tearoff=0)
        self.menu_bot.add_command(
            label="Activar BOT de Telegram",
            command=lambda: self._on_seleccion_menu(opcion_menu="activar")
        )
        self.menu_bot.add_command(
            label="Desactviar BOT de Teleram",
            command=lambda: self._on_seleccion_menu(opcion_menu="desactivar")
        )
        self.menu_bot.add_separator()
        self.menu_bot.add_command(
            label="Salir del lanzador", command=self.exit
        )

        self.menu_bot.entryconfigure(0, state=tk.NORMAL)
        self.menu_bot.entryconfigure(1, state=tk.DISABLED)

        self.add_cascade(label="Bot de Telegram", menu=self.menu_bot)

    def _on_seleccion_menu(self, opcion_menu: str):
        if self._funcion_callback:
            self._funcion_callback(opcion_menu=opcion_menu)

    def exit(self):
        valor = messagebox \
            .askquestion('Salir', '¿Estás seguro de querer salir?')
        if valor == 'yes':
            if self.menu_bot.entrycget(1, "state") == tk.NORMAL:
                self._on_seleccion_menu("desactivar")
            self.parent.destroy()


if __name__ == "__main__":
    logger.critical(f"··· Inicio {__file__} ".ljust(110, "·"))
    logger.debug(f"Otsaila_bot - Versión: {VERSION}")

    root = tk.Tk()
    app = App(master=root)
    root.mainloop()

    logger.critical("··· Fin otsaila.py ".ljust(110, "·") + "\n·" * 3)
