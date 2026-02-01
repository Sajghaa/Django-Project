import os

PROJECTS_ROOT = r"D:\Coding_Projects\100 Django Projects"
OUTPUT_README = os.path.join(PROJECTS_ROOT, "README.md")

IGNORE_FOLDERS = {".git", ".vscode", ".idea", "__pycache__"}
VENV_NAMES = {"venv", "ss_venv", "env"}

projects = []

for name in sorted(os.listdir(PROJECTS_ROOT)):
    path = os.path.join(PROJECTS_ROOT, name)

    if not os.path.isdir(path):
        continue
    if name in IGNORE_FOLDERS:
        continue

    description = "No description yet"
    status = "Planned"
    ready = "❌"

    # description.txt
    desc_path = os.path.join(path, "description.txt")
    if os.path.exists(desc_path):
        with open(desc_path, "r", encoding="utf-8") as f:
            description = f.read().strip()

    # manage.py detection
    if any(f.lower() == "manage.py" for f in os.listdir(path)):
        status = "Completed"

    # venv detection
    if any(os.path.isdir(os.path.join(path, v)) for v in VENV_NAMES):
        ready = "✅"

    projects.append((name, description, status, ready))

# overwrite README completely
with open(OUTPUT_README, "w", encoding="utf-8") as f:
    f.write("# 100 Django Projects Portfolio\n\n")
    f.write("> A curated collection of Django projects demonstrating Django mastery.\n\n")
    f.write("---\n\n")
    f.write("## 📌 Project Index\n\n")
    f.write("| # | Project Name | Description | Status | Ready to Run |\n")
    f.write("|---|--------------|-------------|--------|--------------|\n")

    for i, (name, desc, status, ready) in enumerate(projects, start=1):
        f.write(f"| {i} | [{name}]({name.replace(' ', '%20')}) | {desc} | {status} | {ready} |\n")

    f.write("\n---\n\n")
    f.write("## ⚙️ How to Run a Project\n\n")
    f.write("1. Navigate to the project folder.\n")
    f.write("2. Activate virtual environment (if present).\n")
    f.write("3. Install dependencies: `pip install -r requirements.txt`\n")
    f.write("4. Apply migrations: `python manage.py migrate`\n")
    f.write("5. Run server: `python manage.py runserver`\n\n")
    f.write("---\n\n")
    f.write("## 📌 Notes\n\n")
    f.write("- Projects are numbered to track progress.\n")
    f.write("- ✅ Ready to Run means a virtual environment exists.\n")
    f.write("- ❌ Not ready means you need to create one.\n\n")
    f.write("---\n\n")
    f.write("## ⚖️ License\n\n")
    f.write("MIT License.\n")

print("✅ Clean README.md generated successfully")
