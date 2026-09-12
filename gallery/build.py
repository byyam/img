#!/usr/bin/env python3
"""
Prompt Gallery 构建脚本
扫描 gallery/items/ 下每个条目文件夹，生成 gallery/data.js 供页面读取。

条目文件夹约定：
  gallery/items/NN-名称/
    prompt.txt      第一行 = 标题，其余 = prompt 正文
    image.png/jpg   效果图（任意文件名，取第一个找到的图片文件）
    preview.jpg     （可选）手动指定的预览图；没有则自动为原图生成压缩预览

新增条目：新建文件夹 → 放入 prompt.txt + 图片 → 重新运行本脚本。
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录
ITEMS_DIR = os.path.join(ROOT, "gallery", "items")
OUT_FILE = os.path.join(ROOT, "gallery", "data.js")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
PREVIEW_MAX = 880           # 预览图最长边（页面卡片约 370px 宽，880px 已支持 2x 视网膜屏）
PREVIEW_SIZE_LIMIT = 300 * 1024  # 原图超过 300KB 或边长超过 PREVIEW_MAX 就生成预览


def make_preview(src, dst):
    """用 macOS 自带 sips 生成压缩预览图，失败返回 None。"""
    try:
        subprocess.run(
            ["sips", "-Z", str(PREVIEW_MAX), "-s", "format", "jpeg",
             "-s", "formatOptions", "75", src, "--out", dst],
            check=True, capture_output=True,
        )
        return dst
    except Exception as e:
        print(f"  [警告] 预览图生成失败: {e}", file=sys.stderr)
        return None


def file_size(path):
    return os.path.getsize(path)


def image_dimensions(path):
    try:
        out = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path],
            check=True, capture_output=True, text=True,
        ).stdout
        w = h = 0
        for line in out.splitlines():
            if "pixelWidth" in line:
                w = int(line.split()[-1])
            elif "pixelHeight" in line:
                h = int(line.split()[-1])
        return w, h
    except Exception:
        return 0, 0


def load_entry(dirpath, dirname):
    txt = os.path.join(dirpath, "prompt.txt")
    if not os.path.isfile(txt):
        print(f"  [跳过] {dirname}: 缺少 prompt.txt")
        return None

    with open(txt, encoding="utf-8") as f:
        content = f.read().strip()
    lines = content.splitlines()
    if not lines:
        print(f"  [跳过] {dirname}: prompt.txt 为空")
        return None
    title = lines[0].strip() or dirname
    prompt = "\n".join(lines[1:]).strip()
    if not prompt:
        print(f"  [跳过] {dirname}: 没有找到 prompt 正文")
        return None

    # 找图片：优先手动 preview.jpg，否则第一个非 _preview 图片
    files = sorted(f for f in os.listdir(dirpath)
                   if f.lower().endswith(IMAGE_EXTS) and not f.startswith("_"))
    if not files:
        print(f"  [跳过] {dirname}: 文件夹里没有图片")
        return None

    primary = files[0]
    primary_path = os.path.join(dirpath, primary)
    url_prefix = "gallery/items/" + dirname

    # 决定预览图
    preview_name = None
    if "preview.jpg" in files and primary != "preview.jpg":
        preview_name = "preview.jpg"
    else:
        w, h = image_dimensions(primary_path)
        if file_size(primary_path) > PREVIEW_SIZE_LIMIT or max(w, h) > PREVIEW_MAX:
            dst = os.path.join(dirpath, f"_preview_{os.path.splitext(primary)[0]}.jpg")
            if make_preview(primary_path, dst):
                preview_name = os.path.basename(dst)

    preview_url = url_prefix + "/" + preview_name if preview_name else url_prefix + "/" + primary
    full_url = url_prefix + "/" + primary

    return {
        "title": title,
        "img": preview_url,
        "full": full_url,
        "prompt": prompt,
    }


def main():
    if not os.path.isdir(ITEMS_DIR):
        print(f"未找到条目目录: {ITEMS_DIR}", file=sys.stderr)
        sys.exit(1)

    entries = []
    for dirname in sorted(os.listdir(ITEMS_DIR)):
        dirpath = os.path.join(ITEMS_DIR, dirname)
        if not os.path.isdir(dirpath) or dirname.startswith("."):
            continue
        entry = load_entry(dirpath, dirname)
        if entry:
            entries.append(entry)
            print(f"  [收录] {dirname} → {entry['title']}")

    payload = json.dumps(entries, ensure_ascii=False, indent=2)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("// 由 gallery/build.py 自动生成，请勿手改；新增条目请改文件夹后重新构建\n")
        f.write("window.GALLERY_ITEMS = " + payload + ";\n")

    print(f"\n共收录 {len(entries)} 个条目 → {os.path.relpath(OUT_FILE, ROOT)}")


if __name__ == "__main__":
    main()
