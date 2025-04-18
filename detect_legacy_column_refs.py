import os

TARGET_STRING = "chexbot_reply_id"
PROJECT_DIR = "."  # You can change this to an absolute path

def scan_files(base_path, target):
    print(f"🔍 Scanning for '{target}' in {base_path}...\n")
    matches = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith((".py", ".html", ".txt", ".json", ".js")):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            if target in line:
                                matches.append((full_path, i, line.strip()))
                except Exception as e:
                    print(f"⚠️ Could not read {full_path}: {e}")

    if matches:
        print(f"🚨 Found {len(matches)} references to '{target}':\n")
        for path, line_num, content in matches:
            print(f"{path}:{line_num}: {content}")
    else:
        print("✅ No references found. You're clean!")

if __name__ == "__main__":
    scan_files(PROJECT_DIR, TARGET_STRING)
