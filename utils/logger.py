import json
import os

def log_final_output(title: str, data: dict, filename: str = "final_output.json"):
    if os.getenv("GRUB_DEBUG") != "1":
        return

    log_data = {
        "title": title,
        "output": data
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    print(f"[DEBUG] Final JSON written to {filename}")
