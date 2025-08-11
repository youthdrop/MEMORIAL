import os

# This is the folder Flask uses for static files
static_folder = os.path.join("frontend", "dist")

print("Static folder path:", os.path.abspath(static_folder))

index_path = os.path.join(static_folder, "index.html")
print("Index.html exists:", os.path.exists(index_path))

assets_path = os.path.join(static_folder, "assets")
print("Assets folder exists:", os.path.exists(assets_path))

if os.path.exists(assets_path):
    print("Assets contents:", os.listdir(assets_path)[:5])  # show first 5 files
