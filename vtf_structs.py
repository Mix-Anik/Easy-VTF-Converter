from struct import pack

from c_structs import CUint32, CUShort, CFloat, CUChar


# For full reference see https://developer.valvesoftware.com/wiki/Valve_Texture_Format
NA = 0
# Image data format table ([R,G,B,A], Total bits)
FORMATS = {
    4294967295: None,
    0: ([8, 8, 8, 8], 32),
    1: ([8, 8, 8, 8], 32),
    2: ([8, 8, 8, 0], 24),
    3: ([8, 8, 8, 0], 24),
    4: ([5, 6, 5, 0], 16),
    5: ([NA, NA, NA, NA], 8),
    6: ([NA, NA, NA, 8], 16),
    7: ([NA, NA, NA, NA], 8),
    8: ([0, 0, 0, 8], 8),
    9: ([8, 8, 8, 0], 24),
    10: ([8, 8, 8, 0], 24),
    11: ([8, 8, 8, 8], 32),
    12: ([8, 8, 8, 8], 32),
    13: ([NA, NA, NA, 0], 4),
    14: ([NA, NA, NA, 4], 8),
    15: ([NA, NA, NA, 8], 8),
    16: ([8, 8, 8, 8], 32),
    17: ([5, 6, 5, 0], 16),
    18: ([5, 5, 5, 1], 16),
    19: ([4, 4, 4, 4], 16),
    20: ([NA, NA, NA, 1], 4),
    21: ([5, 5, 5, 1], 16),
    22: ([NA, NA, NA, NA], 16),
    23: ([NA, NA, NA, NA], 32),
    24: ([16, 16, 16, 16], 64),
    25: ([16, 16, 16, 16], 64),
    26: ([NA, NA, NA, NA], 32)
}


class VTFHeader:
    def __init__(self, bin_data):
        self.type_string = bin_data[:4]                         # 4 bytes   | char x4  | "Magic number" identifier
        self.version_major = CUint32(bin_data[4:8])            # 4 bytes   | uint32   | Major vtf version number
        self.version_minor = CUint32(bin_data[8:12])           # 4 bytes   | uint32   | Minor vtf version number
        self.header_size = CUint32(bin_data[12:16])            # 4 bytes   | uint32   | Size of the header struct (16 bytes aligned)
        self.l_width = CUShort(bin_data[16:18])                # 2 bytes   | ushort16 | Width of the largest image
        self.l_height = CUShort(bin_data[18:20])               # 2 bytes   | ushort16 | Height of the largest image
        self.flags = CUint32(bin_data[20:24])                  # 4 bytes   | uint32   | Flags for the image
        self.frames = CUShort(bin_data[24:26])                 # 2 bytes   | ushort16 | Number of frames if animated (1 if no animation)
        self.start_frame = CUShort(bin_data[26:28])            # 2 bytes   | ushort16 | Start frame (always 0)
        self.padding0 = b'\x00'*4                               # 4 bytes   | uchar x4 | Reflectivity padding (16 byte alignment)
        self.reflectivity = [CFloat(bin_data[32:36]),
                             CFloat(bin_data[36:40]),
                             CFloat(bin_data[40:44])]          # 12 bytes  | float x3 | Reflectivity vector
        self.padding1 = b'\x00'*4                               # 4 bytes   | uchar x4 | Reflectivity padding (8 byte packing)
        self.bumpmap_scale = CFloat(bin_data[48:52])           # 4 bytes   | float x1 | Bump map scale
        self.image_format = CUint32(bin_data[52:56])           # 4 bytes   | uint32   | Image format index
        self.mip_count = CUChar(bin_data[56:57])               # 1 bytes   | uchar    | Number of MIP levels (including the largest image)
        self.low_res_image_format = CUint32(bin_data[57:61])   # 4 bytes   | uint32   | Image format of the thumbnail image
        self.low_res_image_width = CUChar(bin_data[61:62])     # 1 bytes   | uchar    | Thumbnail image width
        self.low_res_image_height = CUChar(bin_data[62:63])    # 1 bytes   | uchar    | Thumbnail image height

        if self.version_minor.value > 1:
            self.depth = CUShort(bin_data[63:65])              # 2 bytes   | ushort16 | Depth of the largest mipmap in pixels

        if self.version_minor.value > 2:
            self.padding2 = b'\x00'*3                           # 3 bytes   | uchar x3 | Num resource padding
            self.num_resource = CUint32(bin_data[68:72])       # 4 bytes   | uint32   | Number of resources this vtf has
            self.padding3 = b'\x00'*8                           # 8 bytes   | uchar x8 | Num resource padding
            self.resources = []

            for i in range(self.num_resource.value):
                resource_data = bin_data[80 + 8*i : 80 + 8*(i+1)]
                resource = VTFResource(resource_data)

                # We can basically ignore other resource types, leaving low-res and high-res ones
                if resource.tag in [b'\x01\x00\x00', b'\x30\x00\x00']:
                    self.resources.append(resource)

    def compose(self):
        composed_header = self.type_string + self.version_major.raw() + self.version_minor.raw() + \
                        self.header_size.raw() + self.l_width.raw() + self.l_height.raw() + \
                        self.flags.raw() + self.frames.raw() + self.start_frame.raw() + \
                        self.padding0 + b''.join([x.raw() for x in self.reflectivity]) + \
                        self.padding1 + self.bumpmap_scale.raw() + self.image_format.raw() + \
                        self.mip_count.raw() + self.low_res_image_format.raw() + \
                        self.low_res_image_width.raw() + self.low_res_image_height.raw()

        if self.version_minor.value > 1:
            composed_header += self.depth.raw()

        if self.version_minor.value > 2:
            composed_header += self.padding2 + self.num_resource.raw() + self.padding3

            for res in self.resources:
                composed_header += res.compose()

        # Filling unused bytes
        composed_header += b'\x00' * (self.header_size.value - len(composed_header))

        return composed_header


class VTFResource:
    def __init__(self, res_bin_data):
        self.tag = res_bin_data[:3]                       # 3 bytes   | uchar x3 | A three-byte "tag" that identifies what this resource is
        self.flags = CUChar(res_bin_data[3:4])           # 1 byte    | uchar    | Resource entry flags
        self.offset = CUint32(res_bin_data[4:8])         # 4 bytes   | uint32   | The offset of this resource's data in the file

    def description(self):
        print("Tag: %s" % self.tag)
        print("Flags integer: %s" % self.flags.value)
        print("Offset: %s" % self.offset.value)

    def compose(self):
        return self.tag + self.flags.raw() + self.offset.raw()


class VTFFile:
    def __init__(self, bin_data):
        self.header = VTFHeader(bin_data)  # VTF Header

        # Image resource data
        # Doesn't really matter whether we divide low- and high-res image data for 7.3+ format or not
        # Unless we change the size of image data or offsets in header resource data
        self.image_data = bin_data[self.header.header_size.value:]
        # High resolution image data fromat [mipmap[frame[face[slice[RGBA]]]]]

    def convert(self, version):
        """
        Conversion:
        1. Change vtf minor version
        2. Change vtf header size according to new minor version
        3.1 Add 'Depth' value to the header (7.2+)
            3.1.1 Find it if converting from <7.2
        3.2 Add 'Resource number' value to the header (7.3+)
            3.2.1 Find it if converting from <7.3
        3.3 Add 'Resources' data to the header (7.3+)
            3.3.1 Find it if converting from <7.3
        4 Add Image/Resource data after header
        """

        # TODO 3.1.1: Find actual depth of largest mipmap
        # But 99% of chance it's '1'

        # TODO 3.2.1: Find actual number of resources? (mby not neccessary)
        # Usually we can assume it's 2, ignoring all resources except low/high-res data

        # TODO 3.3.1: Find actual resource flags, instead of nullifying them

        if not 0 <= version <= 5:
            print("Only versions 7.0-7.5 are supported")
            return

        # Changing minor version
        self.header.version_minor.set(version)

        # Changing header size
        if version < 2:
            self.header.header_size.set(64)
        elif version == 2:
            self.header.header_size.set(80)
        elif version > 2:
            self.header.header_size.set(96)

        # Adding 'depth' data
        if version >= 2:
            if 'depth' not in self.header.__dict__:
                self.header.depth = CUShort(b'\x01\x00')

        # Adding resources data
        if version > 2:
            if 'num_resource' not in self.header.__dict__:
                # Finding high-res data offset
                low_res_format_desc = FORMATS[self.header.low_res_image_format.value]

                self.header.padding2 = b'\x00'*3
                self.header.num_resource = CUint32(b'\x02\x00\x00\x00')
                self.header.padding3 = b'\x00'*8
                self.header.resources = []

                # Check if thumbnail exists
                if low_res_format_desc:
                    # Low-res resource data (tag + flags + offset)
                    low_res_resource = VTFResource(b'\x01\x00\x00' + b'\x00' + self.header.header_size.raw())
                    self.header.resources.append(low_res_resource)

                    high_res_offset_n = self.header.low_res_image_width.value * low_res_format_desc[1] + \
                                        self.header.low_res_image_height.value * low_res_format_desc[1] + \
                                        self.header.header_size.value
                    high_res_offset_b = pack("<I", high_res_offset_n)
                else:
                    high_res_offset_b = self.header.header_size.raw()

                # High-res resource data (tag + flags + offset)
                high_res_resource = VTFResource(b'\x30\x00\x00' + b'\x00' + high_res_offset_b)
                self.header.resources.append(high_res_resource)

    def description(self):
        print("Signature: %s" % self.header.type_string)
        print("VTF version: %s.%s" % (self.header.version_major.value, self.header.version_minor.value))
        print("Header size: %s bytes" % self.header.header_size.value)
        print("Largest image dimensions: %sx%s px" % (self.header.l_width.value, self.header.l_height.value))
        print("Flags integer: %s" % self.header.flags.value)
        print("Frames amount: %s" % self.header.frames.value)
        print("Starting frame: %s" % self.header.start_frame.value)
        print("Ref start padding: %s" % self.header.padding0)
        print("Reflectivity vector: (%s,%s,%s)" % (self.header.reflectivity[0].value,
                                                   self.header.reflectivity[1].value,
                                                   self.header.reflectivity[2].value))
        print("Ref end padding: %s" % self.header.padding1)
        print("Bumpmap scale: %s" % self.header.bumpmap_scale.value)
        print("Image format: %s" % self.header.image_format.value)
        print("Mipmap count: %s" % self.header.mip_count.value)
        print("Thumbnail format: %s" % self.header.low_res_image_format.value)
        print("Thumbnail dimensions: %sx%s px" % (self.header.low_res_image_width.value,
                                                   self.header.low_res_image_height.value))

        if self.header.version_minor.value > 1:
            print("Depth: %s" % self.header.depth.value)
        if self.header.version_minor.value > 2:
            print("Resource num start padding: %s" % self.header.padding2)
            print("Resource amount: %s" % self.header.num_resource.value)
            print("Resource num end padding: %s" % self.header.padding3)

            print("Resources contained:")
            for i, res in enumerate(self.header.resources):
                print("%s." % (i+1))
                res.description()

        print("Image data: %s bytes" % len(self.image_data))

    def compose(self):
        return self.header.compose() + self.image_data
