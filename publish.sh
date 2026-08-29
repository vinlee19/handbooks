#!/usr/bin/env bash
# publish.sh -- 源码学习手册集的唯一发布方法
#
# 用法:
#   ./publish.sh            同步所有手册 + 重新生成根导航页 + 提交并推送
#   ./publish.sh --no-push  只同步和生成，不推送
#
# 新增一个手册的完整步骤:
#   1. 在 manifest.conf 里加一行（name|图标|标题|描述|主题色|源目录绝对路径）
#   2. 运行 ./publish.sh
#   3. 完成，GitHub Pages 自动重新部署
#
set -euo pipefail
cd "$(dirname "$0")"

NO_PUSH=0
[ "${1:-}" = "--no-push" ] && NO_PUSH=1

# ---------- 1. 同步各手册目录 ----------
CARDS=""
TOTAL_PAGES=0
TOTAL_BOOKS=0

while IFS='|' read -r -u 3 name icon title desc accent src; do
  # 跳过注释行与空行；name 只允许小写字母/数字/连字符，防止误删目录
  case "$name" in ''|\#*) continue ;; esac
  case "$name" in
    *[!a-z0-9_-]*|'') echo "!! 跳过非法 name: '$name'（只允许小写字母/数字/连字符/下划线）"; continue ;;
  esac
  if [ ! -d "$src" ]; then
    echo "!! 跳过 $name：源目录不存在 $src"
    continue
  fi

  # 整目录同步：自动带上 style.css / script.js / assets/ / specs/ 等辅助文件，
  # 排除视觉检查中间产物与本地垃圾文件
  if ls "$src"/*.html >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude='*visual-check*' \
      --exclude='.git/' --exclude='node_modules/' --exclude='.mimosa/' \
      --exclude='.DS_Store' \
      "$src"/ "$name"/
  else
    # Markdown 手册：用 md2html.py 转换成同风格 HTML（含 mermaid 渲染与资源拷贝）
    rm -rf "$name"
    python3 md2html.py "$src" "$name" "$title" "$icon" "$accent" < /dev/null
  fi

  # 已知修复：duckdb 的 index 里有指向本机 vane 项目的相对链接，站内改为根导航页
  if [ -f "$name/index.html" ]; then
    sed -i '' 's|\.\./\.\./vane/analysis/index\.html|../index.html|g' "$name/index.html" 2>/dev/null || true
  fi

  chapters=$(find "$name" -maxdepth 1 -name '*.html' ! -name 'index.html' | wc -l | tr -d ' ')
  TOTAL_PAGES=$((TOTAL_PAGES + chapters))
  TOTAL_BOOKS=$((TOTAL_BOOKS + 1))

  CARDS="$CARDS$(cat <<CARD
    <a class="card" href="${name}/index.html" style="--ac:${accent}">
      <div class="meta"><span class="badge">${icon} ${name}</span><span class="ch">${chapters} 页 · 纯静态</span></div>
      <h2>${title}</h2>
      <p>${desc}</p>
      <div class="go">进入手册 -></div>
    </a>
CARD
)
"
done 3< manifest.conf

if [ "$TOTAL_BOOKS" -eq 0 ]; then
  echo "!! manifest.conf 中没有可用的手册条目"
  exit 1
fi

# ---------- 2. 生成根导航页 ----------
cat > index.html <<HTML
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>源码深度学习手册集 · Source Study Handbooks</title>
<style>
:root{
  --bg:#0a0e16; --panel:#0f1524; --panel2:#131b2e; --line:#22304a; --line2:#2c3d5c;
  --tx:#dbe6f5; --tx2:#93a5c0; --tx3:#6b7d99; --te:#38bdf8;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
a{color:var(--te);text-decoration:none}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px}
.top{position:sticky;top:0;z-index:50;background:rgba(10,14,22,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:16px;height:54px}
.logo{font-weight:700;font-size:16px;white-space:nowrap}
.logo .m{color:var(--te)}
.topnav{margin-left:auto;display:flex;gap:4px}
.topnav a{font-size:12.5px;color:var(--tx2);padding:4px 8px;border-radius:6px}
.topnav a:hover{color:var(--tx);background:var(--panel2)}
.hero{padding:52px 0 36px;border-bottom:1px solid var(--line);
  background:radial-gradient(1100px 320px at 18% 0%,rgba(56,189,248,.10),transparent)}
.kicker{color:var(--te);font-size:13px;font-weight:600;letter-spacing:2px}
h1{font-size:33px;line-height:1.3;margin:10px 0 8px}
.sub{color:var(--tx2);font-size:15px;max-width:880px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:26px 0 6px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.stat .v{font-size:22px;font-weight:700;color:var(--te)}
.stat .l{font-size:12.5px;color:var(--tx2);margin-top:2px}
h2.sec{font-size:22px;margin:46px 0 6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px;margin:22px 0}
.card{display:block;background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--ac,#38bdf8);
  border-radius:14px;padding:20px 20px 16px;color:var(--tx2);transition:transform .15s,border-color .15s}
.card:hover{transform:translateY(-3px);border-color:var(--ac);text-decoration:none}
.card .meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.card .badge{font-size:12px;font-weight:600;color:var(--ac);background:color-mix(in srgb,var(--ac) 13%,transparent);
  padding:3px 10px;border-radius:99px}
.card .ch{font-size:12px;color:var(--tx3)}
.card h2{font-size:18px;margin:0 0 8px;color:var(--tx);line-height:1.4}
.card p{margin:0;font-size:13.5px;line-height:1.7;color:var(--tx2)}
.card .go{margin-top:14px;font-size:13px;font-weight:600;color:var(--ac)}
.how{background:var(--panel);border:1px solid var(--line);border-left:3px solid #34d399;border-radius:10px;
  padding:14px 18px;margin:18px 0 8px;font-size:14px;color:var(--tx2)}
.how b{color:var(--tx)}
.how code{background:#0e1626;border:1px solid var(--line);border-radius:5px;padding:1px 6px;
  font:12px ui-monospace,Menlo,monospace;color:#8fd3ff}
.foot{border-top:1px solid var(--line);color:var(--tx3);font-size:12.5px;padding:20px 0 44px}
.foot a{color:var(--tx2)}
</style>
</head>
<body>
<header class="top"><div class="wrap">
  <span class="logo"><span class="m">📚</span> 源码深度学习手册集</span>
  <nav class="topnav"><a href="https://github.com/vinlee19/handbooks">GitHub 仓库</a></nav>
</div></header>

<section class="hero"><div class="wrap">
  <div class="kicker">SOURCE STUDY HANDBOOKS · FROM 0 TO 1</div>
  <h1>源码深度学习手册集</h1>
  <p class="sub">一个仓库收录多个开源项目的源码深度分析手册。每本手册都是<strong>纯静态 HTML + 内联 SVG 图解</strong>，无任何外部依赖与构建步骤，浏览器打开即读。内容基于对各项目源码的逐模块分析整理。</p>
  <div class="stats">
    <div class="stat"><div class="v">${TOTAL_BOOKS} 本</div><div class="l">手册数量</div></div>
    <div class="stat"><div class="v">${TOTAL_PAGES} 页</div><div class="l">图文章节总量</div></div>
    <div class="stat"><div class="v">0 依赖</div><div class="l">纯静态 · 秒开</div></div>
  </div>
</div></section>

<main class="wrap">
  <h2 class="sec">手册列表</h2>
  <div class="grid">
${CARDS}  </div>

  <h2 class="sec">如何新增一本手册</h2>
  <div class="how">
    <b>唯一方法：</b>在仓库根目录的 <code>manifest.conf</code> 中新增一行
    <code>name|图标|标题|描述|主题色|源HTML目录</code>，然后运行 <code>./publish.sh</code> ——
    脚本会自动同步该目录的 HTML、重建根导航页、提交并推送到 GitHub Pages。
  </div>
</main>

<footer class="foot"><div class="wrap">
  Generated by <code>publish.sh</code> · $(date '+%Y-%m-%d %H:%M') ·
  <a href="https://github.com/vinlee19/handbooks">vinlee19/handbooks</a> ·
  Powered by GitHub Pages
</div></footer>
</body>
</html>
HTML

echo "已同步 ${TOTAL_BOOKS} 本手册 / ${TOTAL_PAGES} 页，根导航页已重新生成"

# ---------- 3. 提交并推送 ----------
git add -A < /dev/null
if git diff --cached --quiet < /dev/null && [ -z "$(git log @{u}.. --oneline 2>/dev/null)" ]; then
  echo "没有任何变化，无需推送"
else
  if ! git diff --cached --quiet < /dev/null; then
    git commit -m "sync: 手册更新 $(date '+%Y-%m-%d %H:%M')" < /dev/null
  fi
  if [ "$NO_PUSH" -eq 1 ]; then
    echo "已本地提交（--no-push，未推送）"
  else
    git push < /dev/null
    echo "已推送到 GitHub，Pages 会自动重新部署"
  fi
fi
