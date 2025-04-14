import tkinter as tk
from tkinter import messagebox, PhotoImage
from pyswip import Prolog

prolog = Prolog()
prolog.consult("maquillaje.pl")

# Limpiar y registrar las bases disponibles
prolog.query("retractall(disponible(_)).")

# Agregar las bases disponibles desde el inicio
bases_disponibles = [
    "Fit Me Matte",
    "SuperStay Full Coverage",
    "True Match",
    "Double Wear",
    "Studio Fix Powder",
    "Nude Illusion",
    "Fresh & Fit",
    "Dream Matte Mousse",
    "Skin Long-Wear Weightless",
    "Forever Skin Glow",
    "Synchro Skin Radiant Lifting",
    "Healthy Mix",
    "Photofocus Foundation",
    "Stay All Day",
    "HD Liquid Coverage",
    "Soft Touch Mousse",
    "Even Skin Tone",
    "Mineralize Loose",
    "Blur Stick"
]


for base in bases_disponibles:
    prolog.query(f"agregar_disponibilidad('{base}').")

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

respuestas = {}

class CuestionarioApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x500")
        self.root.configure(bg="#f5f5f5")
        self.root.resizable(False, False)

        self.frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=500, height=400)

        self.preguntas = [
            ("¿Cuál es tu nombre?", "nombre", "entry"),
            ("Tipo de piel", "tipo_piel", ["grasa", "seca", "mixta", "normal"]),
            ("¿Tienes piel sensible?", "sensible", ["si", "no"]),
            ("¿Qué gama prefieres?", "gama", ["alta", "media", "baja"]),
            ("¿Qué tipo de base prefieres?", "tipo_base", ["liquida", "en_polvo", "crema", "barra", "polvo_compacto"]),
            ("¿Eres alérgico a algún ingrediente?", "alergico", ["si", "no"]),
            ("¿A qué ingrediente eres alérgico?", "ingrediente_alergia", "entry")
        ]
        self.indice = 0
        self.build_pantalla()

    def build_pantalla(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

        pregunta, clave, tipo = self.preguntas[self.indice]
        tk.Label(self.frame, text=pregunta, font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=15)

        if tipo == "entry":
            self.respuesta = tk.Entry(self.frame, font=("Arial", 12))
            self.respuesta.pack()
        else:
            self.respuesta = tk.StringVar()
            self.respuesta.set(tipo[0])
            for opcion in tipo:
                tk.Radiobutton(self.frame, text=opcion.capitalize(), variable=self.respuesta, value=opcion,
                font=("Arial", 12), bg="#ffffff").pack(anchor="w", padx=20)

        tk.Button(self.frame, text="Siguiente", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
        command=self.siguiente).pack(pady=25)

    def siguiente(self):
        clave = self.preguntas[self.indice][1]
        valor = self.respuesta.get() if isinstance(self.respuesta, tk.StringVar) else self.respuesta.get().strip()
        respuestas[clave] = valor

        if clave == "alergico" and valor == "no":
            self.preguntas = [p for p in self.preguntas if p[1] != "ingrediente_alergia"]

        self.indice += 1

        if self.indice < len(self.preguntas):
            self.build_pantalla()
        else:
            self.recomendar()

    def recomendar(self):
        nombre = respuestas['nombre'].strip().lower()
        tipo_piel = respuestas["tipo_piel"]
        sensible = respuestas["sensible"]
        gama = respuestas["gama"]
        tipo_base = respuestas["tipo_base"]

        print(f"[DEBUG] Registrando usuario: {nombre}")
        print(f"[DEBUG] Características: piel={tipo_piel}, sensible={sensible}, gama={gama}, tipo_base={tipo_base}")

        list(prolog.query(f"registrar_usuario({nombre}, '{tipo_piel}', '{sensible}', '{gama}', '{tipo_base}')."))

        if respuestas.get("alergico") == "si" and respuestas.get("ingrediente_alergia"):
            print(f"[DEBUG] Registrando alergia: {respuestas['ingrediente_alergia']}")
            prolog.query(f"agregar_alergia({nombre}, '{respuestas['ingrediente_alergia']}').")

        resultados = list(prolog.query(f"recomendar_base({nombre}, B)."))
        print(f"[DEBUG] Resultados exactos: {resultados}")
        if not resultados:
            resultados = list(prolog.query(f"recomendar_base_cercana({nombre}, B)."))
            print(f"[DEBUG] Resultados cercanos: {resultados}")

        self.mostrar_resultados(resultados)

    def mostrar_resultados(self, resultados):
        for widget in self.frame.winfo_children():
            widget.destroy()

        if not resultados:
            tk.Label(self.frame, text="No se encontraron productos recomendados.", font=("Arial", 14), bg="#ffffff").pack(pady=20)
            return

        tk.Label(self.frame, text="Productos recomendados:", font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=10)

        for resultado in resultados:
            print(resultado)
            nombre_base = resultado["X"]
            tk.Label(self.frame, text=nombre_base, font=("Arial", 12, "bold"), bg="#ffffff").pack()

            if nombre_base in imagenes:
                try:
                    img = PhotoImage(file=imagenes[nombre_base])
                    img_label = tk.Label(self.frame, image=img, bg="#ffffff")
                    img_label.image = img
                    img_label.pack()
                except:
                    tk.Label(self.frame, text="[Imagen no disponible]", bg="#ffffff").pack()

            if nombre_base in descripciones:
                tk.Label(self.frame, text=descripciones[nombre_base], wraplength=400, font=("Arial", 11), bg="#ffffff").pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sistema Experto de Maquillaje")
    app = CuestionarioApp(root)
    root.mainloop()
