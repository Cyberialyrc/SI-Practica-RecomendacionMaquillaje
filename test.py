from pyswip import Prolog

# Crear el objeto Prolog
prolog = Prolog()

# Consultar el archivo de Prolog
prolog.consult("maquillaje.pl")

list(prolog.query("registrar_usuario(percy, seca, no, media, liquida)."))

# Realizar la consulta de recomendación
resultados = list(prolog.query("recomendar_base(percy, X)."))

# Mostrar los resultados
if resultados:
    print("Bases recomendadas:")
    for resultado in resultados:
        print(resultado["X"])  # Aquí accedemos a la variable "X" que contiene las bases recomendadas
else:
    print("No se encontraron recomendaciones.")
print("Resultados completos:", resultados)
