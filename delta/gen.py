# -*- coding: utf-8 -*-
"""生成 Delta Lake 手册全部页面。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from site_fw import render_page
from ch import CHAPTERS
try:
    from extra import EXTRA
    for i, ex in enumerate(EXTRA):
        CHAPTERS[i]["sections"].extend([("p", x) if isinstance(x, str) else x for x in ex])
except ImportError:
    pass

ACCENT = "#4f8cff"
ICON = "🔷"
SITE = "Delta Lake 源码深度学习手册"
HERE = os.path.dirname(os.path.abspath(__file__))

NAV_LABELS = {
    "01-overview.html": "01 全景", "02-transaction-log.html": "02 事务日志",
    "03-snapshot.html": "03 快照", "04-checkpoint.html": "04 Checkpoint",
    "05-optimistic-tx.html": "05 乐观事务", "06-dml.html": "06 DML",
    "07-maintenance.html": "07 表维护", "08-kernel-ecosystem.html": "08 内核生态",
}
NAV = [("index.html", "目录")] + [(c["file"], NAV_LABELS[c["file"]]) for c in CHAPTERS]

def index_page():
    accs = ["#4f8cff", "#fbbf24", "#a78bfa", "#34d399", "#fb7185", "#c084fc", "#22d3ee", "#60a5fa"]
    descs = {
        "01-overview.html": "日志即表：_delta_log 唯一真相与仓库地图",
        "02-transaction-log.html": "七个 action 定义一张表的完整协议",
        "03-snapshot.html": "重放日志构建三集合内存视图",
        "04-checkpoint.html": "Parquet checkpoint 与 sidecar v2",
        "05-optimistic-tx.html": "OptimisticTransaction 与冲突判定",
        "06-dml.html": "Write/Delete/Update/Merge 统一物理路径",
        "07-maintenance.html": "Optimize、Z-Order 与 Vacuum",
        "08-kernel-ecosystem.html": "Delta Kernel、UniForm 与 Catalog",
    }
    toc_cards = [(accs[i], NAV_LABELS[c["file"]], [descs[c["file"]], f'<a href="{c["file"]}">进入章节 →</a>'])
                 for i, c in enumerate(CHAPTERS)]
    ch = dict(
        file="index.html", title="Delta Lake 源码深度学习手册 · 目录",
        kicker="DELTA LAKE SOURCE STUDY · FROM 0 TO 1",
        sub="Delta Lake 用一个预写日志目录把 ACID、Time Travel、Schema 演进带到了对象存储上。本手册沿「日志协议 → 快照 → 事务 → DML → 维护 → 生态」的主线逐模块拆解 spark/sql/delta 的源码。",
        stats=[("8 章", "图文详解"), ("7 类", "日志 action"), ("8 张", "archify 交互图")],
        sections=[("学习路径（从 0 到 1）", [
            ("cards", toc_cards),
            '<div class="co"><b>阅读建议：</b>02 的日志协议是一切的基础；03/04 讲读取如何加速；05/06 走写入与 DML；07 是运维视角；08 看生态演进。每章配套 archify 交互图在 <code>interactive/</code> 中。</div>',
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
