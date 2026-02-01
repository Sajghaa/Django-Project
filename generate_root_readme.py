import os

# ===== CONFIG =====
PROJECTS_ROOT = r"D:\Coding_Projects\100 Django Projects"
OUTPUT_README = os.path.join(PROJECTS_ROOT, "README.md")
DESCRIPTION_FILENAME = "description.txt"
<<<<<<< HEAD
VENV_NAMES = ["ss_venv", "env"]
=======
VENV_NAMES = ["ss_venv", "venv","env"]
>>>>>>> c6f130b20 (Add root README and generate_root_readme.py script)
IGNORE_FOLDERS = {".git", ".vscode", ".idea", "__pycache__"}
# ==================

projects = []

for folder in sorted(os.listdir(PROJECTS_ROOT)):
    folder_path = os.path.join(PROJECTS_ROOT, folder)
    if not os.path.isdir(folder_path):
        continue
    if folder in IGNORE_FOLDERS:
        continue  # skip system folders

    # Default description
    description = "No description yet"
    status = "Planned"
    ready_to_run = False

    # Read description.txt if exists
    desc_file = os.path.join(folder_path, DESCRIPTION_FILENAME)
    if os.path.exists(desc_file):
        with open(desc_file, "r", encoding="utf-8") as f:
            description = f.read().strip().replace("\n", " ")

    # Detect manage.py for Completed
    manage_py = os.path.join(folder_path, "manage.py")
    if not os.path.exists(manage_py):
        # Try case-insensitive search
        for f in os.listdir(folder_path):
            if f.lower() == "manage.py":
                manage_py = os.path.join(folder_path, f)
                break

    if os.path.exists(manage_py):
        status = "Completed"

    # Detect virtual env
    for venv_name in VENV_NAMES:
        if os.path.exists(os.path.join(folder_path, venv_name)):
            ready_to_run = True
            break

    projects.append((folder, description, status, ready_to_run))

# Generate README content
lines = []
lines.append("# 100 Django Projects Portfolio\n")
lines.append("> A curated collection of Django projects demonstrating Django mastery.\n")
lines.append("---\n")
lines.append("## 📌 Project Index\n")
lines.append("| # | Project Name | Description | Status | Ready to Run |\n")
lines.append("|---|--------------|-------------|--------|--------------|\n")

for i, (name, desc, status, ready) in enumerate(projects, start=1):
    folder_link = name.replace(" ", "%20")
    ready_text = "✅" if ready else "❌"
    lines.append(f"| {i} | [{name}]({folder_link}) | {desc} | {status} | {ready_text} |")

lines.append("\n---\n")
lines.append("## ⚙️ How to Run a Project\n")
lines.append("1. Navigate to the project folder.\n")
lines.append("2. Activate virtual environment (if present).\n")
lines.append("3. Install dependencies: `pip install -r requirements.txt`\n")
lines.append("4. Apply migrations: `python manage.py makemigrations && python manage.py migrate`\n")
lines.append("5. Run server: `python manage.py runserver`\n")
lines.append("6. Open browser: `http://127.0.0.1:8000/`\n")
lines.append("\n---\n")
lines.append("## 📌 Notes\n")
lines.append("- Projects are numbered to track progress.\n")
lines.append("- ✅ Ready to Run indicates a virtual environment exists.\n")
lines.append("- ❌ Not ready to run means you need to create a venv first.\n")
lines.append("\n---\n")
lines.append("## ⚖️ License\n")
lines.append("MIT License. See [LICENSE](LICENSE) for details.\n")

# Write README
with open(OUTPUT_README, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"🔥 Root README.md regenerated at: {OUTPUT_README}")
print(f"✅ {len(projects)} projects included (hidden/system folders ignored)")
