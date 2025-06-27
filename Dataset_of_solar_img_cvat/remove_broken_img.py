from PIL import UnidentifiedImageError
import os
from PIL import Image
import argparse


def check_png_file(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except UnidentifiedImageError:
        print(f"НЕВАЛИДНО, УДАЛЯЕМ: {file_path} (UnidentifiedImageError)")
        os.remove(file_path)
        return False
    except Exception as e:
        print(f"Ошибка в {file_path}: {e}")
        return False


def check_png_files(directory):
    removed = 0
    for filename in os.listdir(directory):
        if filename.lower().endswith(".png"):
            path = os.path.join(directory, filename)
            if not check_png_file(path):
                removed += 1
    print(f"Удалено файлов: {removed}")
    return removed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Проверка PNG файлов в директории.")
    parser.add_argument("--mode", type=str, choices=["dir", "file"], default="dir",
                        help="Режим работы: 'dir' для проверки директории, 'file' для проверки одного файла.")
    parser.add_argument("--directory", type=str, help="Папка с PNG файлами.")
    parser.add_argument("--file", type=str,
                        help="Путь к одному PNG файлу для проверки.")
    args = parser.parse_args()
    if args.mode == "dir":
        if not args.directory:
            print("Не указана директория.")
            exit(1)
        removed = check_png_files(args.directory)
        print(f"Всего удалено файлов: {removed}")
    elif args.mode == "file":
        if not args.file:
            print("Не указан файл.")
            exit(1)
        result = check_png_file(args.file)
        if result:
            print(f"Файл {args.file} валиден.")
        else:
            print(f"Файл {args.file} был удалён или невалиден.")


"python -m remove_broken_img --mode dir --directory 'Dataset/ssrt_images_channel_6000'"
