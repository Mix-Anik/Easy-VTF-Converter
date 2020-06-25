from os import listdir, walk
from os.path import isfile, join
from vtf_structs import VTF_File


def find_textures(dir_paths):
    texture_paths = []

    for path in dir_paths:
        for subdir, dirs, files in walk(path):
            texture_paths += [join(subdir, fname) for fname in listdir(subdir) if
                              (isfile(join(subdir, fname)) and fname[-4:] == ".vtf")]

    return texture_paths

def convert(texture_path, version):
    tex_file = open(texture_path, mode="r+b")
    bytelist = tex_file.read()
    tex_file.close()

    minor_version = int(version[-1])

    # Creating VTF-type object & converting to requested version
    vtf = VTF_File(bytelist)

    # Just in case, so it wouldn't stop processing other files
    try:
        vtf.convert(minor_version)
    except:
        print("Unexpected error")

    # Writing new file (replacing old one)
    tex_file = open(texture_path, 'wb')
    tex_file.write(vtf.compose())
    tex_file.close()