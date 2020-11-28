import math

from PIL import Image

import imagehash
import image_slicer
from stegano import lsb


def hamming_distance(string1, string2):
    distance = 0
    length = len(string1)
    for i in range(length):
        if string1[i] != string2[i]:
            distance += 1
    return distance

def count_tiles_size(width, height, tile_size):
    column = math.ceil(width / tile_size)
    row = math.ceil(height / tile_size)
    return column, row

def perform(original_image_path, changed_image_path):
    original_image = Image.open(original_image_path)
    changed_image = Image.open(changed_image_path)
    w, h = original_image.size
    tile_size = 64
    hash_length = 64
    threshold = hash_length * 0.15
    column, row = count_tiles_size(w, h, tile_size)

    # Slice image to 64x64 blocks
    original_tiles = image_slicer.slice(original_image_path, number_tiles = column*row, col=column, row=row, save=False)
    changed_tiles = image_slicer.slice(changed_image_path, number_tiles = column*row, col=column, row=row, save=False)

    # Итеративно проходим по каждому блоку изображения
    for original_tile, changed_tile in zip(original_tiles, changed_tiles):
        # Получаем хеш блока
        original_hash = imagehash.phash_simple(original_tile.image)
        changed_hash = imagehash.phash_simple(changed_tile.image)

        # Прям хеш методом наименее значащего бита
        original_tile.image = lsb.hide(original_tile.image, str(original_hash))
        changed_tile.image = lsb.hide(changed_tile.image, str(changed_hash))

        # Забираем хеш из изображения
        decoded_original_hash = lsb.reveal(original_tile.image.copy())
        decoded_changed_hash = lsb.reveal(changed_tile.image.copy())

        # Вычисляем расстояние Хемминга и сравниваем его с пороговой границей
        if hamming_distance(decoded_original_hash, decoded_changed_hash) > threshold:
            # Закрашиваем измененные области
            # The current version supports all possible conversions between “L”, “RGB” and “CMYK.” The matrix argument only supports “L” and “RGB”.
            rgb2xyz = (
                0.412453, 0.357580, 0.180423, 0,
                0.212671, 0.215160, 0.072169, 0,
                0.019334, 0.919193, 0.950227, 0)
            changed_tile.image = changed_tile.image.convert("RGB", rgb2xyz)

    result_image = image_slicer.join(changed_tiles, w, h)
    file_name = original_image_path.split(".")[-2]
    result_image_path = original_image_path.replace(file_name, file_name + "_result")
    result_image.save(result_image_path)

    original_image.show()
    changed_image.show()
    result_image.show()


if __name__ == '__main__':
    # original_image_path = "./images/original_wolf.jpg"
    # changed_image_path = "./images/changed_wolf.jpg"
    original_image_path = "./images/original_giraffe.jpg"
    changed_image_path = "./images/changed_giraffe.jpg"
    perform(original_image_path, changed_image_path)
