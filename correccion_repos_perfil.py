import os
import requests
import subprocess
from openai import OpenAI
import argparse

# Configura la API de OpenAI usando una variable de entorno
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Directorio de destino para los repositorios
directorio_destino = "./repositorios_alumnos"

# Prompt de evaluación para la API de OpenAI
with open('correccion_repos_perfil.prompt', 'r', encoding='utf-8') as file:
    prompt_evaluacion = file.read().strip()

# Crea el directorio de destino si no existe
os.makedirs(directorio_destino, exist_ok=True)

# Función para descargar repositorios de un usuario
def descargar_repositorios(usuario):
    print(f"Descargando repositorio de: {usuario}")
    url = f"https://api.github.com/users/{usuario}/repos"
    respuesta = requests.get(url)

    if respuesta.status_code == 200:
        repos = respuesta.json()
        # Filtrar el repositorio que coincide con el nombre de usuario
        for repo in repos:
            if repo['name'] == usuario:
                nombre_repo = repo['name']
                clone_url = repo['clone_url']
                ruta_repo = os.path.join(directorio_destino, usuario, nombre_repo)
                os.makedirs(os.path.dirname(ruta_repo), exist_ok=True)

                # Clonar el repositorio si no existe
                if not os.path.exists(ruta_repo):
                    print(f"Clonando {nombre_repo}...")
                    subprocess.run(["git", "clone", clone_url, ruta_repo])
                else:
                    print(f"El repositorio {nombre_repo} ya existe. Saltando descarga...")

                # Evaluar el README.md independientemente de si el repositorio fue clonado o ya existía
                evaluar_readme(ruta_repo)
                break  # Salir del bucle después de encontrar el repositorio correcto
        else:
            print(f"No se encontró un repositorio con el nombre '{usuario}'.")
    else:
        print(f"Error al obtener los repositorios para {usuario} - Status Code: {respuesta.status_code}")

# Función para evaluar el README.md con la API de OpenAI
def evaluar_readme(ruta_repo):
    readme_path = os.path.join(ruta_repo, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            contenido_readme = f.read()

        # Usar openai.ChatCompletion para los modelos de la serie GPT
        respuesta = client.chat.completions.create(model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that evaluates README.md files."},
            {"role": "user", "content": f"{prompt_evaluacion}\n\n{contenido_readme}"}
        ],
        max_tokens=1500,
        temperature=0.25)

        evaluacion = respuesta.choices[0].message.content.strip()
        print(f"Evaluación del README.md de {ruta_repo}:\n{evaluacion}\n")
    else:
        print(f"No se encontró README.md en {ruta_repo}")

# Configuración de argumentos de línea de comandos
parser = argparse.ArgumentParser(description="Descargar y evaluar repositorios de un usuario de GitHub")
parser.add_argument('usuario', type=str, help="Nombre de usuario de GitHub del alumno")
args = parser.parse_args()

# Ejecutar la descarga y evaluación para el usuario proporcionado
descargar_repositorios(args.usuario)

print("Descarga y evaluación de repositorios completada.")