import os
import subprocess
import datetime
import sys

MAX_SIZE_MB = 100

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Error:", e.stderr)
        return False

def find_large_files(path):
    large_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                size_mb = os.path.getsize(full_path) / (1024 * 1024)
                if size_mb > MAX_SIZE_MB:
                    large_files.append(full_path)
            except:
                pass
    return large_files

def add_to_gitignore(files):
    if not files:
        return

    print("⚠️ Archivos grandes detectados, se ignorarán:")
    with open(".gitignore", "a") as f:
        for file in files:
            relative_path = os.path.relpath(file)
            print(" -", relative_path)
            f.write(relative_path.replace("\\", "/") + "\n")

def auto_git(repo_url):
    # 🔥 Detecta automáticamente la ruta actual
    ruta = os.getcwd()
    print(f"📁 Trabajando en: {ruta}")

    # Inicializar git
    if not os.path.exists(".git"):
        if not run_command("git init"):
            return
        print("✔ Repositorio inicializado")

    # Crear .gitignore si no existe
    if not os.path.exists(".gitignore"):
        with open(".gitignore", "w") as f:
            f.write("""node_modules/
*.log
.env
dist/
build/
*.exe
*.zip
*.rar
""")
        print("✔ .gitignore creado")

    # Detectar archivos grandes
    large_files = find_large_files(ruta)
    add_to_gitignore(large_files)

    # Limpiar cache
    run_command("git rm -r --cached .")

    # Remote
    remotes = subprocess.getoutput("git remote")
    if "origin" not in remotes:
        if not run_command(f"git remote add origin {repo_url}"):
            return
        print("✔ Remote agregado")

    # Agregar archivos
    if not run_command("git add ."):
        return

    # Verificar cambios
    status = subprocess.getoutput("git status --porcelain")
    if not status.strip():
        print("ℹ️ No hay cambios para subir")
        return

    # Commit
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not run_command(f'git commit -m "Auto commit {fecha}"'):
        return

    # Push
    if not run_command("git branch -M main"):
        return

    if not run_command("git push -u origin main"):
        print("❌ Falló el push")
        return

    print("🚀 Proyecto subido correctamente")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso:")
        print("python auto_git.py <url_repositorio>")
    else:
        repo = sys.argv[1]
        auto_git(repo)