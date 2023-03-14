def convert_cpu_unit(size):
    # Returns the milicores
    # If no units follow the number, assume it is a single core
    size = str(size)
    if size[-1].isdigit():
        return round(float(size) * 1000, 3)
    # If the unit is "m", assume it is milicores
    elif size[-1] == "m":
        return round(float(size[:-1]), 3)
    elif size[-1] == "n":
        return round(float(size[:-1]) / 1000 / 1000, 3)

def convert_memory_unit(size):
    size = str(size)

    if size[-2:] == "Ki":
        return round(float(size[:-2]), 3)
    elif size[-2:] == "Mi":
        return round(float(size[:-2]) * 1024, 3)
    elif size[-2:] == "Gi":
        return round(float(size[:-2]) * 1024 * 1024, 3)
    else:
        raise Exception("Invalid unit")