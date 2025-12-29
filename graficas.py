import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd


class Graficador:
    def __init__(self):
        try:
            plt.style.use("dark_background")
        except:
            pass

    def obtener_grafica_dona(self, datos_sql, frame_padre):
        if not datos_sql:
            df = pd.DataFrame({"categoria": ["Sin Datos"], "total": [1]})
        else:
            df = pd.DataFrame(datos_sql, columns=["categoria", "total"])

        fig = Figure(figsize=(3, 3), dpi=80)
        ax = fig.add_subplot(111)

        colores = ["#1f6aa5", "#2c3e50", "#17a2b8", "#007bff", "#6610f2"]

        wedges, texts, autotexts = ax.pie(
            df["total"],
            labels=df["categoria"],
            autopct="%1.1f%%",
            startangle=90,
            colors=colores,
            textprops={"color": "white", "fontsize": 8},
        )

        circulo_centro = plt.Circle((0, 0), 0.70, fc="#242424")
        ax.add_artist(circulo_centro)
        ax.axis("equal")
        canvas = FigureCanvasTkAgg(fig, master=frame_padre)
        canvas.draw()
        return canvas.get_tk_widget()

    def obtener_grafica_barras(self, datos, frame_padre):
        # 1. Convertir datos a DataFrame
        if not datos:
            df = pd.DataFrame({"fecha": ["Sin Deudas"], "monto": [0]})
        else:
            df = pd.DataFrame(datos, columns=["fecha", "monto"])
            df = df.sort_values("fecha")

        # 2. Crear Figura
        fig = Figure(figsize=(4, 3), dpi=80)
        ax = fig.add_subplot(111)

        # 3. Estilo Oscuro
        fig.patch.set_facecolor("#242424")
        ax.set_facecolor("#242424")

        # 4. Dibujar Barras
        ax.bar(df["fecha"], df["monto"], color="#1f6aa5")

        # 5. Etiquetas
        ax.set_title("Proyección de Pagos (Tarjetas)", color="white", fontsize=10)
        ax.tick_params(axis="x", colors="white", rotation=45)
        ax.tick_params(axis="y", colors="white")

        # Bordes
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color("white")
        ax.spines["left"].set_color("white")

        # 6. Empaquetar para Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_padre)
        canvas.draw()
        return canvas.get_tk_widget()
