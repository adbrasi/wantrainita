#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=========================================================================================
 Pipeline Step 2: Download Essential Models for Wan 2.1 Training (Optimized)
=========================================================================================
DESCRIÇÃO:
  Este script orquestra o download de todos os modelos e arquivos necessários
  para o treinamento LoRA. Ele utiliza 'huggingface-cli' com 'hf_transfer'
  para downloads acelerados e salva os arquivos em um diretório 'models' local.

FUNCIONALIDADES:
  1. Cria um diretório 'models' no local de execução do script.
  2. Unifica todos os downloads através da biblioteca Hugging Face para consistência.
  3. Verifica e instala as dependências 'huggingface-hub[cli]' e 'hf_transfer' para
     garantir downloads em alta velocidade.
  4. Evita baixar novamente arquivos que já existem no diretório de destino.
  5. Exibe o progresso do download em tempo real no terminal.
  6. Organiza os arquivos baixados, movendo-os para a raiz do diretório 'models'
     e limpando as subpastas criadas pelo downloader.

COMO USAR:
  - Navegue até a pasta do seu projeto no terminal.
  - Execute o script. Ele criará uma pasta 'models' e baixará os arquivos nela.
    python lora_training_pipeline/2_download_wan_files.py
=========================================================================================
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# --- PASTA DE DESTINO LOCAL ---
# O diretório 'models' será criado no diretório de trabalho atual.
CWD = Path.cwd()
MODELS_DIR = CWD / "models"

# --- CONFIGURAÇÃO DOS ARQUIVOS A SEREM BAIXADOS PELO HUGGING FACE ---
# Todos os modelos, incluindo o clip_vision, estão listados aqui.
MODELS_TO_DOWNLOAD = [
    {
        "repo_id": "Comfy-Org/Wan_2.1_ComfyUI_repackaged",
        "repo_filename": "split_files/diffusion_models/wan2.1_t2v_14B_fp16.safetensors",
        "local_filename": "wan2.1_t2v_14B_fp16.safetensors"
    },
    {
        "repo_id": "Wan-AI/Wan2.1-T2V-14B",
        "repo_filename": "Wan2.1_VAE.pth",
        "local_filename": "Wan2.1_VAE.pth"
    },
    {
        "repo_id": "Wan-AI/Wan2.1-T2V-14B",
        "repo_filename": "models_t5_umt5-xxl-enc-bf16.pth",
        "local_filename": "models_t5_umt5-xxl-enc-bf16.pth"
    },
    {
        "repo_id": "Wan-AI/Wan2.1-I2V-14B-720P",
        "repo_filename": "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth",
        "local_filename": "models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth"
    }
]

def check_and_install_dependencies():
    """Verifica e instala 'huggingface-hub[cli]' e 'hf_transfer'."""
    print("--- Verificando Dependências para Download Acelerado ---")
    pip_executable = [sys.executable, "-m", "pip"]
    
    packages = {
        "huggingface_hub": "huggingface_hub[cli]",
        "hf_transfer": "hf_transfer"
    }
    
    needs_install = False
    for import_name, install_name in packages.items():
        try:
            # Tenta importar o pacote para verificar se está instalado
            __import__(import_name)
            print(f"✅ '{install_name}' já está instalado.")
        except ImportError:
            print(f"⚠️  '{install_name}' não encontrado. Instalando...")
            try:
                # Executa o pip install e mostra a saída para o usuário
                subprocess.run(
                    pip_executable + ["install", "-U", install_name],
                    check=True
                )
                print(f"   -> '{install_name}' instalado com sucesso.")
                needs_install = True
            except subprocess.CalledProcessError as e:
                print(f"\n❌ ERRO: Falha ao instalar '{install_name}'.", file=sys.stderr)
                print(f"Por favor, tente instalar manualmente: pip install -U \"{install_name}\"", file=sys.stderr)
                sys.exit(1)
    
    if needs_install:
        print("\nDependências instaladas. Continuando com o script.")
    else:
        print("Todas as dependências necessárias estão prontas.\n")


def download_required_files():
    """
    Orquestra o download acelerado de todos os arquivos necessários usando
    huggingface-cli com hf_transfer.
    """
    print(f"--- Iniciando download dos modelos para '{MODELS_DIR.resolve()}' ---")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    for model_info in MODELS_TO_DOWNLOAD:
        repo_id = model_info["repo_id"]
        repo_filename = model_info["repo_filename"]
        local_filename = model_info["local_filename"]
        
        final_destination_path = MODELS_DIR / local_filename
        
        print(f"\n▶️  Processando: {local_filename}")

        if final_destination_path.exists():
            print(f"  ✅ Arquivo já existe. Pulando.")
            continue

        # Comando para download com hf_transfer habilitado
        command = [
            "huggingface-cli", "download",
            repo_id,
            repo_filename,
            "--local-dir", str(MODELS_DIR),
            "--local-dir-use-symlinks", "False",
            "--force-download" # Garante que baixe mesmo se um arquivo parcial existir
        ]
        
        # Define o ambiente para habilitar o download rápido
        download_env = os.environ.copy()
        download_env["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
        
        print(f"  📥 Baixando de '{repo_id}' (usando hf_transfer)...")
        try:
            # Executa o comando sem capturar a saída para mostrar o progresso
            subprocess.run(command, env=download_env, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n❌ ERRO ao baixar '{local_filename}'.", file=sys.stderr)
            print(f"  Comando executado: {' '.join(command)}", file=sys.stderr)
            # Continua para o próximo arquivo em caso de erro
            continue
        except FileNotFoundError:
            print("\n❌ ERRO: 'huggingface-cli' não encontrado.", file=sys.stderr)
            print("   Certifique-se de que as dependências foram instaladas corretamente.", file=sys.stderr)
            sys.exit(1)

        # O `huggingface-cli` baixa mantendo a estrutura de pastas do repositório
        # Ex: models/split_files/clip_vision/clip_vision_h.safetensors
        downloaded_file_path = MODELS_DIR / repo_filename
        
        if not downloaded_file_path.exists():
            print(f"  ❌ ERRO PÓS-DOWNLOAD: Arquivo '{downloaded_file_path}' não encontrado.", file=sys.stderr)
            continue
            
        # Move o arquivo para a raiz do diretório 'models'
        print(f"  🚚 Movendo arquivo para o destino final...")
        try:
            shutil.move(str(downloaded_file_path), str(final_destination_path))
        except Exception as e:
            print(f"  ❌ ERRO ao mover o arquivo: {e}", file=sys.stderr)
            continue

        # Limpa as pastas vazias criadas pelo download (ex: 'split_files')
        try:
            # Obtém o diretório de primeiro nível criado dentro de MODELS_DIR
            top_level_created_dir = MODELS_DIR / Path(repo_filename).parts[0]
            if top_level_created_dir.is_dir() and not any(top_level_created_dir.iterdir()):
                 shutil.rmtree(top_level_created_dir)
                 print(f"  🧹 Limpeza da pasta vazia '{top_level_created_dir.name}' concluída.")
        except (IndexError, FileNotFoundError):
            # Ignora se o arquivo não estava em um subdiretório
            pass
        
        print(f"  ✔️  '{local_filename}' pronto!")
        
    print("\n--- Download de todos os arquivos concluído ---")


if __name__ == "__main__":
    try:
        print("=========================================================")
        print("  INICIANDO PIPELINE DE DOWNLOAD DE MODELOS (OTIMIZADO)  ")
        print("=========================================================")
        
        check_and_install_dependencies()
        download_required_files()
        
        print("\n" + "="*57)
        print("✅         TODOS OS DOWNLOADS FORAM CONCLUÍDOS         ✅")
        print("="*57)
        print(f"Todos os arquivos foram salvos em: {MODELS_DIR.resolve()}")

    except KeyboardInterrupt:
        print("\n\nOperação interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nOcorreu um erro inesperado no pipeline: {e}", file=sys.stderr)
        sys.exit(1)