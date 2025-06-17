#!/bin/bash
# Script de instalação CORRIGIDO para o Musubi Tuner no ambiente Runpod
# Versão 2: Corrige o conflito de dependência do torchaudio.
set -e

echo "-----------------------------------------------------"
echo "Iniciando a instalação do Musubi Tuner (v2)..."
echo "-----------------------------------------------------"
echo ""

# --- PASSO 1: Atualizar pacotes do sistema e instalar ferramentas úteis ---
echo "--> Atualizando lista de pacotes e instalando git e nano..."
apt-get update
apt-get install -y git nano
echo "--> Ferramentas do sistema instaladas."
echo ""

# --- PASSO 2: Clonar o repositório do Musubi Tuner ---
if [ -d "musubi-tuner-main" ]; then
    echo "--> Diretório 'musubi-tuner-main' já existe. Pulando a clonagem."
else
    echo "--> Clonando o repositório de https://github.com/kohya-ss/musubi-tuner..."
    git clone https://github.com/kohya-ss/musubi-tuner.git musubi-tuner-main
    echo "--> Repositório clonado com sucesso."
fi
cd musubi-tuner-main
echo ""

# --- PASSO 3: Atualizar PyTorch, torchvision e torchaudio (RECOMENDADO) ---
echo "--> Verificando a versão do PyTorch..."
CURRENT_PYTORCH_VERSION=$(python -c "import torch; print(torch.__version__)")
echo "    Versão atual do PyTorch: $CURRENT_PYTORCH_VERSION"
echo "    Versão recomendada pelo Musubi Tuner: 2.5.1 ou superior"
echo ""
echo "--> ATUALIZANDO torch, torchvision e torchaudio juntos para manter a compatibilidade..."
sleep 3

# CORREÇÃO: Adicionado 'torchaudio' à linha de atualização
pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
echo "--> Ecossistema PyTorch atualizado com sucesso."
echo ""


# --- PASSO 4: Instalar as dependências Python do Musubi Tuner ---
echo "--> Instalando as dependências Python a partir do pyproject.toml..."
pip install \
    "accelerate==1.6.0" \
    "av==14.0.1" \
    "bitsandbytes==0.45.4" \
    "diffusers==0.32.1" \
    "einops==0.7.0" \
    "huggingface-hub==0.30.0" \
    "opencv-python==4.10.0.84" \
    "pillow>=10.2.0" \
    "safetensors==0.4.5" \
    "toml==0.10.2" \
    "tqdm==4.67.1" \
    "transformers==4.46.3" \
    "voluptuous==0.15.2" \
    "ftfy==6.3.1" \
    "easydict==1.13"
echo "--> Dependências principais instaladas."
echo ""

# --- PASSO 5: Instalar dependências opcionais (para logging e visualização) ---
echo "--> Instalando dependências opcionais (matplotlib, tensorboard)..."
pip install matplotlib tensorboard prompt-toolkit
echo "--> Dependências opcionais instaladas."
echo ""


# --- PASSO 6: Instalar o Musubi Tuner ---
echo "--> Instalando o Musubi Tuner em modo editável..."
pip install -e .
echo "--> Musubi Tuner instalado com sucesso."
echo ""


# --- PASSO 7: Verificação Final ---
echo "--> Verificando se há dependências quebradas..."
pip check
echo "--> Verificação concluída. (Aviso sobre 'pycairo' pode ser ignorado com segurança)"
echo ""

echo "-----------------------------------------------------"
echo "✅ Instalação do Musubi Tuner concluída com sucesso!"
echo "-----------------------------------------------------"
echo "Você está no diretório: $(pwd)"
echo "O ambiente está pronto para o treinamento."