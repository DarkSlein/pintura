def increment_version(version):
    parts = list(map(int, version.split('.')))
    parts[2] += 1  # Increment patch version
    if parts[2] >= 10:
        parts[2] = 0
        parts[1] += 1
        if parts[1] >= 10:
            parts[1] = 0
            parts[0] += 1
    return '.'.join(map(str, parts))

with open('version.txt', 'r') as f:
    current_version = f.read().strip()

new_version = increment_version(current_version)

with open('version.txt', 'w') as f:
    f.write(new_version)

print(new_version)