# 源码深度学习手册集 · Source Study Handbooks

一个仓库收录多个开源项目的**源码深度分析手册**。每本手册都是纯静态 HTML + 内联 SVG 图解，零依赖、零构建，浏览器打开即读。

**在线阅读**：<https://vinlee19.github.io/handbooks/>

## 手册列表

| 手册 | 内容 | 目录 |
|---|---|---|
| 🌙 Mooncake 源码深度学习手册 | Kimi 底层 KVCache 中心化分离式架构：Transfer Engine、RDMA、Store 三部曲、端到端数据流 | [`mooncake/`](mooncake/index.html) |
| 🦆 DuckDB 从 0 到 1：源码深度分析 | 物理架构、查询流水线、Pipeline 执行、MVCC 冲突、WAL 与 Checkpoint、事务生命周期 | [`duckdb/`](duckdb/index.html) |
| 🏞 DuckLake 源码深度解析 | 元数据目录、快照时间旅行、读写路径、事务并发、内联 Compaction、后端加密 | [`ducklake/`](ducklake/index.html) |

## 新增一本手册（唯一方法）

1. 在根目录 [`manifest.conf`](manifest.conf) 中新增一行：

   ```
   name|图标|标题|一句话描述|主题色|源HTML目录的绝对路径
   ```

2. 运行：

   ```bash
   ./publish.sh
   ```

脚本会自动：同步该目录的全部 HTML（排除 `*visual-check*` 中间产物、自动带上 `assets/`）-> 重建根导航页 `index.html` -> 提交并推送，GitHub Pages 自动重新部署。

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
├── mooncake/         # 各手册一个子目录
├── duckdb/
└── ducklake/
```
