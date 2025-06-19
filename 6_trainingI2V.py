# 6_training.py
# Versão corrigida para ambiente Runpod (sem venv)
import sys
import subprocess
import argparse
from pathlib import Path

# --- (‼️) CONFIGURAÇÃO PRINCIPAL - EDITE AQUI (‼️) ---
# Coloque aqui o nome EXATO do arquivo do modelo DiT que você usa para este treino.
DIT_MODEL_FILE = "wan2.1_i2v_480p_14B_fp16.safetensors" # ⬅️⬅️⬅️ VERIFIQUE E EDITE ESTA LINHA SE NECESSÁRIO
# --- FIM DAS CONFIGURAÇÕES ---

# --- Lógica do Script (não precisa editar abaixo) ---
REPO_DIR = "musubi-tuner-main"
MODELS_DIR = "models"

# Hiperparâmetros baseados no seu comando preferido
TASK = "i2v-14B"
LEARNING_RATE = "6e-5"
NETWORK_DIM = "32"
MAX_TRAIN_EPOCHS = "50"
SAVE_EVERY_N_EPOCHS = "4"
#SAVE_EVERY_N_STEPS = "5" # Adicionado baseado no seu comando original
SEED = "748"

def run_command_realtime(command, error_msg):
    """Executa um comando e exibe sua saída em tempo real, linha por linha."""
    print(f"\n▶️  Iniciando o treinamento... O comando completo é:")
    # Formata o comando para melhor legibilidade
    formatted_command = " \\\n   ".join(f'"{c}"' if " " in c else c for c in command)
    print(f"   {formatted_command}")
    print("\n" + "="*60)
    print("A saída do treinamento aparecerá abaixo. Pode levar um tempo para começar.")
    print("="*60 + "\n")
    
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding='utf-8', bufsize=1
        )
        for line in process.stdout:
            print(line, end='', flush=True)
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO: {error_msg}")
        print(f"   O treinamento falhou com o código de saída: {e.returncode}.")
        print("   Verifique a saída de erro acima.")
        sys.exit(1)

def main(args):
    """Função principal para configurar e iniciar o treinamento."""
    print("=" * 60)
    print(f"🚀 Iniciando Script de Treinamento da LoRA: '{args.name}' 🚀")
    print("=" * 60)
    
    workspace_dir = Path("/workspace")
    
    # --- Verificações ---
    print("\n🔍 Verificando o ambiente em /workspace...")
    repo_path = workspace_dir / REPO_DIR
    dit_model_path = workspace_dir / MODELS_DIR / DIT_MODEL_FILE
    dataset_toml_path = workspace_dir / args.dataset_toml
    
    paths_to_check = { "Repositório Musubi": repo_path, "Modelo DiT": dit_model_path, "Dataset TOML": dataset_toml_path }
    all_ok = True
    for name, path in paths_to_check.items():
        if not path.exists():
            print(f"   ❌ ERRO: {name} não encontrado em '{path}'"); all_ok = False
    if not all_ok:
        print("\nCertifique-se de que o nome do arquivo DIT_MODEL_FILE está correto no topo do script."); sys.exit(1)
        
    output_dir = workspace_dir / "outputs" / args.name
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✅ Ambiente verificado. A saída será salva em '{output_dir}'")

    # --- Construção do Comando ---
    train_script = str(repo_path / "src/musubi_tuner/wan_train_network.py")
    
    # Argumentos do otimizador separados corretamente
    optimizer_args_list = ["betas=0.9,0.999,0.9999", "weight_decay=0.01", "eps=1e-30,1e-16"]

    command = [
        "accelerate", "launch", "--num_cpu_threads_per_process", "1", "--mixed_precision", "fp16",
        train_script,
        "--task", TASK,
        "--dit", str(dit_model_path),
        "--dataset_config", str(dataset_toml_path),
        "--sdpa",
        "--split_attn",
        "--blocks_to_swap","16",
        "--optimizer_type", "came_pytorch.CAME.CAME",
        "--learning_rate", LEARNING_RATE,
        "--max_data_loader_n_workers", "2",
        "--mixed_precision", "fp16", 
        "--persistent_data_loader_workers",
        "--network_module", "networks.lora_wan",
        "--network_dim", NETWORK_DIM,
        "--network_alpha",NETWORK_DIM,
        "--timestep_sampling", "shift",
        "--discrete_flow_shift", "3.5",
        "--max_train_epochs", MAX_TRAIN_EPOCHS,
        "--save_every_n_epochs", SAVE_EVERY_N_EPOCHS,
        "--seed", SEED,
        "--output_dir", str(output_dir),
        "--output_name", args.name,
        "--network_args", "loraplus_lr_ratio=4",
        "--lr_scheduler", "constant_with_warmup",
        "--lr_warmup_steps","100",
        "--fp8_base",
        "--fp8_scaled",
        "--gradient_checkpointing",
        "--optimizer_args", *optimizer_args_list # CORREÇÃO: Passando como argumentos separados
    ]

    # --- Execução ---
    run_command_realtime(command, "Ocorreu um erro durante o treinamento.")
    
    print("\n" + "=" * 60)
    print(f"🎉 Treinamento '{args.name}' concluído com sucesso! 🎉")
    print(f"   Seus modelos LoRA foram salvos em: '{output_dir.resolve()}'")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inicia um treinamento de LoRA para Wan2.1 com configurações personalizadas.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("name", type=str, help="O nome para esta sessão de treinamento.\nSerá usado para criar a pasta de saída e nomear os arquivos LoRA.")
    parser.add_argument("--dataset_toml", type=str, default="dataset.toml", help="Nome do arquivo de configuração do dataset .toml (padrão: dataset.toml)")
    parsed_args = parser.parse_args()
    main(parsed_args)
