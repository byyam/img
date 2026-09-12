# img · Prompt Gallery

图片 Prompt 效果预览画廊 —— 打开页面即可浏览每条 Prompt 的生成效果，**点击图片或「复制 Prompt」按钮即复制对应 Prompt**。

## 使用

1. 打开 `index.html`，浏览画廊。
2. 点击任意图片 → 该条 Prompt 复制到剪贴板（带提示反馈）。
3. 点图片右上角放大镜可查看大图；「展开全文」查看完整 Prompt；顶部搜索框可按标题/关键词过滤。

## 添加新条目（无需改代码）

1. 在 `gallery/items/` 下新建一个文件夹，建议带序号前缀控制排序，如 `03-我的新海报/`。
2. 文件夹里放两个东西：
   - `prompt.txt`：**第一行是标题**，其余内容是完整 prompt
   - 任意文件名的效果图（png/jpg/webp）
3. 双击仓库根目录的 **`双击重建数据.command`**，完成。

构建脚本（`gallery/build.py`）会自动扫描所有条目文件夹生成 `gallery/data.js`；如果原图超过 800KB 或边长超过 1200px，还会自动用 macOS 自带的 `sips` 生成压缩预览图（`_preview_*.jpg`），页面秒开。也可以在文件夹里手动放一张 `preview.jpg` 覆盖自动预览。

> 手动重建的命令行方式：`python3 gallery/build.py`

## 目录结构

```
img/
├── index.html              画廊页面（无需修改）
├── 双击重建数据.command     添加条目后双击运行
└── gallery/
    ├── build.py            构建脚本
    ├── data.js             自动生成的数据（勿手改）
    └── items/
        ├── 01-韩式插画艺术海报（上下分割）/
        │   ├── prompt.txt
        │   ├── image.png
        │   └── _preview_image.jpg   （自动生成的预览图）
        └── 02-韩式插画艺术海报（精简版）/
            └── ...
```

## License

MIT
