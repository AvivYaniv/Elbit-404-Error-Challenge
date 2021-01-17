import sys

# Constant Definition Section
# File Section
ELBIT_FILE_PATH                         = 'elbitsystems.elbit'
OUTPUT_IMAGE_PATH                       = 'elbit.asciiart'
# Image Section
IMAGE_HEIGHT                            = 200
IMAGE_WIDTH                             = 28

class ASCIIArtImage:
    def __init__(self, width, height, default_value=None):
        self.DEFAULT_VALUE              = default_value if default_value else '_'
        self.X_RANGE                    = width
        self.Y_RANGE                    = height
        self._image                     = [[self.DEFAULT_VALUE for _ in range(self.Y_RANGE)] for _ in range(self.X_RANGE)]
        self._x                         = 0
        self._y                         = 0
        self._values_count              = 0

    def set_x(self, x):
        self._x                         = x

    def set_y(self, y):
        self._y                         = y

    def set_value(self, value):
        self._values_count              += 1
        self._image[self._x][self._y]    = value

    def draw(self, output_file_path):
        with open(output_file_path, 'w') as f:
            for y in range(self.Y_RANGE):
                line = ''
                for x in range(self.X_RANGE):
                    line += self._image[x][y]
                f.write(f'{line}\n')

class ElbitFileReader:
    def __init__(self):
        # Constant Definition Section
        # Lambda Definition
        self.HEX_TO_BYTE        = lambda hex_str: bytes.fromhex(hex_str)
        self.DEC_TO_BYTE        = lambda dec_str: bytes.fromhex(hex(int(dec_str))[2:])
        # Eblit File Format Section
        self.COMMENT_START      = b'<'
        self.COMMENT_END        = b'>'
        self.COMMENT_LENGTH     = 3
        self.OPCODE_LENGTH      = 2
        self.COMMENT_CONTENT    = 1
        self.END_OF_FILE        = b''
        # Opcodes Section
        self.X_GOTO_OPCODE_NAME = 'GOTO x'
        self.Y_GOTO_OPCODE_NAME = 'GOTO y'
        self.GOTO_OPCODES       = \
            {
                self.HEX_TO_BYTE('3F'): self.X_GOTO_OPCODE_NAME,
                self.HEX_TO_BYTE('40'): self.Y_GOTO_OPCODE_NAME,
            }
        self.PRINT_OPCODE       = self.HEX_TO_BYTE('24')
        self.PRINT_TYPES        = \
            {
                self.HEX_TO_BYTE('00'): ' ',
                self.HEX_TO_BYTE('01'): ',',
                self.HEX_TO_BYTE('02'): '%',
                self.HEX_TO_BYTE('04'): ',',
                self.DEC_TO_BYTE('16'): '#',
                self.DEC_TO_BYTE('32'): '(',
                self.DEC_TO_BYTE('64'): '/',
                self.DEC_TO_BYTE('128'): '*'
            }

    def read(self, elbit_file_path, print_comments=True):
        ascii_art_image     = ASCIIArtImage(IMAGE_HEIGHT, IMAGE_WIDTH)
        try:
            with open(elbit_file_path, 'rb') as f:
                opcode, directive   = f.read(1), f.read(1)
                is_in_comment       = False
                current_comment     = b''
                # As long as not EOF
                while self.END_OF_FILE != opcode:
                    # If in comment
                    if is_in_comment:
                        # If comment not ended
                        if self.COMMENT_END != opcode:
                            # Add byte to comment
                            current_comment += opcode
                            # Read comment content
                            opcode           = f.read(self.COMMENT_CONTENT)
                        # Else, end of comment
                        else:
                            # If print comment flag is on
                            if print_comments:
                                # Print comment
                                print(current_comment.decode("utf-8"))
                            is_in_comment   = False
                            current_comment = b''
                            # Drain comment token identifier
                            f.read(self.COMMENT_LENGTH-self.COMMENT_CONTENT)
                            # Read opcode
                            opcode, directive  = f.read(1), f.read(1)
                    # Else, not in comment
                    else:
                        # If start of comment
                        if self.COMMENT_START == opcode:
                            current_comment = b''
                            is_in_comment   = True
                            # Drain rest of comment token identifier
                            f.read(self.COMMENT_LENGTH-self.OPCODE_LENGTH)
                            # Read comment content
                            opcode          = f.read(self.COMMENT_CONTENT)
                        # Else, opcode
                        else:
                            # If GOTO opcode
                            if      opcode in self.GOTO_OPCODES:
                                # Detect opcode axis and location
                                goto_opcode_name    = self.GOTO_OPCODES[opcode]
                                goto_location       = int.from_bytes(directive, byteorder=sys.byteorder)
                                # If        x-axis set x location
                                if self.X_GOTO_OPCODE_NAME == goto_opcode_name:
                                    ascii_art_image.set_x(goto_location)
                                # Else if,  y-axis set y location
                                elif self.Y_GOTO_OPCODE_NAME == goto_opcode_name:
                                    ascii_art_image.set_y(goto_location)
                            # Else if PRINT opcode
                            elif    opcode == self.PRINT_OPCODE:
                                # Set print value
                                if directive not in self.PRINT_TYPES:
                                    raise Exception(f'Unknown PRINT value {directive}')
                                print_value = self.PRINT_TYPES[directive]
                                ascii_art_image.set_value(print_value)
                            # Read next OPCODE
                            opcode, directive = f.read(1), f.read(1)
        except Exception as e:
            print(e)
        # Return result of Elbit file, an ASCII art image
        return ascii_art_image

if __name__ == "__main__":
    elbit_file_reader = ElbitFileReader()
    image_result      = elbit_file_reader.read(ELBIT_FILE_PATH)
    image_result.draw(OUTPUT_IMAGE_PATH)
