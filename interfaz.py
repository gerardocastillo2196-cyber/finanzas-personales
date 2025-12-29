import customtkinter as ctk
from modelo import GestorGastos
from graficas import Graficador
from tkinter import messagebox
from tkinter import filedialog

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("dark-blue")


class AppGastos(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. CONFIGURACIÓN BÁSICA
        self.title("Sistema de Finanzas Personales")
        self.geometry("900x750")

        # 2. INSTANCIAS DE LÓGICA
        self.gestor = GestorGastos()
        self.graficador = Graficador()

        # 3. CREACIÓN DE LOS CONTENEDORES (FRAMES)
        self.frame_izq = ctk.CTkFrame(self)
        self.frame_izq.pack(side="left", fill="both", expand=True, padx=10, pady=50)

        self.frame_der = ctk.CTkFrame(self, width=350)
        self.frame_der.pack(side="right", fill="y", padx=10, pady=10)

        # 4. CREACIÓN DEL MENÚ DE OPCIONES
        # (IMPORTANTE: Crear esto ANTES de llamar a crear_formulario)
        self.menu_opciones = ctk.CTkOptionMenu(
            self,
            values=["Gestionar Tarjetas", "Exportar a Excel", "Reset", "Salir"],
            command=self.evento_menu,
            width=110,
            height=30,
            corner_radius=8,
            fg_color="#2b2b2b",
            button_color="#333333",
            button_hover_color="#444444",
            text_color="white",
        )
        self.menu_opciones.set(" Menú")
        self.menu_opciones.place(relx=0.58, y=10, anchor="n")

        # 5. NUEVO BOTÓN: PROYECCIÓN DE PAGOS
        # Este botón cambia la gráfica para ver las fechas de pago
        self.btn_proyeccion = ctk.CTkButton(
            self,
            text="📅 Ver Pagos Tarjetas",
            width=120,
            height=30,
            fg_color="#3a7ebf",
            command=self.mostrar_grafica_proyeccion,
        )
        self.btn_proyeccion.place(relx=0.40, y=10, anchor="n")

        # 6. LLAMAR A LAS FUNCIONES DE DIBUJO
        # Ahora sí podemos crear el formulario porque el menú ya existe
        self.crear_formulario()
        self.actualizar_grafica()

    def evento_menu(self, opcion_seleccionada):
        if opcion_seleccionada == "Gestionar Tarjetas":
            self.abrir_ventana_tarjetas()
            self.menu_opciones.set(" Menú")

        elif opcion_seleccionada == "Salir":
            self.destroy()
            # ¡OJO! No hacemos .set() aquí porque la ventana ya se cerró

        elif opcion_seleccionada == "Reset":
            respuesta = messagebox.askyesno(
                "PRECAUCION",
                "Estás a punto de borrar toda tu base de datos.\nEsta acción no se puede deshacer.",
            )
            if respuesta:
                self.gestor.resetear_base_datos()
                self.actualizar_grafica()
                messagebox.showinfo("Listo", "Su sistema ha sido formateado")
            self.menu_opciones.set(" Menú")

        elif opcion_seleccionada == "Exportar a Excel":
            # CORRECCIÓN: Usamos asksaveasfilename para obtener solo la ruta texto
            ruta = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos de Excel", "*.xlsx")],
                title="Guardar reporte",
                initialfile="Mi_reporte.xlsx",
            )
            if ruta:
                exito = self.gestor.exportar_excel(ruta)
                if exito:
                    messagebox.showinfo("Éxito", "Reporte guardado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo guardar el reporte")
            self.menu_opciones.set(" Menú")

    def crear_formulario(self):
        self.titulo = ctk.CTkLabel(
            self.frame_der, text="Nuevo Movimiento", font=("Arial", 20, "bold")
        )
        self.titulo.pack(pady=20)

        # TIPO
        self.lbl_tipo = ctk.CTkLabel(self.frame_der, text="Tipo de Movimiento:")
        self.lbl_tipo.pack(pady=(10, 0), anchor="w", padx=20)

        self.combo_tipo = ctk.CTkComboBox(
            self.frame_der, values=["GASTO", "INGRESO", "AHORROS"], width=250
        )
        self.combo_tipo.pack(pady=5, padx=20, anchor="w")
        self.combo_tipo.set("GASTO")

        # CATEGORÍA
        lista_categorias = [
            "Comida",
            "Transporte",
            "Servicios",
            "Entretenimiento",
            "Salud",
            "Educación",
            "Ropa",
            "Ahorro",
            "Sueldo",
            "Otros",
        ]

        self.combo_categoria = ctk.CTkComboBox(
            self.frame_der, values=lista_categorias, width=250
        )
        self.combo_categoria.pack(pady=10, padx=20, anchor="w")
        self.combo_categoria.set("Comida")

        # CONCEPTO
        self.entry_concepto = ctk.CTkEntry(
            self.frame_der, placeholder_text="Concepto (Ej: Pizza)", width=250
        )
        self.entry_concepto.pack(pady=10, padx=20, anchor="w")

        # MÉTODO
        self.lbl_metodo = ctk.CTkLabel(self.frame_der, text="Método de Pago:")
        self.lbl_metodo.pack(pady=(10, 0), anchor="w", padx=20)

        self.combo_metodo = ctk.CTkComboBox(
            self.frame_der,
            values=["EFECTIVO", "TARJETA DE CREDITO", "DEBITO"],
            width=250,
        )
        self.combo_metodo.pack(pady=5, padx=20, anchor="w")

        # COMBO OCULTO PARA TARJETAS ESPECÍFICAS
        self.combo_tarjetas_especificas = ctk.CTkOptionMenu(
            self.frame_der, width=250, values=["Sin tarjetas"]
        )
        # Activamos el "sensor" para mostrar/ocultar este menú
        self.combo_metodo.configure(command=self.verificar_si_es_tarjeta)

        # MONTO
        self.entry_monto = ctk.CTkEntry(
            self.frame_der, placeholder_text="Monto (Ej: 50.00)", width=250
        )
        self.entry_monto.pack(pady=10, padx=20, anchor="w")

        # BOTÓN GUARDAR
        self.btn_guardar = ctk.CTkButton(
            self.frame_der, text="Guardar Operación", command=self.accion_guardar
        )
        self.btn_guardar.pack(pady=(30, 0))

        self.lbl_mensaje = ctk.CTkLabel(self.frame_der, text="", text_color="green")
        self.lbl_mensaje.pack(pady=5)

        self.separador = ctk.CTkLabel(
            self.frame_der, text="Desglose de categorias", text_color="white"
        )
        self.separador.pack(pady=(0, 5))

        self.frame_lista = ctk.CTkScrollableFrame(
            self.frame_der, height=200, label_text="Totales"
        )
        self.frame_lista.pack(fill="x", padx=10, pady=(5, 10), expand=True)

    def abrir_ventana_tarjetas(self):
        ventana_t = ctk.CTkToplevel(self)
        ventana_t.title("Gestionar Tarjetas")
        ventana_t.geometry("300x350")
        ventana_t.transient(self)

        ctk.CTkLabel(
            ventana_t, text="Gestionar tarjetas", font=("arial", 16, "bold")
        ).pack(pady=15)

        entry_nombre = ctk.CTkEntry(ventana_t, placeholder_text="Alias (Ej: Visa Oro)")
        entry_nombre.pack(pady=10, padx=20)

        entry_corte = ctk.CTkEntry(ventana_t, placeholder_text="Día de Corte (Ej: 5)")
        entry_corte.pack(pady=10, padx=20)

        entry_pago = ctk.CTkEntry(ventana_t, placeholder_text="Día de Pago (Ej: 25)")
        entry_pago.pack(pady=10, padx=20)

        lbl_status = ctk.CTkLabel(ventana_t, text="")
        lbl_status.pack(pady=5)

        def guardar_tarjeta():
            nom = entry_nombre.get()
            corte = entry_corte.get()
            pago = entry_pago.get()

            if nom and corte.isdigit() and pago.isdigit():
                exito = self.gestor.guardar_movimientos_tarjeta(
                    nom, int(corte), int(pago)
                )

                if exito:
                    lbl_status.configure(text="Tarjeta Guardada", text_color="green")
                    entry_nombre.delete(0, "end")
                    entry_corte.delete(0, "end")
                    entry_pago.delete(0, "end")
                else:
                    lbl_status.configure(
                        text="Error al Guardar Tarjeta", text_color="red"
                    )
            else:
                lbl_status.configure(
                    text="Revisa que los días sean números", text_color="red"
                )

        ctk.CTkButton(
            ventana_t, text="Guardar Configuración", command=guardar_tarjeta
        ).pack(pady=20)

    def actualizar_grafica(self):
        """Muestra la Gráfica de Dona (Balance General)"""
        for widget in self.frame_izq.winfo_children():
            widget.destroy()

        balance = self.gestor.calcular_balance()
        color_texto = "#2cc985" if balance >= 0 else "#ff5555"

        ctk.CTkLabel(
            self.frame_izq,
            text=f"Balance: Q{balance:,.2f}",
            font=("Arial", 30, "bold"),
            text_color=color_texto,
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            self.frame_izq, text="Distribución de Gastos", font=("Arial", 18, "bold")
        ).pack(pady=10)

        datos = self.gestor.obtener_gastos_por_categoria()
        self.actualizar_lista_textual(datos)

        canvas_widget = self.graficador.obtener_grafica_dona(datos, self.frame_izq)
        canvas_widget.pack(expand=True, fill="both", padx=20, pady=20)

    def mostrar_grafica_proyeccion(self):
        """Muestra la Gráfica de Barras (Pagos de Tarjetas)"""
        # 1. Limpiamos el frame izquierdo
        for widget in self.frame_izq.winfo_children():
            widget.destroy()

        # 2. Pedimos los datos calculados al modelo
        # (Asegúrate de haber agregado 'obtener_proyeccion_pagos' en modelo.py)
        datos_proyeccion = self.gestor.obtener_proyeccion_pagos()

        # 3. Título nuevo
        ctk.CTkLabel(
            self.frame_izq, text="Calendario de Pagos", font=("Arial", 25, "bold")
        ).pack(pady=10)

        # 4. Llamamos al graficador de BARRAS (asegúrate de tenerlo en graficas.py)
        canvas = self.graficador.obtener_grafica_barras(
            datos_proyeccion, self.frame_izq
        )
        canvas.pack(expand=True, fill="both", padx=20, pady=20)

        # 5. Botón para volver al inicio
        ctk.CTkButton(
            self.frame_izq,
            text="Volver al Balance",
            command=self.actualizar_grafica,
            fg_color="transparent",
            border_width=1,
        ).pack(pady=10)

    def actualizar_lista_textual(self, datos_sql):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        for fila in datos_sql:
            categoria = fila[0]
            monto = fila[1]
            texto_linea = f"{categoria}: Q{monto:,.2f}"
            lbl_item = ctk.CTkLabel(self.frame_lista, text=texto_linea, anchor="w")
            lbl_item.pack(fill="x", padx=5, pady=2)

    def accion_guardar(self):
        # 1. Obtenemos datos del formulario
        tipo = self.combo_tipo.get()
        cat = self.combo_categoria.get()
        con = self.entry_concepto.get()
        metodo_bruto = self.combo_metodo.get()
        mon = self.entry_monto.get()

        # 2. LÓGICA DE TARJETA:
        # Si eligió tarjeta, queremos guardar el NOMBRE ESPECÍFICO (ej: Visa), no el genérico.
        metodo_final = metodo_bruto

        if metodo_bruto == "TARJETA DE CREDITO":
            nombre_tarjeta = self.combo_tarjetas_especificas.get()
            if nombre_tarjeta and nombre_tarjeta != "Sin tarjetas":
                metodo_final = nombre_tarjeta

        # 3. Validaciones
        if not cat or not con or not mon:
            self.lbl_mensaje.configure(text="Faltan datos", text_color="red")
            return

        try:
            # 4. Guardamos usando metodo_final
            self.gestor.guardar_gastos(cat, con, float(mon), tipo, metodo_final)
            self.lbl_mensaje.configure(text="Guardado", text_color="green")

            # 5. Limpiar y Actualizar
            self.combo_categoria.set("comida")
            self.entry_concepto.delete(0, "end")
            self.entry_monto.delete(0, "end")
            self.actualizar_grafica()

        except ValueError:
            self.lbl_mensaje.configure(
                text="El monto debe ser numérico", text_color="red"
            )
        except Exception as e:
            self.lbl_mensaje.configure(text=f"Error: {e}", text_color="red")

    def verificar_si_es_tarjeta(self, metodo_selecionado):
        if metodo_selecionado == "TARJETA DE CREDITO":
            # Usamos obtener_nombre_tarjetas (singular) tal como lo tienes en tu modelo.py
            nombres = self.gestor.obtener_nombre_tarjetas()

            if nombres:
                self.combo_tarjetas_especificas.configure(values=nombres)
                self.combo_tarjetas_especificas.set(nombres[0])
                self.combo_tarjetas_especificas.pack(
                    pady=(5, 10), padx=10, anchor="w", after=self.combo_metodo
                )
            else:
                self.lbl_mensaje.configure(
                    text="⚠ Registra una tarjeta primero",
                    text_color="orange",
                )
        else:
            self.combo_tarjetas_especificas.pack_forget()


if __name__ == "__main__":
    app = AppGastos()
    app.mainloop()
