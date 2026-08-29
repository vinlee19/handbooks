#!/usr/bin/env python3
"""md2html.py -- 把 Markdown 深度分析手册转换为与站点同风格的静态 HTML。

用法: md2html.py <src_dir> <out_dir> <site_title> [icon]

- 每个 .md 转成同名 .html（index.md -> index.html）
- ```mermaid 代码块经 mermaid.js（CDN）渲染，深色主题
- 非 md 资源（png/svg/...）原样拷贝，保持相对路径引用可用
- 无 index.md 的目录自动生成章节目录页
"""
import html
import pathlib
import re
import shutil
import sys

import markdown

MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.S)
MD_LINK_RE = re.compile(r"\]\(([^)#\s]+\.md)(#[^)\s]*)?\)")
JUNK = (".git", "node_modules", ".mimosa", "__pycache__")

CSS = """
:root{--bg:#0a0e16;--panel:#0f1524;--panel2:#131b2e;--line:#22304a;--line2:#2c3d5c;
--tx:#dbe6f5;--tx2:#93a5c0;--tx3:#6b7d99;--ac:__ACCENT__}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--tx);
font:15px/1.8 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
a{color:var(--ac);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:960px;margin:0 auto;padding:0 28px}
.top{position:sticky;top:0;z-index:50;background:rgba(10,14,22,.93);backdrop-filter:blur(8px);
border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:14px;height:54px;flex-wrap:nowrap;overflow-x:auto}
.logo{font-weight:700;font-size:15px;white-space:nowrap;flex-shrink:0;color:var(--tx)}
.logo span{color:var(--ac)}
.nav{margin-left:auto;display:flex;gap:2px}
.nav a{font-size:12.5px;color:var(--tx2);padding:4px 8px;white-space:nowrap;border-radius:6px}
.nav a:hover{color:var(--tx);background:var(--panel2);text-decoration:none}
.nav a.on{color:var(--ac);background:color-mix(in srgb,var(--ac) 13%,transparent)}
main.wrap{padding:36px 28px 30px}
h1{font-size:30px;line-height:1.35;margin:8px 0 20px}
h2{font-size:22px;margin:40px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--line)}
h3{font-size:17.5px;margin:28px 0 10px}
p{margin:12px 0;color:#c7d3e6}
strong{color:#eaf2fd}
blockquote{margin:16px 0;padding:10px 18px;border-left:3px solid var(--ac);
background:var(--panel);border-radius:0 10px 10px 0;color:var(--tx2);font-size:14px}
blockquote p{margin:6px 0;color:var(--tx2)}
pre{background:#0b1220;border:1px solid var(--line);border-radius:10px;padding:14px 16px;
overflow-x:auto;font:12.5px/1.6 ui-monospace,Menlo,Consolas,monospace}
code{background:#0e1626;border:1px solid var(--line);border-radius:5px;padding:1px 6px;
font:12.5px ui-monospace,Menlo,monospace;color:#8fd3ff}
pre code{background:none;border:none;padding:0;color:inherit}
table{border-collapse:collapse;margin:18px 0;width:100%;font-size:13.5px}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left;color:#c7d3e6}
th{background:var(--panel2);color:var(--tx);font-weight:600}
tr:nth-child(2n) td{background:rgba(255,255,255,.02)}
ul,ol{color:#c7d3e6;padding-left:24px}
li{margin:6px 0}
img{max-width:100%%;border-radius:10px;border:1px solid var(--line);background:#fff}
.mermaid{margin:22px 0;padding:18px;background:var(--panel);border:1px solid var(--line);
border-radius:14px;overflow-x:auto;text-align:center}
.mermaid svg{max-width:100%%;height:auto}
.toc-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;margin:24px 0}
.toc-grid a{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;
padding:16px 18px;color:var(--tx2);font-size:14px}
.toc-grid a:hover{border-color:var(--ac);text-decoration:none}
.toc-grid a b{display:block;color:var(--tx);font-size:15px;margin-bottom:4px}
.foot{border-top:1px solid var(--line);color:var(--tx3);font-size:12.5px;padding:20px 0 44px}
hr{border:none;border-top:1px solid var(--line);margin:32px 0}
"""


def stash_mermaid(md_text):
    blocks = []

    def _stash(m):
        blocks.append(m.group(1).rstrip())
        return f"\n\nMERMAIDPLACEHOLDER{len(blocks) - 1}\n\n"

    return MERMAID_RE.sub(_stash, md_text), blocks


def restore_mermaid(body, blocks):
    def _restore(m):
        i = int(m.group(1))
        return f'<div class="mermaid">\n{html.escape(blocks[i])}\n</div>'

    body = re.sub(r"<p>MERMAIDPLACEHOLDER(\d+)</p>", _restore, body)
    body = re.sub(r"MERMAIDPLACEHOLDER(\d+)", _restore, body)
    return body


def rewrite_md_links(md_text):
    return MD_LINK_RE.sub(lambda m: f"]({m.group(1)[:-3]}.html{m.group(2) or ''})", md_text)


def first_heading(md_text):
    m = re.search(r"^#\s+(.+)$", md_text, re.M)
    if m:
        return m.group(1).strip()
    for line in md_text.splitlines():
        line = line.strip()
        if line:
            return line.lstrip("# ").strip()
    return "未命名"


def page_md_files(src_dir):
    files = sorted(
        p for p in src_dir.glob("*.md")
        if p.name != "index.md" and p.name != "README.md"
    )
    return files


def build_nav(src_dir, current_html):
    items = []
    if (src_dir / "index.md").exists():
        items.append(("index.html", "总览"))
    for p in page_md_files(src_dir):
        title = first_heading(p.read_text(encoding="utf-8"))
        title = re.sub(r"^\d+\s*[·.]\s*", "", title)
        items.append((p.with_suffix(".html").name, title))
    links = "".join(
        f'<a href="{html.escape(href, quote=True)}"{" class=on" if href == current_html else ""}>{html.escape(t)}</a>'
        for href, t in items
    )
    return f'<nav class="nav">{links}</nav>'


def wrap_page(title, site_title, icon, nav, body, accent):
    css = CSS.replace("__ACCENT__", accent)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} · {html.escape(site_title)}</title>
<style>{css}</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>mermaid.initialize({{startOnLoad:true,theme:'dark',flowchart:{{curve:'basis'}}}});</script>
</head>
<body>
<header class="top"><div class="wrap"><span class="logo">{icon} <span>{html.escape(site_title)}</span></span>{nav}</div></header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">Markdown 自动生成 · <a href="index.html">返回目录</a></div></footer>
</body>
</html>
"""


def convert_md_file(md_path, src_dir, site_title, icon, accent):
    text = md_path.read_text(encoding="utf-8")
    stashed, blocks = stash_mermaid(text)
    stashed = rewrite_md_links(stashed)
    exts = ["tables", "fenced_code"]
    try:
        import pygments  # noqa: F401
        exts.append("codehilite")
        body = markdown.markdown(stashed, extensions=exts,
                                 extension_configs={"codehilite": {"noclasses": True, "pygments_style": "monokai"}})
    except ImportError:
        body = markdown.markdown(stashed, extensions=exts)
    body = restore_mermaid(body, blocks)
    title = first_heading(text)
    nav = build_nav(src_dir, md_path.with_suffix(".html").name)
    return wrap_page(title, site_title, icon, nav, body, accent), title


def make_index_page(src_dir, site_title, icon, accent):
    rows = []
    for p in page_md_files(src_dir):
        title = first_heading(p.read_text(encoding="utf-8"))
        href = p.with_suffix(".html").name
        rows.append(f'<a href="{html.escape(href, quote=True)}"><b>{html.escape(title)}</b>{html.escape(p.stem)}</a>')
    body = f'<h1>{html.escape(site_title)}</h1>\n<div class="toc-grid">{"".join(rows)}</div>'
    nav = build_nav(src_dir, "index.html")
    return wrap_page("目录", site_title, icon, nav, body, accent)


def copy_assets(src_dir, out_dir):
    for p in src_dir.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(src_dir)
        if any(part in JUNK or "visual-check" in part for part in rel.parts):
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".json", ".css", ".js"}:
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    src_dir, out_dir, site_title = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
    icon = sys.argv[4] if len(sys.argv) > 4 else "📘"
    accent = sys.argv[5] if len(sys.argv) > 5 else "#38bdf8"
    if not src_dir.is_dir():
        sys.exit(f"!! 源目录不存在: {src_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    mds = page_md_files(src_dir)
    has_index = (src_dir / "index.md").exists()
    for p in mds:
        page, _ = convert_md_file(p, src_dir, site_title, icon, accent)
        (out_dir / p.with_suffix(".html").name).write_text(page, encoding="utf-8")
    if has_index:
        page, _ = convert_md_file(src_dir / "index.md", src_dir, site_title, icon, accent)
        (out_dir / "index.html").write_text(page, encoding="utf-8")
    else:
        (out_dir / "index.html").write_text(make_index_page(src_dir, site_title, icon, accent), encoding="utf-8")
    copy_assets(src_dir, out_dir)
    print(f"   md2html: {len(mds) + (1 if has_index else 0)} 页（含目录） -> {out_dir}")


if __name__ == "__main__":
    main()
