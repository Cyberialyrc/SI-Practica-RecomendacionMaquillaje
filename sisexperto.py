import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
from pyswip import Prolog

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

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

        try:
            portada_img = CTkImage(Image.open(imagenes["portada"]), size=(300, 300))
            self.portada_btn = ctk.CTkButton(self.root, image=portada_img, text="", fg_color="transparent", hover_color="#f8e1e7", command=self.build_pantalla)
            self.portada_btn.image = portada_img
            self.portada_btn.pack(pady=30)
        except Exception as e:
            print(f"Error al cargar imagen de portada: {e}")
            self.build_pantalla()

        self.frame = ctk.CTkFrame(self.root, fg_color="#ffffff", corner_radius=40, width=420, height=340, border_width=0)

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

        self.frame.place(relx=0.5, rely=0.55, anchor="center")
        self.frame.configure(bg_color="#EBE8DB")
        self.frame.pack_propagate(False)

        for widget in self.frame.winfo_children():
            widget.destroy()

        pregunta, clave, tipo = self.preguntas[self.indice]
        ctk.CTkLabel(self.frame, text=pregunta, text_color="#B03052", font=("Century Gothic", 16, "bold")).pack(pady=15)

        if tipo == "entry":
            self.respuesta = ctk.CTkEntry(self.frame, width=160, corner_radius=10, fg_color="#fdf7f7", justify="center", placeholder_text="Escribe tu nombre")
            self.respuesta.pack(pady=10)
        else:
            self.respuesta = ctk.StringVar()
            self.respuesta.set(tipo[0])
            for opcion in tipo:
                ctk.CTkRadioButton(self.frame, text=opcion.capitalize(), variable=self.respuesta, value=opcion,
                                   text_color="#3D0301", fg_color="#D76C82", hover_color="#B03052").pack(anchor="w", padx=40)

        ctk.CTkButton(self.frame, text="Siguiente", command=self.siguiente,
                      fg_color="#D76C82", hover_color="#B03052",
                      text_color="white", font=("Century Gothic", 13, "bold"), corner_radius=20, width=140).pack(pady=25)

    def siguiente(self):
        clave = self.preguntas[self.indice][1]
        valor = self.respuesta.get() if isinstance(self.respuesta, ctk.StringVar) else self.respuesta.get().strip()
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
            ctk.CTkLabel(self.frame, text="No se encontraron productos recomendados.", text_color="#3D0301", font=("Century Gothic", 14)).pack(pady=20)
            return

        ctk.CTkLabel(self.frame, text="Productos recomendados:", text_color="#B03052", font=("Century Gothic", 15, "bold")).pack(pady=10)

        for resultado in resultados:
            nombre_base = resultado["B"]
            ctk.CTkLabel(self.frame, text=nombre_base, text_color="#3D0301", font=("Century Gothic", 13, "bold")).pack()

            if nombre_base in imagenes:
                try:
                    img = CTkImage(Image.open(imagenes[nombre_base]))
                    img_label = ctk.CTkLabel(self.frame, image=img, text="")
                    img_label.image = img
                    img_label.pack()
                except Exception as e:
                    print(f"Error al cargar imagen de producto {nombre_base}: {e}")
                    ctk.CTkLabel(self.frame, text="[Imagen no disponible]").pack()

            if nombre_base in descripciones:
                ctk.CTkLabel(self.frame, text=descripciones[nombre_base], text_color="#3D0301", font=("Century Gothic", 12), wraplength=400).pack(pady=5)

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Sistema Experto de Maquillaje")
    app = CuestionarioApp(root)
    root.mainloop()


