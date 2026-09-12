#!/bin/bash
# 双击运行：重新扫描 gallery/items/ 并生成页面数据
cd "$(dirname "$0")"
python3 gallery/build.py
echo ""
read -p "完成，按回车关闭…"
