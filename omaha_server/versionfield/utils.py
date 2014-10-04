# coding: utf8


def convert_version_string_to_int(string, number_bits):
    """
    Take in a verison string e.g. '3.0.1'
    Store it as a converted int: 3*(2**number_bits[0])+0*(2**number_bits[1])+1*(2**number_bits[2])

    >>> convert_version_string_to_int('3.0.1',[8,8,16])
    50331649
    """
    numbers = [int(number_string) for number_string in string.split(".")]

    if len(numbers) > len(number_bits):
        raise NotImplementedError(
            "Versions with more than {0} decimal places are not supported".format(len(number_bits) - 1))

    # add 0s for missing numbers
    numbers.extend([0] * (len(number_bits) - len(numbers)))

    # convert to single int and return
    number = 0
    total_bits = 0
    for num, bits in reversed(zip(numbers, number_bits)):
        max_num = (bits + 1) - 1
        if num >= 1 << max_num:
            raise ValueError("Number {0} cannot be stored with only {1} bits. Max is {2}".format(num, bits, max_num))
        number += num << total_bits
        total_bits += bits

    return number


def convert_version_int_to_string(number, number_bits):
    """
    Take in a verison string e.g. '3.0.1'
    Store it as a converted int: 3*(2**number_bits[0])+0*(2**number_bits[1])+1*(2**number_bits[2])

    >>> convert_version_int_to_string(50331649,[8,8,16])
    '3.0.1'
    """
    number_strings = []
    total_bits = sum(number_bits)
    for bits in number_bits:
        shift_amount = (total_bits - bits)
        number_segment = number >> shift_amount
        number_strings.append(str(number_segment))
        total_bits = total_bits - bits
        number = number - (number_segment << shift_amount)

    return ".".join(number_strings)


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()