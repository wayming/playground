def is_palin(s: str):
    l = [x for x in s if x.isalnum]
    return l[::-1]
