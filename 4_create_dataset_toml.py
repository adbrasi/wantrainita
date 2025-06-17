import pathlib
import os
import argparse

# O caminho de destino para o arquivo dataset.toml
OUTPUT_PATH = "./dataset.toml"

def create_dataset_toml(resolution, target_frames, source_fps, base_video_dir):
    """
    Gera o arquivo dataset.toml com base nos parâmetros fornecidos.

    Args:
        resolution (str): String formatada para a resolução, ex: "[256, 256]".
        target_frames (str): String formatada para os frames, ex: "[1, 25, 45]".
        source_fps (float): FPS do vídeo de origem, ex: 30.0.
        base_video_dir (str): O nome da pasta base para os vídeos.
    """
    # Define os caminhos de vídeo e cache dinamicamente
    video_dir = os.path.join(".", base_video_dir)
    cache_dir = os.path.join(video_dir, "cache")

    # Cria o conteúdo do TOML usando uma f-string com os parâmetros recebidos
    toml_content = f"""[general]
resolution = {resolution}
caption_extension = ".txt"
batch_size = 1
enable_bucket = true
bucket_no_upscale = false

[[datasets]]
video_directory = "{video_dir}"
cache_directory = "{cache_dir}"
target_frames = {target_frames}
frame_extraction = "head"
source_fps = {source_fps}
"""

    output_file = pathlib.Path(OUTPUT_PATH)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(toml_content)

    print(f"Arquivo `{OUTPUT_PATH}` criado/atualizado com sucesso com as seguintes configurações:")
    print(f" - Resolution:    {resolution}")
    print(f" - Target Frames: {target_frames}")
    print(f" - Source FPS:    {source_fps}")
    print(f" - Video Dir:     {video_dir}")
    print(f" - Cache Dir:     {cache_dir}")


def main():
    """
    Função principal para parsear argumentos e criar o arquivo de configuração.
    """
    parser = argparse.ArgumentParser(
        description="Gera um arquivo dataset.toml com configurações personalizadas.",
        formatter_class=argparse.RawTextHelpFormatter # Melhora a formatação da ajuda
    )

    # Argumentos para personalizar o dataset
    parser.add_argument(
        "-R", "--resolution",
        type=str,
        default="256x256",
        help="Resolução dos vídeos no formato LARGURAxALTURA.\n(padrão: 256x256)"
    )
    parser.add_argument(
        "-F", "--target_frames",
        type=str,
        default="1-25-45",
        help="Frames a serem extraídos, separados por hífen.\n(padrão: 1-25-45)"
    )
    parser.add_argument(
        "-S", "--source_fps",
        type=float,
        default=30.0,
        help="FPS do vídeo de origem.\n(padrão: 30.0)"
    )
    parser.add_argument(
        "-o", "--output_dir",
        type=str,
        default="videos_dataset",
        help="Diretório base para os vídeos e o cache.\n(padrão: videos_dataset)"
    )

    args = parser.parse_args()

    # --- Processamento dos argumentos para o formato TOML ---

    # Converte '256x256' para a string '[256, 256]'
    try:
        res_parts = [int(p.strip()) for p in args.resolution.split('x')]
        if len(res_parts) != 2: raise ValueError
        resolution_str = f"[{res_parts[0]}, {res_parts[1]}]"
    except (ValueError, IndexError):
        print(f"Erro: Formato de resolução inválido '{args.resolution}'. Use o formato LARGURAxALTURA (ex: 512x512).")
        return

    # Converte '1-25-45' para a string '[1, 25, 45]'
    try:
        frame_parts = [int(p.strip()) for p in args.target_frames.split('-')]
        target_frames_str = str(frame_parts)  # str() de uma lista já formata corretamente
    except ValueError:
        print(f"Erro: Formato de frames inválido '{args.target_frames}'. Use números separados por hífen (ex: 1-25-45).")
        return

    # O FPS já está no formato float, graças ao `type=float` no parser
    source_fps_float = args.source_fps

    # Chama a função principal com os valores processados
    create_dataset_toml(
        resolution=resolution_str,
        target_frames=target_frames_str,
        source_fps=source_fps_float,
        base_video_dir=args.output_dir
    )

if __name__ == "__main__":
    main()