import tkinter as tk
from tkinter import messagebox, PhotoImage
from pyswip import Prolog

prolog = Prolog()
prolog.consult("maquillaje.pl")

prolog.query("retractall(disponible(_)).")

bases_disponibles = [
    "Fit Me Matte", "SuperStay Full Coverage", "True Match", "Double Wear",
    "Studio Fix Powder", "Nude Illusion", "Fresh & Fit", "Dream Matte Mousse",
    "Skin Long-Wear Weightless", "Forever Skin Glow", "Synchro Skin Radiant Lifting",
    "Healthy Mix", "Photofocus Foundation", "Stay All Day", "HD Liquid Coverage",
    "Soft Touch Mousse", "Even Skin Tone", "Mineralize Loose", "Blur Stick"
]

for base in bases_disponibles:
    prolog.query(f"agregar_disponibilidad('{base}').")

imagenes = {
    "Fit Me Matte": "imagenes/fit_me_matte.png",
    "Double Wear": "imagenes/double_wear.png",
    "Studio Fix Powder": "imagenes/studio_fix.png",
    "portada": "imagenes/chihuahua_portada.png"
}

descripciones = {
    "Fit Me Matte": "Base líquida de cobertura natural. Ideal para piel grasa.",
    "Double Wear": "Larga duración, alta cobertura, ideal para eventos largos.",
    "Studio Fix Powder": "Polvo compacto con buena fijación, perfecto para retoques."
}

respuestas = {}

class CuestionarioApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x700")
        self.root.configure(bg="#EBE8DB")
        self.root.resizable(False, False)

        # Imagen como botón de inicio (sin cuadro blanco)
        try:
            portada_img = PhotoImage(file=imagenes["portada"])
            self.portada_btn = tk.Button(self.root, image=portada_img, bd=0, highlightthickness=0, relief="flat", command=self.build_pantalla)
            self.portada_btn.image = portada_img
            self.portada_btn.pack(pady=30)
        except Exception as e:
            print(f"Error al cargar imagen de portada: {e}")
            self.build_pantalla()

        self.frame = tk.Frame(root, bg="#ffffff", bd=2, relief=tk.GROOVE)

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

    def build_pantalla(self):
        if hasattr(self, 'portada_btn'):
            self.portada_btn.destroy()

        self.frame.place(relx=0.5, rely=0.55, anchor=tk.CENTER, width=500, height=400)

        for widget in self.frame.winfo_children():
            widget.destroy()

        pregunta, clave, tipo = self.preguntas[self.indice]
        tk.Label(self.frame, text=pregunta, font=("Helvetica", 14, "bold"), fg="#B03052", bg="#ffffff").pack(pady=15)

        if tipo == "entry":
            self.respuesta = tk.Entry(self.frame, font=("Helvetica", 12), bg="#f9f4f2")
            self.respuesta.pack()
        else:
            self.respuesta = tk.StringVar()
            self.respuesta.set(tipo[0])
            for opcion in tipo:
                tk.Radiobutton(self.frame, text=opcion.capitalize(), variable=self.respuesta, value=opcion,
                               font=("Helvetica", 12), fg="#3D0301", bg="#ffffff", activebackground="#EBE8DB").pack(anchor="w", padx=20)

        tk.Button(self.frame, text="Siguiente", font=("Helvetica", 12, "bold"),
                  bg="#D76C82", fg="white", activebackground="#B03052",
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

        list(prolog.query(f"registrar_usuario({nombre}, '{tipo_piel}', '{sensible}', '{gama}', '{tipo_base}')."))

        if respuestas.get("alergico") == "si" and respuestas.get("ingrediente_alergia"):
            prolog.query(f"agregar_alergia({nombre}, '{respuestas['ingrediente_alergia']}').")

        resultados = list(prolog.query(f"recomendar_base({nombre}, B)."))
        if not resultados:
            resultados = list(prolog.query(f"recomendar_base_cercana({nombre}, B)."))

        self.mostrar_resultados(resultados)

    def mostrar_resultados(self, resultados):
        for widget in self.frame.winfo_children():
            widget.destroy()

        if not resultados:
            tk.Label(self.frame, text="No se encontraron productos recomendados.", font=("Helvetica", 14), fg="#3D0301", bg="#ffffff").pack(pady=20)
            return

        tk.Label(self.frame, text="Productos recomendados:", font=("Helvetica", 14, "bold"), fg="#B03052", bg="#ffffff").pack(pady=10)

        for resultado in resultados:
            nombre_base = resultado["B"]
            tk.Label(self.frame, text=nombre_base, font=("Helvetica", 12, "bold"), fg="#3D0301", bg="#ffffff").pack()

            if nombre_base in imagenes:
                try:
                    img = PhotoImage(file=imagenes[nombre_base])
                    img_label = tk.Label(self.frame, image=img, bg="#ffffff")
                    img_label.image = img
                    img_label.pack()
                except Exception as e:
                    print(f"Error al cargar imagen de producto {nombre_base}: {e}")
                    tk.Label(self.frame, text="[Imagen no disponible]", bg="#ffffff").pack()

            if nombre_base in descripciones:
                tk.Label(self.frame, text=descripciones[nombre_base], wraplength=400,
                         font=("Helvetica", 11), fg="#3D0301", bg="#ffffff").pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sistema Experto de Maquillaje")
    app = CuestionarioApp(root)
    root.mainloop()

