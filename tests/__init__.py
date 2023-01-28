def is_even(n):
    return n % 2 == 0


def is_positive(n):
    return n > 0


def first_item_positive(collection):
    return collection[0] > 0


def palindromic_int(n):
    return int(str(n)[::-1]) == n
