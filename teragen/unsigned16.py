class Unsigned16:
    MAX_VALUE = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    def __init__(self, input_value: [int, str, 'Unsigned16'] = 0):
        if isinstance(input_value, int):
            self.value = input_value

        elif isinstance(input_value, str):
            self.set(input_value)

        elif isinstance(input_value, Unsigned16):
            self.value = input_value.value

        else:
            raise ValueError(f"Invalid value {input_value}")

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value & Unsigned16.MAX_VALUE

    def del_value(self):
        del self._value

    value = property(get_value, set_value, del_value, "Unsigned16 value")

    def set(self, s: str):
        self.value = int(s, 16)

    def __str__(self):
        return format(self.value, '032x')

    def set_long(self, long):
        self.value = long

    def get_byte(self, b: int) -> int:
        if 0 <= b < 16:
            return (self.value >> (120 - 8 * b)) & 0xFF
        raise ValueError(f"Invalid byte number {b}")

    # Avoid recomputing ord('0') and ord('A') every time
    ord0 = ord('0')
    ordA = ord('A')

    def get_hex_digit(self, p: int) -> int:
        digit = self.get_byte(p // 2)
        if p % 2 == 0:
            digit >>= 4
        digit &= 0xf
        if digit < 10:
            return self.ord0 + digit
        else:
            return self.ordA + digit - 10

    def multiply(self, b: 'Unsigned16') -> None:
        self.value *= b.value

    def add(self, b: 'Unsigned16') -> None:
        self.value += b.value

    def shift_left(self, bits: int) -> None:
        self.value <<= bits

    def get_high_8_bytes(self) -> int:
        return self.value >> 64

    def get_low_8_bytes(self) -> int:
        return self.value & 0xFFFFFFFFFFFFFFFF

# class Unsigned16:
#     def __init__(self, value=0):
#         if isinstance(value, int):
#             self.hi8 = np.int64(0)
#             self.lo8 = np.int64(value)
#         elif isinstance(value, str):
#             self.set(value)
#         else:
#             self.hi8 = value.hi8
#             self.lo8 = value.lo8
#
#     def set(self, s):
#         self.hi8 = np.int64(0)
#         self.lo8 = np.int64(0)
#         lastDigit = np.int64(0xF) << 60
#         for ch in s:
#             digit = self.get_hex_digit(ch)
#             if (lastDigit & self.hi8) != 0:
#                 raise ValueError(f"{s} overflowed 16 bytes")
#             self.hi8 <<= 4
#             self.hi8 |= rshift((self.lo8 & lastDigit), 60)
#             self.lo8 <<= 4
#             self.lo8 |= digit
#
#     def set_long(self, l):
#         self.lo8 = np.int64(l)
#         self.hi8 = np.int64(0)
#
#     def __str__(self):
#         if self.hi8 == 0:
#             return hex(self.lo8)
#         else:
#             result = hex(twos_complement(self.hi8)) + format(twos_complement(self.lo8), '016x')
#             return result
#
#     def __eq__(self, other):
#         if isinstance(other, Unsigned16):
#             return self.hi8 == other.hi8 and self.lo8 == other.lo8
#         else:
#             return False
#
#     def get_byte(self, b):
#         if 0 <= b < 16:
#             if b < 8:
#                 return (self.hi8 >> (56 - 8 * b)) & 0xFF
#             else:
#                 return (self.lo8 >> (120 - 8 * b)) & 0xFF
#         return 0
#
#     def get_hex_digit(self, ch):
#         if isinstance(ch, str):
#             digit = ord(ch)
#             if ord('0') <= digit <= ord('9'):
#                 return digit - ord('0')
#             if ord('a') <= digit <= ord('f'):
#                 return digit - ord('a') + 10
#             if ord('A') <= digit <= ord('F'):
#                 return digit - ord('A') + 10
#             raise ValueError(f"Invalid hex digit {ch}")
#         elif isinstance(ch, int):
#             p = ch
#             digit = self.get_byte(p // 2)
#             if p % 2 == 0:
#                 digit >>= 4
#             digit &= 0xf
#             if digit < 10:
#                 return chr(ord('0') + digit)
#             else:
#                 return chr(ord('A') + digit - 10)
#
#
#     def getHigh8(self):
#         return self.hi8
#
#     def getLow8(self):
#         return self.lo8
#
#     def multiply(self, b):
#         left = [0] * 4
#         left[0] = self.lo8 & 0xFFFFFFFF
#         left[1] = rshift(self.lo8, 32)
#         left[2] = self.hi8 & 0xFFFFFFFF
#         left[3] = rshift(self.hi8, 32)
#
#         right = [0] * 5
#         right[0] = b.lo8 & 0x7FFFFFFF
#         right[1] = rshift(b.lo8, 31) & 0x7FFFFFFF
#         right[2] = rshift(b.lo8, 62) + ((b.hi8 & 0x1FFFFFFF) << 2)
#         right[3] = rshift(b.hi8, 29) & 0x7FFFFFFF
#         right[4] = rshift(b.hi8, 60)
#
#         self.set_long(0)
#         tmp = Unsigned16()
#         for l in range(4):
#             for r in range(5):
#                 prod = left[l] * right[r]
#                 if prod != 0:
#                     off = l * 32 + r * 31
#                     tmp.set_long(prod)
#                     tmp.shift_left(off)
#                     self.add(tmp)
#
#     def add(self, b):
#         sumHi = self.hi8 + b.hi8
#         hibit0 = np.int64(self.lo8 < 0)
#         hibit1 = np.int64(b.lo8 < 0)
#         sumLo = self.lo8 + b.lo8
#         reshibit = np.int64(sumLo < 0)
#         if (hibit0 & hibit1) != 0 or ((hibit0 ^ hibit1) != 0 and reshibit == 0):
#             sumHi += 1  # add carry bit
#         self.hi8 = sumHi
#         self.lo8 = sumLo
#
#     def shift_left(self, bits):
#         if bits != 0:
#             if bits < 64:
#                 self.hi8 <<= bits
#                 self.hi8 |= (self.lo8 >> (64 - bits))
#                 self.lo8 <<= bits
#             elif bits < 128:
#                 self.hi8 = self.lo8 << (bits - 64)
#                 self.lo8 = 0
#             else:
#                 self.hi8 = 0
#                 self.lo8 = 0
