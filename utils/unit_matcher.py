def convert_cpu_unit(size):
    # Returns the milicores
    # If no units follow the number, assume it is a single core
    size = str(size)
    if size[-1].isdigit():
        return int(size) * 1000
    # If the unit is "m", assume it is milicores
    elif size[-1] == "m":
        return int(size[:-1])

def convert_memory_unit(size):
    size = str(size)

    if size[-2:] == "Ki":
        return int(size[:-2])
    elif size[-2:] == "Mi":
        return int(size[:-2]) * 1024
    elif size[-2:] == "Gi":
        return int(size[:-2]) * 1024 * 1024
    else:
        raise Exception("Invalid unit")