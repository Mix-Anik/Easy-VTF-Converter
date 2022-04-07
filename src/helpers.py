from os import walk
from os.path import join


def find_textures(dir_paths, subfolders=True):
    texture_paths = []

    for path in dir_paths:
        for subdir, _, filenames in walk(path):
            for filename in filenames:
                abs_path = join(subdir, filename)

                if filename[-4:] == ".vtf":
                    texture_paths.append(abs_path)

            if not subfolders:
                break

    return texture_paths
