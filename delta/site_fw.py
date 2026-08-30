"""hudi/delta 手册共享渲染框架：与 mooncake/ducklake 系列同一视觉体系。"""

CSS = """
:root{
  --bg:#0a0e16; --panel:#0f1524; --panel2:#131b2e; --line:#22304a; --line2:#2c3d5c;
  --tx:#dbe6f5; --tx2:#93a5c0; --tx3:#6b7d99; --ac:__AC__;
  --code-bg:#0b1220;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
a{color:var(--ac);text-decoration:none} a:hover{text-decoration:underline}
.wrap{max-width:1080px;margin:0 auto;padding:0 28px}
.top{position:sticky;top:0;z-index:50;background:rgba(10,14,22,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:16px;height:54px}
.logo{font-weight:700;font-size:16px;color:var(--tx);white-space:nowrap;flex-shrink:0}
.logo .m{color:var(--ac)}
.topnav{margin-left:auto;display:flex;gap:4px;flex-wrap:wrap;overflow-x:auto}
.topnav a{font-size:12.5px;color:var(--tx2);padding:4px 8px;white-space:nowrap;border-radius:6px}
.topnav a:hover{color:var(--tx);background:var(--panel2);text-decoration:none}
.topnav a.on{color:var(--ac);background:color-mix(in srgb,var(--ac) 13%,transparent)}
.hero{padding:44px 0 30px;border-bottom:1px solid var(--line);
  background:radial-gradient(1100px 300px at 18% 0%,color-mix(in srgb,var(--ac) 10%,transparent),transparent)}
.kicker{color:var(--ac);font-size:13px;font-weight:600;letter-spacing:2px}
h1{font-size:32px;line-height:1.3;margin:10px 0 8px}
.sub{color:var(--tx2);font-size:15px;max-width:880px}
h2{font-size:22px;margin:46px 0 14px;display:flex;align-items:center;gap:10px}
h2 .n{display:inline-flex;align-items:center;justify-content:center;min-width:30px;height:30px;border-radius:8px;
 background:color-mix(in srgb,var(--ac) 13%,transparent);color:var(--ac);font-size:14px;font-weight:700}
h3{font-size:17px;margin:28px 0 10px;color:var(--tx)}
p{margin:10px 0;color:#c7d3e6}
strong{color:#eaf2fd}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:22px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.stat .v{font-size:21px;font-weight:700;color:var(--ac)}
.stat .l{font-size:12.5px;color:var(--tx2);margin-top:2px}
.fig{margin:22px 0;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 18px 10px}
.fig svg{display:block;width:100%;height:auto}
.figcap{display:flex;gap:8px;align-items:baseline;padding:10px 4px 6px;color:var(--tx2);font-size:13px;border-top:1px dashed var(--line);margin-top:12px}
.figcap b{color:var(--ac);font-size:12.5px;white-space:nowrap}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px;margin:22px 0}
.card{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--dc,#38bdf8);border-radius:12px;padding:14px 16px}
.card h4{margin:0 0 8px;font-size:14.5px;color:var(--tx)}
.card ul{margin:0;padding-left:18px;font-size:13px;color:var(--tx2)}
.card li{margin:4px 0}
.co{border:1px solid var(--line);border-left:3px solid var(--ac);background:var(--panel);border-radius:10px;padding:12px 16px;margin:16px 0;font-size:14px;color:var(--tx2)}
.co b{color:var(--tx)}
code{background:#0e1626;border:1px solid var(--line);border-radius:5px;padding:1px 6px;font:12px ui-monospace,Menlo,monospace;color:#8fd3ff}
pre{background:var(--code-bg);border:1px solid var(--line);border-radius:10px;padding:14px 16px;overflow-x:auto;font:12.5px/1.6 ui-monospace,Menlo,monospace;color:#c9d9ee}
pre code{background:none;border:none;padding:0;color:inherit}
table{border-collapse:collapse;margin:18px 0;width:100%;font-size:13.5px}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left;color:#c7d3e6}
th{background:var(--panel2);color:var(--tx);font-weight:600}
ul,ol{color:#c7d3e6;padding-left:22px} li{margin:5px 0}
.foot{border-top:1px solid var(--line);color:var(--tx3);font-size:12.5px;padding:20px 0 40px}
svg text{font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.svgm{font-family:ui-monospace,Menlo,Consolas,monospace!important}
"""

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def B(x, y, w, h, fill, stroke, title, sub=None, mono=False, tsize=13, tcolor="#dbe6f5", ssize=11, scolor="#8fa5c8", rx=9):
    cls = ' class="svgm"' if mono else ""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>']
    if sub:
        out.append(f'<text x="{x+w/2}" y="{y+h/2-6}" fill="{tcolor}" font-size="{tsize}" font-weight="bold" text-anchor="middle">{esc(title)}</text>')
        out.append(f'<text x="{x+w/2}" y="{y+h/2+14}" fill="{scolor}" font-size="{ssize}" text-anchor="middle"{cls}>{esc(sub)}</text>')
    else:
        out.append(f'<text x="{x+w/2}" y="{y+h/2+4}" fill="{tcolor}" font-size="{tsize}" font-weight="bold" text-anchor="middle"{cls}>{esc(title)}</text>')
    return "".join(out)

def A(x1, y1, x2, y2, label=None, color="#5f7ba6", dash=False, width=1.5, lx=None, ly=None, lcolor=None, marker="ar0"):
    d = ' stroke-dasharray="5 4"' if dash else ""
    lc = lcolor or color
    out = [f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d} marker-end="url(#{marker})"/>']
    if label:
        mx, my = lx if lx is not None else (x1+x2)/2, ly if ly is not None else (y1+y2)/2 - 6
        out.append(f'<text x="{mx}" y="{my}" fill="{lc}" font-size="11" text-anchor="middle">{esc(label)}</text>')
    return "".join(out)

def T(x, y, text, size=12, color="#93a5c0", bold=False, anchor="start", mono=False):
    cls = ' class="svgm"' if mono else ""
    w = ' font-weight="bold"' if bold else ""
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}"{w} text-anchor="{anchor}"{cls}>{esc(text)}</text>'

def R(x, y, w, h, fill, rx=8, stroke=None):
    s = f' stroke="{stroke}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>'

def FIG(title, caption, w, h, body, defs=""):
    return (f'<div class="fig"><svg viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f'<defs><marker id="ar0" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#5f7ba6"/></marker>'
            f'<marker id="ar1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#38bdf8"/></marker>'
            f'<marker id="ar2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#fbbf24"/></marker>{defs}</defs>'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#0c1322" rx="10"/>{body}</svg>'
            f'<div class="figcap"><b>图</b><span>{esc(caption)}</span></div></div>')

def NAV(icon, site, chapters, current):
    links = "".join(
        f'<a href="{f}"{" class=on" if f == current else ""}>{label}</a>'
        for f, label in chapters)
    return (f'<header class="top"><div class="wrap">'
            f'<span class="logo"><span class="m">{icon}</span> {esc(site)}</span>'
            f'<nav class="topnav">{links}</nav></div></header>')

def CARDS(cards):
    out = ['<div class="cards">']
    for dot, title, items in cards:
        lis = "".join(f"<li>{i}</li>" for i in items)
        out.append(f'<div class="card" style="--dc:{dot}"><h4>{title}</h4><ul>{lis}</ul></div>')
    out.append("</div>")
    return "".join(out)

def render_page(accent, icon, site, chapters, ch, out_path):
    css = CSS.replace("__AC__", accent)
    nav = NAV(icon, site, chapters, ch["file"])
    stats = "".join(f'<div class="stat"><div class="v">{v}</div><div class="l">{l}</div></div>'
                    for v, l in ch.get("stats", []))
    body = []
    for i, (h2, items) in enumerate(ch["sections"], 1):
        body.append(f'<h2><span class="n">{i:02d}</span>{h2}</h2>')
        for it in items:
            kind, val = (it if isinstance(it, tuple) else ("p", it))
            if kind == "p":
                body.append(f"<p>{val}</p>")
            elif kind == "h3":
                body.append(f"<h3>{val}</h3>")
            elif kind == "fig":
                body.append(val)
            elif kind == "co":
                body.append(f'<div class="co"><b>{val}</b></div>')
            elif kind == "co2":
                body.append(f'<div class="co">{val}</div>')
            elif kind == "pre":
                import html as _h
                body.append(f"<pre><code>{_h.escape(val)}</code></pre>")
            elif kind == "table":
                body.append(val)
            elif kind == "cards":
                body.append(CARDS(val))
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(ch['title'])}</title>
<style>{css}</style>
</head>
<body>
{nav}
<section class="hero"><div class="wrap">
  <div class="kicker">{esc(ch['kicker'])}</div>
  <h1>{esc(ch['title'])}</h1>
  <p class="sub">{ch['sub']}</p>
  <div class="stats">{stats}</div>
</div></section>
<main class="wrap">
{"".join(body)}
</main>
<footer class="foot"><div class="wrap">源码深度学习手册 · 基于逐模块源码分析 · <a href="index.html">返回目录</a></div></footer>
</body>
</html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
