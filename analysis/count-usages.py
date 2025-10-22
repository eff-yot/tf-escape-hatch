import os
import re
from pathlib import Path
from collections import defaultdict


PATTERNS = {
    "local-exec": re.compile(r'^\s*provisioner\s+"local-exec"\s*{', re.MULTILINE),
    "remote-exec": re.compile(r'^\s*provisioner\s+"remote-exec"\s*{', re.MULTILINE),
    "data-external": re.compile(r'^\s*data\s+"external"\s+"\w+"\s*{', re.MULTILINE)
}

EXCLUDED_DIRS = {'test', 'tests', 'example', 'examples'}
TERRAFORM_EXTENSION = '.tf'


def analyze_module(module_dir):
    occurrences = defaultdict(int)
    found = {key: False for key in PATTERNS.keys()}

    for root, _, files in os.walk(module_dir):
        for filename in files:
            if not filename.endswith(TERRAFORM_EXTENSION):
                continue

            file_path = Path(root) / filename
            relative_path = file_path.relative_to(module_dir)

            path_parts = [part.lower() for part in relative_path.parts[:-1]]
            if any(part in EXCLUDED_DIRS for part in path_parts):
                continue

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for key, pattern in PATTERNS.items():
                matches = pattern.findall(content)
                if matches:
                    occurrences[key] += len(matches)
                    found[key] = True

    return occurrences, found


modules_dir = Path("./unverified/all")
output_file = Path("filtered_unverified_modules-v1.txt")

total_occurrences = defaultdict(int)
modules_containing = {key: set() for key in PATTERNS.keys()}
scanned_count = 0

for item in modules_dir.iterdir():
    if not item.is_dir():
        continue

    scanned_count += 1
    occurrences, found = analyze_module(item)

    for key in PATTERNS.keys():
        total_occurrences[key] += occurrences[key]
        if found[key]:
            modules_containing[key].add(item.name)

all_found_modules = set().union(*modules_containing.values())

with open(output_file, 'w', encoding='utf-8') as f:
    for module_name in sorted(all_found_modules):
        f.write(f"{module_name}\n")

le_modules = modules_containing['local-exec']
re_modules = modules_containing['remote-exec']
de_modules = modules_containing['data-external']

all_three = le_modules & re_modules & de_modules
le_and_re_only = (le_modules & re_modules) - de_modules
le_and_de_only = (le_modules & de_modules) - re_modules
re_and_de_only = (re_modules & de_modules) - le_modules
le_only = le_modules - re_modules - de_modules
re_only = re_modules - le_modules - de_modules
de_only = de_modules - le_modules - re_modules

print(f"total modules scanned: {scanned_count}")
print(f"local-exec: {len(le_modules)}")
print(f"remote-exec: {len(re_modules)}")
print(f"data external: {len(de_modules)}")
print(f"local-exec: {total_occurrences['local-exec']}")
print(f"remote-exec: {total_occurrences['remote-exec']}")
print(f"data external: {total_occurrences['data-external']}")
print(f"using all three (local-exec, remote-exec, data-external): {len(all_three)}")
print(f"using exactly local-exec and remote-exec only: {len(le_and_re_only)}")
print(f"using exactly local-exec and data-external only: {len(le_and_de_only)}")
print(f"using exactly remote-exec and data-external only: {len(re_and_de_only)}")
print(f"using exactly local-exec only: {len(le_only)}")
print(f"using exactly remote-exec only: {len(re_only)}")
print(f"using exactly data-external only: {len(de_only)}")
print(f"total unique modules containing any target pattern: {len(all_found_modules)}")
