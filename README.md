# 源码深度学习手册集 · Source Study Handbooks

一个仓库收录多个开源项目的**源码深度分析手册**。HTML 手册为纯静态页面 + 内联 SVG 图解；Markdown 手册由 `md2html.py` 自动转换为同风格页面（mermaid 图经 CDN 渲染）。零构建、浏览器打开即读。

**在线阅读**：<https://vinlee19.github.io/handbooks/>

## 手册列表（12 本 / 100 页）

| 手册 | 内容 | 目录 |
|---|---|---|
| 🌙 Mooncake 源码深度学习手册 | Kimi 底层 KVCache 中心化分离式架构：Transfer Engine、RDMA、Store 三部曲、端到端数据流 | [`mooncake/`](mooncake/index.html) |
| 🦆 DuckDB 从 0 到 1 | 物理架构、查询流水线、Pipeline 执行、MVCC 冲突、WAL 与 Checkpoint、事务生命周期 | [`duckdb/`](duckdb/index.html) |
| 🏞 DuckLake 源码深度解析 | 湖仓元数据层：目录设计、快照时间旅行、读写路径、事务并发与后端加密 | [`ducklake/`](ducklake/index.html) |
| 🤖 Pi 源码深度剖析 | TypeScript 编码智能体框架：架构、AI 层、Agent 循环、会话压缩、扩展、TUI、RPC | [`pi/`](pi/index.html) |
| 🏹 Lance 深度源码解析 | 面向 AI 的列式格式：物理布局、编码、读写路径、向量/标量索引、SIMD | [`lance/`](lance/index.html) |
| 🌖 Moonlink 源码深度解析 | Mooncake 生态 Rust 湖仓表引擎：摄入、核心引擎、DV、WAL、Iceberg、LSN 并发 | [`moonlink/`](moonlink/index.html) |
| 🐘 pg_mooncake 源码深度解析 | Postgres 列存扩展：架构、Moonlink 引擎、CDC 复制、Iceberg、DuckDB 查询 | [`pg_mooncake/`](pg_mooncake/index.html) |
| 🧭 Vane 从 0 到 1 | 物理架构、引擎原理、核心交互、分布式查询、多模态 AI 与扩展编写 | [`vane/`](vane/index.html) |
| 🧩 Apache Burr 源码深度剖析 | 状态机驱动的 AI 应用框架：State/Action/Application、图构建、持久化、追踪 | [`burr/`](burr/index.html) |
| ☁️ Databend 源码深度解析 | 云原生 OLAP：三层架构、Raft 元数据、SQL 前端、优化器、FUSE 存储（md 转换） | [`databend/`](databend/index.html) |
| 🐡 Daft 源码深度解析 | 分布式 DataFrame：核心类型、DSL、逻辑计划、Swordfish 执行（md 转换） | [`daft/`](daft/index.html) |
| 💨 Airflow 源码分析 | 2.x vs 3.x：生态全景、组件交互、数据流与部署架构图解（md 转换） | [`airflow/`](airflow/index.html) |

## 新增一本手册（唯一方法）

1. 在根目录 [`manifest.conf`](manifest.conf) 中新增一行：

   ```
   name|图标|标题|一句话描述|主题色|源目录绝对路径
   ```

   源目录里放 HTML（直接同步）或 Markdown（自动经 `md2html.py` 转成同风格页面）均可。

2. 运行：

   ```bash
   ./publish.sh
   ```

脚本会自动同步内容（排除 `*visual-check*` 产物与 `.mimosa` 等）、重建根导航页、提交并推送，GitHub Pages 自动重新部署。

## 本地阅读

```bash
python3 -m http.server 8000
# 访问 http://localhost:8000
```

## 结构

```
├── index.html        # 根导航页（由 publish.sh 生成）
├── manifest.conf     # 手册注册表：新增手册只改这里
├── publish.sh        # 唯一发布方法
├── md2html.py        # Markdown -> 同风格 HTML 转换器（md 手册用）
├── mooncake/ ...     # 各手册一个子目录
└── airflow/
```
