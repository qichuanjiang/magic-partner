from pathlib import Path


def deduplicate_file_names(file_names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    resolved: list[str] = []

    for original_name in file_names:
        stem = Path(original_name).stem
        suffix = Path(original_name).suffix
        key = original_name.lower()

        if key not in seen:
            seen[key] = 0
            resolved.append(original_name)
            continue

        seen[key] += 1
        resolved.append(f"{stem}({seen[key]}){suffix}")

    return resolved
