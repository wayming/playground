def flat_dict(d, prefix="") -> str:
    result = ""
    print(f"prefix={prefix}")
    if not prefix:
        result += "{"
    for k, v in d.items():
        nextPrefix = k if not prefix else prefix + "." + k
        if type(v) is not dict:
            result += "'" + nextPrefix + "' : " + str(v) + ", "
        else:
            result += flat_dict(v, nextPrefix)
    if not prefix:
        result += "}"

    return result
