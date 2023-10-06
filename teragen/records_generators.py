from teragen.unsigned16 import Unsigned16

KEY_LEN = 10
VALUE_LEN = 90
RECORD_LEN = KEY_LEN + VALUE_LEN

ord_space = ord(' ')
ord_newline = ord('\n')
ord_cr = ord('\r')


def generate_record(rec_buf, rand: 'Unsigned16', record_number: 'Unsigned16') -> None:
    # Generate the 10-byte key using the high 10 bytes of the 128-bit random number
    for i in range(10):
        rec_buf[i] = rand.get_byte(i)

    # Add 2 bytes of "break"
    rec_buf[10] = 0x00
    rec_buf[11] = 0x11

    # Convert the 128-bit record number to 32 bits of ASCII hexadecimal
    # as the next 32 bytes of the record.
    for i in range(32):
        rec_buf[12 + i] = record_number.get_hex_digit(i)

        # Add 4 bytes of "break" data
    rec_buf[44] = 0x88
    rec_buf[45] = 0x99
    rec_buf[46] = 0xAA
    rec_buf[47] = 0xBB

    # Add 48 bytes of filler based on low 48 bits of random number
    for i in range(12):
        v = rand.get_hex_digit(20 + i)
        rec_buf[48 + i * 4] = v
        rec_buf[49 + i * 4] = v
        rec_buf[50 + i * 4] = v
        rec_buf[51 + i * 4] = v

    # Add 4 bytes of "break" data
    rec_buf[96] = 0xCC
    rec_buf[97] = 0xDD
    rec_buf[98] = 0xEE
    rec_buf[99] = 0xFF


def make_big_integer(value: int):
    return value if value >= 0 else (value + 2 ** 64)


def generate_ascii_record(rec_buf, rand: 'Unsigned16', record_number: 'Unsigned16') -> None:
    # Generate the 10-byte ascii key using mostly the high 64 bits.
    temp = make_big_integer(rand.get_high_8_bytes())
    for i in range(8):
        rec_buf[i] = temp % 95 + ord_space
        temp //= 95

    temp = make_big_integer(rand.get_low_8_bytes())
    rec_buf[8] = temp % 95 + ord_space
    temp //= 95
    rec_buf[9] = temp % 95 + ord_space

    # Add 2 bytes of "break" data
    rec_buf[10] = ord_space
    rec_buf[11] = ord_space

    # convert the 128-bit record number to 32 bits of ascii hexadecimal as the next 32 bytes of the record.
    for i in range(32):
        rec_buf[12 + i] = record_number.get_hex_digit(i)

    # Add 2 bytes of "break" data
    rec_buf[44] = ord_space
    rec_buf[45] = ord_space

    # Add 52 bytes of filler based on low 48 bits of random number
    for i in range(13):
        rec_buf[46 + i * 4] = rec_buf[47 + i * 4] = rec_buf[48 + i * 4] = rec_buf[49 + i * 4] = (
            rand.get_hex_digit(19 + i))

    # Add 2 bytes of "break" data
    rec_buf[98] = ord_cr
    rec_buf[99] = ord_newline
