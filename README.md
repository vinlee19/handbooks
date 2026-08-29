# Mooncake 深度解析学习手册

对 [Mooncake](https://github.com/kvcache-ai/Mooncake)（Kimi 背后的 KVCache 语义化缓存池平台）源码与架构的深度学习笔记，以纯静态 HTML + 内联 SVG 的形式呈现，共 10 章 40+ 张手绘架构图。

**在线阅读**：<https://vinlee19.github.io/mooncake-study/>

## 目录

| 章节 | 主题 |
|---|---|
| [01 总览](https://vinlee19.github.io/mooncake-study/01-overview.html) | 项目定位、整体架构与核心概念 |
| [02 物理架构](https://vinlee19.github.io/mooncake-study/02-physical-architecture.html) | 集群拓扑与进程视图 |
| [03 Transfer Engine](https://vinlee19.github.io/mooncake-study/03-transfer-engine.html) | 传输引擎设计与抽象 |
| [04 RDMA 深入](https://vinlee19.github.io/mooncake-study/04-rdma-deep-dive.html) | RDMA 传输路径与拓扑感知 |
| [05 Store 架构](https://vinlee19.github.io/mooncake-study/05-store-architecture.html) | KVCache 存储服务总体架构 |
| [06 Master](https://vinlee19.github.io/mooncake-study/06-store-master.html) | Master 元数据管理与分配策略 |
| [07 Client](https://vinlee19.github.io/mooncake-study/07-store-client.html) | 客户端缓存与读写流程 |
| [08 高可用](https://vinlee19.github.io/mooncake-study/08-storage-ha.html) | 副本、容错与数据一致性 |
| [09 生态](https://vinlee19.github.io/mooncake-study/09-ecosystem.html) | 与 vLLM / SGLang 等推理框架的集成 |
| [10 数据流](https://vinlee19.github.io/mooncake-study/10-dataflow.html) | 端到端数据流全链路图解 |

## 本地阅读

无任何构建依赖，直接用浏览器打开 `index.html`，或：

```bash
python3 -m http.server 8000
# 访问 http://localhost:8000
```
