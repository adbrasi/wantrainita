import os
import sys
import subprocess
import zipfile
import argparse

# --- INÍCIO DO BLOCO DE VERIFICAÇÃO DE DEPENDÊNCIAS ---
def check_and_install_packages():
    """
    Verifica se as dependências necessárias estão instaladas e, se não estiverem,
    tenta instalá-las usando o pip.
    """
    required_packages = ["requests", "tqdm"]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"A biblioteca '{package}' não foi encontrada. Instalando automaticamente...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"'{package}' instalado com sucesso.")
            except subprocess.CalledProcessError as e:
                print(f"Erro ao instalar '{package}'. Por favor, instale manualmente usando 'pip install {package}'.")
                print(f"Erro do subprocesso: {e}")
                sys.exit(1) # Encerra o script se a instalação falhar

# Executa a verificação e instalação antes de qualquer outra coisa
check_and_install_packages()
# --- FIM DO BLOCO DE VERIFICAÇÃO DE DEPENDÊNCIAS ---


# Agora que garantimos que os pacotes existem, podemos importá-los
import requests
from tqdm import tqdm


def download_file(url, destination_folder):
    """
    Baixa um arquivo de uma URL para uma pasta de destino.

    Args:
        url (str): A URL do arquivo a ser baixado.
        destination_folder (str): O caminho da pasta onde o arquivo será salvo.

    Returns:
        str: O caminho do arquivo baixado ou None se ocorrer um erro.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Lança uma exceção para códigos de erro HTTP

        filename = url.split('/')[-1]
        filepath = os.path.join(destination_folder, filename)

        total_size = int(response.headers.get('content-length', 0))

        print(f"Baixando o arquivo de: {url}")
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
        
        return filepath

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None

def extract_zip(zip_path, extract_to_dir):
    """
    Extrai um arquivo .zip para um diretório específico.

    Args:
        zip_path (str): O caminho para o arquivo .zip.
        extract_to_dir (str): O diretório onde o conteúdo será extraído.
    """
    try:
        print(f"Extraindo para o diretório: {extract_to_dir}")
        os.makedirs(extract_to_dir, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_dir)
        print("Extração concluída.")
    except zipfile.BadZipFile:
        print(f"Erro: O arquivo '{zip_path}' não é um arquivo zip válido.")
    except Exception as e:
        print(f"Ocorreu um erro durante a extração: {e}")


def main():
    """
    Função principal para orquestrar o download, extração e limpeza.
    """
    parser = argparse.ArgumentParser(
        description="Baixa e extrai um arquivo .zip."
    )
    parser.add_argument(
        "zip_url", 
        type=str, 
        help="A URL completa do arquivo .zip a ser baixado."
    )
    parser.add_argument(
        "-o", "--output_dir",
        type=str,
        default="videos_dataset",
        help="Diretório de destino para extrair os arquivos (padrão: videos_dataset)."
    )

    args = parser.parse_args()
    
    # O diretório de destino agora é flexível, vindo dos argumentos.
    extract_destination = args.output_dir
    
    # O arquivo zip será baixado no diretório atual para facilitar a limpeza.
    download_folder = "."

    downloaded_zip_path = download_file(args.zip_url, download_folder)

    if downloaded_zip_path:
        extract_zip(downloaded_zip_path, extract_destination)
        
        # Limpeza do arquivo .zip
        try:
            os.remove(downloaded_zip_path)
            print(f"Limpeza concluída. Arquivo .zip '{downloaded_zip_path}' removido.")
        except OSError as e:
            print(f"Erro ao remover o arquivo .zip: {e}")

if __name__ == "__main__":
    main()