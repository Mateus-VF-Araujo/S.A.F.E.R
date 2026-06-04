import os
import subprocess
import time
import webbrowser
from pathlib import Path

def run_command(cmd, cwd=None, block=True):
    if block:
        return subprocess.run(cmd, shell=True, cwd=cwd)
    else:
        return subprocess.Popen(cmd, shell=True, cwd=cwd)

def main():
    base_dir = Path(__file__).resolve().parent
    frontend_dir = base_dir / "frontEnd"
    backend_dir = base_dir / "face_recognition"
    db_dir = base_dir / "database"
    node_modules_dir = frontend_dir / "node_modules"

    print("="*50)
    print("Iniciando S.A.F.E.R")
    print("="*50)

    print("\n[1/5] Sincronizando ambiente Python (uv sync)...")
    run_command("uv sync", cwd=base_dir)

    print("\n[2/5] Verificando dependências do React...")
    if not node_modules_dir.exists():
        print("      Pasta 'node_modules' não encontrada. Baixando pacotes do NPM...")
        run_command("npm install", cwd=frontend_dir)
    else:
        print("Dependências do Node já estão instaladas. Pulando etapa.")

    print("\n[3/5] Inicializando Tabelas no MySQL...")
    run_command("uv run python database.py", cwd=db_dir)

    print("\n[4/5] Subindo os servidores (FastAPI e Vite)...")
    backend_process = run_command(
        "uv run uvicorn model_stream:app --reload --port 8000", 
        cwd=backend_dir, 
        block=False
    )
    
    frontend_process = run_command(
        "npm run dev", 
        cwd=frontend_dir, 
        block=False
    )

    print("\n[5/5] Abrindo a interface no navegador...")
    time.sleep(3) 
    webbrowser.open("http://localhost:5173")

    print("\n" + "="*50)
    print("Sistema online.\n\nPressione [Ctrl+C] no terminal para desligar os servidores.")
    print("="*50 + "\n")

    # Mantém o script rodando para segurar os processos
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nEncerrando S.A.F.E.R...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servidores desligados com sucesso.")

if __name__ == "__main__":
    main()