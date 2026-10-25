import hashlib
import json
import os
import re
from pathlib import Path

# Cấu hình đường dẫn
ME_FOLDER = Path(r"D:\Tool Clearme\ME REGION")
GITHUB_USER = "giangtt"  # Thay bằng username GitHub của bạn
GITHUB_REPO = "clean-me-repo"  # Thay bằng tên repository GitHub của bạn
BRANCH = "main"

BASE_RAW_URL = (
    f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/"
)


def get_sha256(file_path: Path) -> str:
  hasher = hashlib.sha256()
  with open(file_path, "rb") as f:
    while chunk := f.read(65536):
      hasher.update(chunk)
  return hasher.hexdigest()


def parse_me_info(filename: str, data: bytes) -> tuple[str, str]:
  """Trích xuất Version và SKU từ tên tệp hoặc quét cấu trúc $MN2"""
  # 1. Trích xuất qua định dạng tên chuẩn (vd: 16.1.42.2872_COR_LP.bin)
  ver_match = re.search(r"(\d{1,2}\.\d{1,2}\.\d{1,2}\.\d{3,4})", filename)
  version = ver_match.group(1) if ver_match else "Unknown"

  sku = "Unknown"
  fname_upper = filename.upper()
  if "COR_LP" in fname_upper or "CORPORATE LP" in fname_upper:
    sku = "Corporate LP"
  elif "COR_H" in fname_upper or "CORPORATE H" in fname_upper:
    sku = "Corporate H"
  elif "CON_LP" in fname_upper or "CONSUMER LP" in fname_upper:
    sku = "Consumer LP"
  elif "CON_H" in fname_upper or "CONSUMER H" in fname_upper:
    sku = "Consumer H"

  # 2. Quét phụ trợ từ header $MN2 nếu tên tệp không chứa version
  if version == "Unknown":
    idx = data.find(b"$MN2")
    if idx != -1 and idx + 16 <= len(data):
      import struct

      maj, min_v, hfx, bld = struct.unpack("<4H", data[idx + 8 : idx + 16])
      if 11 <= maj <= 20:
        version = f"{maj}.{min_v}.{hfx}.{bld}"

  return version, sku


def build_manifest():
  if not ME_FOLDER.exists():
    print(f"[-] Không tìm thấy thư mục: {ME_FOLDER}")
    return

  entries = []
  all_files = sorted(
      [f for f in ME_FOLDER.glob("*.bin") if f.is_file()],
      key=lambda x: x.name.lower(),
  )

  print(f"[+] Tìm thấy {len(all_files)} tệp ME Region...")

  for file_path in all_files:
    with open(file_path, "rb") as f:
      content = f.read()

    version, sku = parse_me_info(file_path.name, content)

    # Tách nhánh Major.Minor (vd: 16.1, 20.0, 15.0)
    major_minor = ".".join(version.split(".")[:2]) if "." in version else "N/A"

    entry = {
        "filename": file_path.name,
        "version": version,
        "branch": major_minor,
        "sku": sku,
        "size_bytes": file_path.stat().st_size,
        "sha256": get_sha256(file_path),
        "download_url": f"{BASE_RAW_URL}{file_path.name}",
    }
    entries.append(entry)

  manifest_data = {
      "total_count": len(entries),
      "updated_at": "2026-10-23",
      "firmwares": entries,
  }

  out_path = ME_FOLDER / "manifest.json"
  with open(out_path, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2, ensure_ascii=False)

  print(f"[✓] Đã tạo thành công manifest: {out_path}")


if __name__ == "__main__":
  build_manifest()