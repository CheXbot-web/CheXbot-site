def load_keys(filepath="x_keys.txt"):
    keys = {}
    with open(filepath, "r") as f:
        for line in f:
            if "=" in line:
                key, val = line.strip().split("= ", 1)
                keys[key] = val
    return keys
