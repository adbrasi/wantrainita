#!/bin/bash

# Script para instalar e executar WD-LLM-Caption-CLI
# Uso: ./wd_caption_installer.sh <caminho_da_pasta_com_videos>

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verifica se foi passado o caminho da pasta
if [ -z "$1" ]; then
    log_error "Uso: $0 <caminho_da_pasta_com_videos>"
    exit 1
fi

VIDEO_PATH="$1"

# Verifica se a pasta existe
if [ ! -d "$VIDEO_PATH" ]; then
    log_error "Pasta não encontrada: $VIDEO_PATH"
    exit 1
fi

# Diretório base para instalação (mesmo diretório do script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$SCRIPT_DIR/wd-llm-caption-cli"
FRAMES_DIR="$SCRIPT_DIR/extracted_frames"

log_info "Iniciando processo de instalação e execução..."
log_info "Pasta de vídeos: $VIDEO_PATH"
log_info "Diretório de instalação: $INSTALL_DIR"

# Função para instalar OpenCV se não estiver instalado
install_opencv() {
    log_info "Verificando OpenCV para extração de frames..."
    
    # Verifica se OpenCV está instalado no ambiente atual
    if python3 -c "import cv2" 2>/dev/null; then
        log_success "OpenCV já está disponível."
        return 0
    fi
    
    log_info "OpenCV não encontrado. Instalando..."
    pip3 install opencv-python-headless
    log_success "OpenCV instalado com sucesso!"
}

# Função para extrair frames dos vídeos usando Python/OpenCV
extract_frames() {
    log_info "Extraindo primeiro frame de cada vídeo usando OpenCV..."
    
    # Cria diretório para frames se não existir
    mkdir -p "$FRAMES_DIR"
    
    # Cria script Python temporário para extração de frames
    cat > "/tmp/extract_frames.py" << 'EOF'
import cv2
import os
import sys
from pathlib import Path

def extract_first_frame(video_path, output_path):
    """Extrai o primeiro frame de um vídeo usando OpenCV"""
    try:
        # Abre o vídeo
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Erro: Não foi possível abrir o vídeo {video_path}")
            return False
        
        # Lê o primeiro frame
        ret, frame = cap.read()
        
        if not ret:
            print(f"Erro: Não foi possível ler o primeiro frame de {video_path}")
            cap.release()
            return False
        
        # Salva o frame como imagem
        success = cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Libera o vídeo
        cap.release()
        
        if success:
            print(f"✓ Frame extraído: {os.path.basename(output_path)}")
            return True
        else:
            print(f"Erro: Falha ao salvar {output_path}")
            return False
            
    except Exception as e:
        print(f"Erro ao processar {video_path}: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Uso: python extract_frames.py <pasta_videos> <pasta_frames>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    frames_path = sys.argv[2]
    
    # Extensões de vídeo suportadas
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v', '.flv', '.wmv', '.3gp', '.m2v'}
    
    # Encontra todos os vídeos
    video_files = []
    for ext in video_extensions:
        video_files.extend(Path(video_path).glob(f'*{ext}'))
        video_files.extend(Path(video_path).glob(f'*{ext.upper()}'))
    
    if not video_files:
        print("Nenhum vídeo encontrado na pasta especificada.")
        return
    
    print(f"Encontrados {len(video_files)} vídeos para processar.")
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for i, video_file in enumerate(video_files, 1):
        # Nome do arquivo sem extensão
        name_without_ext = video_file.stem
        output_frame = Path(frames_path) / f"{name_without_ext}.jpg"
        
        # Verifica se o frame já foi extraído
        if output_frame.exists():
            print(f"[{i}/{len(video_files)}] Frame já existe: {name_without_ext}.jpg")
            skip_count += 1
            continue
        
        print(f"[{i}/{len(video_files)}] Extraindo frame de: {video_file.name}")
        
        # Extrai o frame
        if extract_first_frame(str(video_file), str(output_frame)):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\n=== Resumo da extração ===")
    print(f"Sucessos: {success_count}")
    print(f"Já existiam: {skip_count}")
    print(f"Erros: {error_count}")
    print(f"Total processado: {len(video_files)}")

if __name__ == "__main__":
    main()
EOF
    
    # Executa o script Python
    python3 /tmp/extract_frames.py "$VIDEO_PATH" "$FRAMES_DIR"
    
    # Remove o script temporário
    rm -f /tmp/extract_frames.py
    
    log_success "Extração de frames concluída!"
}

# Função para instalar o projeto
install_project() {
    log_info "Verificando instalação do projeto..."
    
    # Se o diretório não existe, clona o repositório
    if [ ! -d "$INSTALL_DIR" ]; then
        log_info "Clonando repositório..."
        cd "$SCRIPT_DIR"
        git clone https://github.com/fireicewolf/wd-llm-caption-cli.git
        log_success "Repositório clonado!"
    else
        log_success "Repositório já existe."
    fi
    
    cd "$INSTALL_DIR"
    
    # Verifica se o venv já existe
    if [ ! -d ".venv" ]; then
        log_info "Criando ambiente virtual Python..."
        python3 -m venv .venv
        log_success "Ambiente virtual criado!"
    else
        log_success "Ambiente virtual já existe."
    fi
    
    # Ativa o ambiente virtual
    log_info "Ativando ambiente virtual..."
    source .venv/bin/activate
    
    # Verifica se pip está atualizado
    pip install --upgrade pip
    pip install einops
    # Instala dependências se necessário
    log_info "Verificando e instalando dependências..."
    
    # Instala PyTorch
    if ! python -c "import torch" 2>/dev/null; then
        log_info "Instalando PyTorch..."
        pip install torch==2.5.0 --index-url https://download.pytorch.org/whl/cpu
    fi
    
    # Instala dependências LLM
    if [ -f "requirements_llm.txt" ]; then
        log_info "Instalando dependências LLM..."
        pip install -U -r requirements_llm.txt
    fi
    
    # Instala dependências Hugging Face
    if [ -f "requirements_huggingface.txt" ]; then
        log_info "Instalando dependências Hugging Face..."
        pip install -U -r requirements_huggingface.txt
    fi
    
    log_success "Instalação concluída!"
}

# Função para executar o caption
run_caption() {
    log_info "Executando geração de captions..."
    
    cd "$INSTALL_DIR"
    source .venv/bin/activate
    
    # Verifica se existem frames para processar
    frame_count=$(find "$FRAMES_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) 2>/dev/null | wc -l)
    
    if [ "$frame_count" -eq 0 ]; then
        log_error "Nenhum frame encontrado para processar."
        exit 1
    fi
    
    log_info "Processando $frame_count frames..."
    
    # Executa o comando de caption
    python caption.py \
        --data_path "$FRAMES_DIR" \
        --caption_method llm \
        --llm_choice florence \
        --llm_qnt 8bit \
        --caption_extension .txt \
        --log_level INFO \
        --not_overwrite
    
    log_success "Geração de captions concluída!"
}

# Função para mover captions para a pasta original
move_captions() {
    log_info "Movendo captions para a pasta original dos vídeos..."
    
    moved_count=0
    
    # Move os arquivos .txt gerados para a pasta original dos vídeos
    find "$FRAMES_DIR" -name "*.txt" -type f | while read -r caption_file; do
        filename=$(basename "$caption_file")
        target_path="$VIDEO_PATH/$filename"
        
        if [ -f "$target_path" ]; then
            log_warning "Caption já existe: $filename"
        else
            cp "$caption_file" "$target_path"
            log_success "Caption movido: $filename"
            moved_count=$((moved_count + 1))
        fi
    done
    
    log_success "Captions movidos para: $VIDEO_PATH"
}

# --- NOVA FUNÇÃO ADICIONADA ---
# Função para limpar frases indesejadas das captions
cleanup_captions() {
    log_info "Limpando frases indesejadas dos arquivos de caption..."
    
    # Verifica se existem arquivos .txt para processar
    if ! compgen -G "$VIDEO_PATH/*.txt" > /dev/null; then
        log_warning "Nenhum arquivo .txt encontrado para limpar."
        return
    fi
    
    local cleaned_count=0
    # Loop através de todos os arquivos .txt na pasta de destino
    for caption_file in "$VIDEO_PATH"/*.txt; do
        if [ -f "$caption_file" ]; then
            # Usa 'sed' para remover as frases indesejadas (case-insensitive)
            # -e: permite múltiplos comandos
            # s/.../.../gI: substitui globalmente e ignora maiúsculas/minúsculas
            # s/^[[:space:]]*//: remove espaços/tabs no início da linha
            sed -i \
                -e 's/The image shows //gI' \
                -e 's/The image is //gI' \
                -e 's/The image show //gI' \
                -e 's/^[[:space:]]*//' \
                "$caption_file"
            
            cleaned_count=$((cleaned_count + 1))
        fi
    done
    
    log_success "$cleaned_count arquivos de caption foram limpos."
}
# --- FIM DA NOVA FUNÇÃO ---


# Função principal
main() {
    log_info "=== WD-LLM-Caption-CLI Auto Installer ==="
    
    # Instala OpenCV
    install_opencv
    
    # Extrai frames dos vídeos
    extract_frames
    
    # Instala o projeto
    install_project
    
    # Executa geração de captions
    run_caption
    
    # Move captions para pasta original
    move_captions
    
    # --- CHAMADA PARA A NOVA FUNÇÃO ---
    # Limpa as captions de frases indesejadas
    cleanup_captions
    # --- FIM DA CHAMADA ---
    
    log_success "=== Processo concluído com sucesso! ==="
    log_info "Os arquivos de caption (.txt) foram criados e limpos na pasta: $VIDEO_PATH"
    log_info "Os frames extraídos estão em: $FRAMES_DIR"
    log_info "Para executar novamente, use: $0 $VIDEO_PATH"
}

# Executa função principal
main