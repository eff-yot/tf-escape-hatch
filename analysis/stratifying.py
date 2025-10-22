import json

modules_file = "filtered_unverified_modules-v1.txt"
metadata_file = "stats_unverified_count.json"

with open(modules_file, "r") as f:
    module_names = [line.strip() for line in f if line.strip()]

with open(metadata_file, "r") as f:
    metadata = json.load(f)

high_downloads = []
medium_downloads = []
low_downloads = []

for module_name in module_names:
    if module_name in metadata:
        downloads = metadata[module_name]["downloads"]

        if downloads > 3935.52:
            high_downloads.append(module_name)
        elif downloads > 799.48:
            medium_downloads.append(module_name)
        else:
            low_downloads.append(module_name)

with open("unverified_high.txt", "w") as f:
    for module in high_downloads:
        f.write(module + "\n")

with open("unverified_medium.txt", "w") as f:
    for module in medium_downloads:
        f.write(module + "\n")

with open("unverified_low.txt", "w") as f:
    for module in low_downloads:
        f.write(module + "\n")


print(f"High: {len(high_downloads)}")
print(f"Medium: {len(medium_downloads)}")
print(f"Low: {len(low_downloads)}")
