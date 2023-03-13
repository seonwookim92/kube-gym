def convert_cpu_unit(size):
    # Returns the milicores
    # If no units follow the number, assume it is a single core
    size = str(size)
    if size[-1].isdigit():
        return float(size) * 1000
    # If the unit is "m", assume it is milicores
    elif size[-1] == "m":
        return float(size[:-1])
    elif size[-1] == "n":
        return float(size[:-1]) / 1000

def convert_memory_unit(size):
    size = str(size)

    if size[-2:] == "Ki":
        return float(size[:-2])
    elif size[-2:] == "Mi":
        return float(size[:-2]) * 1024
    elif size[-2:] == "Gi":
        return float(size[:-2]) * 1024 * 1024
    else:
        raise Exception("Invalid unit")