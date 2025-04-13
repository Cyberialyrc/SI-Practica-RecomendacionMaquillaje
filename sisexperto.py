import tkinter as tk
from tkinter import messagebox, PhotoImage
from pyswip import Prolog

# Datos temporales
respuestas = {}
prolog = Prolog()
prolog.consult("maquillaje.pl")

# Diccionario de imágenes y descripciones
imagenes = {
    "Fit Me Matte": "imagenes/fit_me_matte.png",
    "Double Wear": "imagenes/double_wear.png",
    "Studio Fix Powder": "imagenes/studio_fix.png",
}
descripciones = {
    "Fit Me Matte": "Base líquida de cobertura natural. Ideal para piel grasa.",
    "Double Wear": "Larga duración, alta cobertura, ideal para eventos largos.",
    "Studio Fix Powder": "Polvo compacto con buena fijación, perfecto para retoques.",
}

# Cuestionario paso a paso
class CuestionarioApp:
    def __init__(self, root):
        self.root = root
        self.preguntas = [
            ("¿Cuál es tu nombre?", "nombre", "entry"),
            ("Tipo de piel", "tipo_piel", ["grasa", "seca", "mixta", "normal"]),
            ("¿Tienes piel sensible?", "sensible", ["si", "no"]),
            ("¿Qué gama prefieres?", "gama", ["alta", "media", "baja"]),
            ("¿Qué tipo de base prefieres?", "tipo_base", ["liquida", "en_polvo", "crema", "barra", "polvo_compacto"]),
        ]
        self.indice = 0
        self.build_pantalla()

    def build_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        pregunta, clave, tipo = self.preguntas[self.indice]
        tk.Label(self.root, text=pregunta, font=('Arial', 14)).pack(pady=10)

        if tipo == "entry":
            self.respuesta = tk.Entry(self.root)
            self.respuesta.pack()
        else:
            self.respuesta = tk.StringVar()
            self.respuesta.set(tipo[0])
            for opcion in tipo:
                tk.Radiobutton(self.root, text=opcion, variable=self.respuesta, value=opcion).pack(anchor="w")

        tk.Button(self.root, text="Siguiente", command=self.siguiente).pack(pady=20)

    def siguiente(self):
        clave = self.preguntas[self.indice][1]
        valor = self.respuesta.get() if isinstance(self.respuesta, tk.StringVar) else self.respuesta.get()

        respuestas[clave] = valor
        self.indice += 1

        if self.indice < len(self.preguntas):
            self.build_pantalla()
        else:
            self.recomendar()

    def recomendar(self):
        nombre = respuestas["nombre"]
        tipo_piel = respuestas["tipo_piel"]
        sensible = respuestas["sensible"]
        gama = respuestas["gama"]
        tipo_base = respuestas["tipo_base"]

        # Registrar usuario en Prolog
        prolog.query(f"retractall(piel({nombre},_))")
        prolog.query(f"retractall(preferencia_marca({nombre},_))")
        prolog.query(f"retractall(preferencia_tipo_base({nombre},_))")
        prolog.query(f"retractall(piel_sensible({nombre}))")
        prolog.query(f"registrar_usuario({nombre}, {tipo_piel}, {sensible}, {gama}, {tipo_base})")

        resultados = list(prolog.query(f"recomendar_base({nombre}, Base)"))
        if not resultados:
            resultados = list(prolog.query(f"recomendar_base_cercana({nombre}, Base)"))

        self.mostrar_resultados(resultados)

    def mostrar_resultados(self, resultados):
        for widget in self.root.winfo_children():
            widget.destroy()

        if not resultados:
            tk.Label(self.root, text="No se encontraron productos recomendados.", font=('Arial', 14)).pack(pady=20)
            return

        tk.Label(self.root, text="Productos recomendados:", font=('Arial', 14, "bold")).pack(pady=10)

        for resultado in resultados:
            nombre_base = resultado["Base"]
            tk.Label(self.root, text=nombre_base, font=('Arial', 12, "bold")).pack()

            if nombre_base in imagenes:
                try:
                    img = PhotoImage(file=imagenes[nombre_base])
                    tk.Label(self.root, image=img).pack()
                    # Para que la imagen no se elimine al salir de scope
                    self.root.image = img
                except Exception as e:
                    tk.Label(self.root, text="[Imagen no disponible]").pack()

            if nombre_base in descripciones:
                tk.Label(self.root, text=descripciones[nombre_base], wraplength=300).pack(pady=5)

# Lanzar app
root = tk.Tk()
root.title("Sistema Experto de Maquillaje")
app = CuestionarioApp(root)
root.mainloop()
