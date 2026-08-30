# -*- coding: utf-8 -*-
"""生成 Hudi 手册全部页面。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_fw import render_page, CARDS
from ch_a import CHAPTERS_A
from ch_b import CHAPTERS_B

ACCENT = "#00e5cc"
ICON = "🪶"
SITE = "Hudi 源码深度学习手册"
HERE = os.path.dirname(os.path.abspath(__file__))

CHAPTERS = CHAPTERS_A + CHAPTERS_B
for mod, attr in (("extra", "EXTRA"), ("extra2", "EXTRA2"), ("extra3", "EXTRA3")):
    try:
        m = __import__(mod)
        for i, ex in enumerate(getattr(m, attr, [])):
            norm = []
            for x in ex:
                if isinstance(x, str): norm.append(("p", x))
                elif isinstance(x, tuple) and len(x) == 3:
                    norm.append((x[0], x[1])); norm.append(("p", x[2]))
                else: norm.append(x)
            CHAPTERS[i]["sections"].extend(norm)
    except ImportError:
        pass
NAV_LABELS = {
    "01-overview.html": "01 全景", "02-timeline.html": "02 Timeline",
    "03-file-layout.html": "03 文件布局", "04-cow-write.html": "04 COW 写",
    "05-mor-compaction.html": "05 MOR", "06-index.html": "06 索引",
    "07-read-path.html": "07 读路径", "08-concurrency.html": "08 并发",
}
NAV = [(c["file"], NAV_LABELS[c["file"]]) for c in CHAPTERS]

def index_page():
    toc_cards = []
    accs = ["#00e5cc", "#fbbf24", "#a78bfa", "#22d3ee", "#34d399", "#fb7185", "#c084fc", "#60a5fa"]
    descs = {
        "01-overview.html": "设计哲学、两种表类型与仓库模块地图",
        "02-timeline.html": "instant 状态机、.hoodie 文件形态与崩溃恢复",
        "03-file-layout.html": "FileGroup / FileSlice / Log File 三层布局",
        "04-cow-write.html": "upsert 八步流水线与 marker 防部分写",
        "05-mor-compaction.html": "deltacommit 追加与异步 compaction",
        "06-index.html": "Bloom / Bucket / HBase / Record Index",
        "07-read-path.html": "Snapshot / ReadOptimized / Incremental",
        "08-concurrency.html": "锁、OCC 冲突校验与时间线原子性",
    }
    for i, c in enumerate(CHAPTERS):
        toc_cards.append((accs[i], NAV_LABELS[c["file"]],
                          [descs[c["file"]],
                           f'<a href="{c["file"]}">进入章节 →</a>']))
    ch = dict(
        file="index.html", title="Hudi 源码深度学习手册 · 目录",
        kicker="APACHE HUDI SOURCE STUDY · FROM 0 TO 1",
        sub="Apache Hudi 把数据库的增量语义（upsert / delete / 事务 / 索引）带到数据湖上。本手册按「写入 → 元数据 → 布局 → 索引 → 读取 → 并发」的顺序逐模块拆解源码，全部结论有源码路径佐证。",
        stats=[("8 章", "图文详解"), ("40+", "源码坐标引用"), ("8 张", "archify 交互图")],
        sections=[("学习路径（从 0 到 1）", [
            ("cards", toc_cards),
            '<div class="co"><b>阅读建议：</b>先读 01/02 建立心智模型，再沿 03→04→05 走写入主线，06/07 补索引与读路径，08 收束并发语义。每章末尾的交互图可在 <code>interactive/</code> 中查看。</div>',
        ])],
    )
    render_page(ACCENT, ICON, SITE, NAV, ch, os.path.join(HERE, "index.html"))

def main():
    for c in CHAPTERS:
        render_page(ACCENT, ICON, SITE, NAV, c, os.path.join(HERE, c["file"]))
    index_page()
    print("generated:", ", ".join(c["file"] for c in CHAPTERS), "index.html")

if __name__ == "__main__":
    main()
