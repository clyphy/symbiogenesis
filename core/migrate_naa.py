import os

root_dir = "."
replacements = {
    "symbiogenesis": "symbiogenesis",
    "symbiogenesis": "symbiogenesis",
    "NAA": "NAA",
    "naa": "naa",
}

updated_files = 0

for dirpath, _, filenames in os.walk(root_dir):
    if ".git" in dirpath:
        continue
    for f in filenames:
        if f.endswith((".py", ".sh", ".json", ".md", ".txt", ".bak")):
            filepath = os.path.join(dirpath, f)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
            except (UnicodeDecodeError, OSError):
                continue

            modified = False
            for old, new in replacements.items():
                if old in content:
                    content = content.replace(old, new)
                    modified = True

            if modified:
                with open(filepath, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"[Updated] {filepath}")
                updated_files += 1

print(f"\nMigration complete. Total files updated: {updated_files}")
