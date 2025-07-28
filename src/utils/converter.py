def converte(value):
    try:
        if value is None:
            return 0.0
        value = value.strip()
        if value == "":
            return 0.0
        return float(value)
    except:
        return 0.0