from os import listdir, walk
from os.path import isfile, join


def find_textures(dir_paths):
    texture_paths = []

    for path in dir_paths:
        for subdir, _, _ in walk(path):
            for filename in listdir(subdir):
                abs_path = join(subdir, filename)
                if isfile(abs_path) and filename[-4:] == ".vtf":
                    texture_paths.append(abs_path)

    return texture_paths
