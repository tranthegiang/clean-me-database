import json
import urllib.parse
from pathlib import Path

# Thư mục gốc chứa các folder CSME
REPO_DIR = Path(__file__).resolve().parent

# Thông tin chính xác từ GitHub của bạn
GITHUB_USER = "tranthegiang"
REPO_NAME = "clean-me-database"
BRANCH = "main"

manifest = {}
total_files = 0

print("Đang quét toàn bộ các file Clean ME...")

# Quét tất cả các file .bin nằm trong các thư mục CSME
for bin_file in REPO_DIR.rglob("*.bin"):
    # Bỏ qua nếu file nằm trong thư mục ẩn của Git (.git)
    if ".git" in bin_file.parts:
        continue

    # Lấy đường dẫn tương đối (Ví dụ: CSME 14.0 Repository r14/14.0.31...bin)
    rel_path = bin_file.relative_to(REPO_DIR).as_posix()

    # Mã hóa các khoảng trắng trong tên thư mục thành %20 để URL không bị lỗi khi tải về
    encoded_rel_path = urllib.parse.quote(rel_path)

    # Link Raw trực tiếp của GitHub
    raw_url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{encoded_rel_path}"

    # Đưa vào danh bạ manifest (Key là tên file để tool tìm kiếm tức thì)
    manifest[bin_file.name] = raw_url
    total_files += 1

# Xuất dữ liệu ra manifest.json
manifest_path = REPO_DIR / "manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(
    f"-> Thành công! Đã tạo xong manifest.json cho {total_files} file Clean ME."
)