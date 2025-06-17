# 5_run_precaching.py
# Versão corrigida para ambiente Runpod (sem venv)
import sys
import subprocess
from pathlib import Path

# --- CONFIGURAÇÕES ---
# Nomes dos diretórios e arquivos que o script espera encontrar no /workspace
REPO_DIR = "musubi-tuner-main"
MODELS_DIR = "models"
DATASET_CONFIG = "dataset.toml"

# Nomes dos arquivos de modelo
VAE_FILE = "Wan2.1_VAE.pth"
CLIP_FILE = "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth"
T5_FILE = "models_t5_umt5-xxl-enc-bf16.pth"
BATCH_SIZE = "16" # O batch size para o cache do text encoder

def run_command_realtime(command, error_msg):
    """Executa um comando e exibe sua saída em tempo real."""
    print(f"\n▶️  Executando: {' '.join(command)}")
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1 
        )
        
        for line in process.stdout:
            print(line, end='')

        process.wait()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO: {error_msg}")
        print(f"   O comando falhou com o código de saída: {e.returncode}.")
        print("   Verifique a saída de erro acima para mais detalhes.")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ ERRO: Comando '{command[0]}' não encontrado.")
        sys.exit(1)

def main():
    """Função principal que orquestra as verificações e a execução dos scripts."""
    print("=" * 60)
    print("🚀 Iniciando Scripts de Pré-Cache do Musubi 🚀")
    print("=" * 60)
    
    # Define os caminhos a partir de /workspace
    workspace_dir = Path("/workspace")
    paths_to_check = {
        "Repositório (musubi-tuner-main)": workspace_dir / REPO_DIR,
        "Arquivo de configuração (dataset.toml)": workspace_dir / DATASET_CONFIG,
        f"Modelo VAE ({VAE_FILE})": workspace_dir / MODELS_DIR / VAE_FILE,
        f"Modelo CLIP ({CLIP_FILE})": workspace_dir / MODELS_DIR / CLIP_FILE,
        f"Modelo T5 ({T5_FILE})": workspace_dir / MODELS_DIR / T5_FILE,
    }
    
    print("\n🔍 Verificando se todos os arquivos e pastas necessários existem em /workspace...")
    all_ok = True
    for name, path in paths_to_check.items():
        if not path.exists():
            print(f"   ❌ ERRO: {name} não encontrado em '{path}'")
            all_ok = False
            
    if not all_ok:
        print("\nPor favor, execute os scripts anteriores ou verifique os nomes/locais dos arquivos.")
        sys.exit(1)
    
    print("   ✅ Todos os arquivos e pastas foram encontrados!")

    # --- PASSO 1: CACHE DE LATENTS (VAE + CLIP) ---
    print("\n" + "-" * 20 + " PASSO 1: Cache de Latents (VAE) " + "-" * 20)
    
    latents_script_path = str(workspace_dir / REPO_DIR / "src/musubi_tuner/wan_cache_latents.py")
    command1 = [
        "python", # Usa o python do ambiente do Pod
        latents_script_path,
        "--dataset_config", str(paths_to_check["Arquivo de configuração (dataset.toml)"]),
        "--vae", str(paths_to_check[f"Modelo VAE ({VAE_FILE})"]),
        "--clip", str(paths_to_check[f"Modelo CLIP ({CLIP_FILE})"])
    ]
    run_command_realtime(command1, "Falha ao executar o cache de latents.")
    print("\n✅ Cache de latents concluído com sucesso!")

    # --- PASSO 2: CACHE DE SAÍDAS DO TEXT ENCODER (T5) ---
    print("\n" + "-" * 15 + " PASSO 2: Cache de Text Encoder (T5) " + "-" * 15)
    
    text_encoder_script_path = str(workspace_dir / REPO_DIR / "src/musubi_tuner/wan_cache_text_encoder_outputs.py")
    command2 = [
        "python", # Usa o python do ambiente do Pod
        text_encoder_script_path,
        "--dataset_config", str(paths_to_check["Arquivo de configuração (dataset.toml)"]),
        "--t5", str(paths_to_check[f"Modelo T5 ({T5_FILE})"]),
        "--batch_size", BATCH_SIZE
    ]
    run_command_realtime(command2, "Falha ao executar o cache do text encoder.")
    print("\n✅ Cache do text encoder concluído com sucesso!")

    # --- CONCLUSÃO ---
    print("\n" + "=" * 60)
    print("🎉 Scripts de pré-cache concluídos com sucesso! 🎉")
    print("=" * 60)
    print("\nAgora você está pronto para iniciar o treinamento principal com '6_training.py'")

if __name__ == "__main__":
    main()