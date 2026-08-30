# -*- coding: utf-8 -*-
"""Delta 手册第四轮补充（最后一轮，推过 1000 线）。"""
EXTRA4 = [
    # 01
    [
        ("h3", "写入协议的四个设计约束"),
        "Delta 的写入协议有四个硬约束：① 文件级原子性（整个 JSON 写完整才可见）② 前缀有序（版本号严格递增）③ 幂等（同版本号不可重复）④ dataChange 标记（区分逻辑数据变化与物理布局变化）。这四个约束保证了多写者的一致性底线，也是所有 LogStore 实现必须满足的接口契约。",
        ("h3", "Spark 集成的三层架构"),
        "Delta 与 Spark 的集成分三层：① Catalog 层（DeltaCatalog 实现 V2Catalog 接口，管 DDL/表发现）② Planner 层（DuckdbPlannerHook / DeltaAnalysis 把 Delta 表的查询劫持进 Spark 的 BatchScanExec）③ Execution 层（WriteIntoDelta / DeltaOptimizedWriterExec 等物理算子）。三层各有独立的钩子与优化点。",
        ("h3", "Delta 与 Hudi 的关键差异"),
        "Delta：无内置更新索引（依赖 stats 裁剪 + full scan 定位）、日志扁平化（无 fileGroup 概念）、DV 是新特性；Hudi：内置多索引（Bloom/Bucket/Record）、fileGroup 概念贯穿全库、timeline 即元数据。Delta 更简单直观，Hudi 的更新语义更丰富——这是两种设计哲学的取舍。",
    ],
    # 02
    [
        ("h3", "action 的 JSON 解析与前向兼容"),
        "Action 伴生对象通过 <code>JsonUtils.mapper</code>（Jackson ObjectMapper）反序列化：未知字段被忽略（<code>FAIL_ON_UNKNOWN_PROPERTIES=false</code>），使新版本写入的 action 旧版本可安全解析。protocol 不满足时才拒绝——前向兼容由 protocol 门控，而不是由 JSON 解析器。这种「宽松解析 + 严格 protocol」的设计是 Delta 演进策略的核心。",
        ("h3", "add.stats 的生成与存储"),
        "stats 由 <code>StatisticsCollection</code> 在写入时计算：扫描每个文件的每一列取 min/max/nullCount。列数超过 <code>delta.dataSkippingNumIndexedCols</code>（默认 32）的列不收集。clusterBy 表自动把 clustering 列放在前 32 列——这就是 clustering 改善裁剪的原因。stats 本身也是 JSON 序列化后存进 add，大表可以考虑 <code>delta.checkpoint.parquet</code> 中的 stats parquet 加速读取。",
        ("h3", "setTransaction 的使用场景"),
        "setTransaction 的两个核心场景：① Structured Streaming 的 checkpoint 机制（每个 micro-batch 记录 (queryId, batchId) 防重放）② 自定义写入者的幂等标记（如 Kafka offset 追踪）。不使用 setTransaction 的流式写入没有 exactly-once 语义——重复消费会产生重复数据。",
    ],
    # 03
    [
        ("h3", "Snapshot 的分区谓词缓存"),
        "Snapshot 构建后按分区列缓存谓词映射：每个分区值的文件列表。这对分区数多、文件数少的表优化显著（如按小时分区的流水表）。缓存随新提交失效重算——频繁写入的场景缓存命中率低，这是 Delta 查询在高频写入场景下的性能瓶颈之一。",
        ("h3", "tombstones 与冲突检测的关系"),
        "tombstones 不只是「已删除文件」的记录：ConflictChecker 用它判断「我读的文件是否被并发删除」。checkpoint 截断 tombstones 后，太旧的冲突检测会失效——这就是 Delta 的隔离级别在高频写入场景下的退化。CheckpointMetadata 里记录了 tombstone 截断的水位。",
        ("h3", "与 Hudi FileSystemView 的对比"),
        "Delta 的 Snapshot 直接维护 activeFiles 集合（扁平），Hudi 的 FileSystemView 按 fileGroup 分层组装 fileSlice。Delta 的模型更简单但缺少「文件组身份」概念（更新定位靠 stats/bloom 而非结构化索引）；Hudi 的模型更复杂但支持 record-level 操作。两者的视图缓存都是进程内存 + 可选服务端化。",
    ],
    # 04
    [
        ("h3", "checkpoint 的触发时机与并发"),
        "post-commit hook 在每次提交后检查版本号是否为 checkpointInterval 的倍数。多个并行写者可能同时触发 checkpoint——CheckpointProvider 的 last_checkpoint 信息让后者检测到前者已完成（检查 version 是否一致），避免重复写。VACUUM 不会删除仍被 _last_checkpoint 引用的 checkpoint 文件。",
        ("h3", "v1 与 v2 的兼容与选择"),
        "v1 checkpoint 的局限：10 个 part 的写并行度上限固定、单文件可能过大（add action 含完整 stats JSON）。v2 引入 sidecar 后主文件精简、sidecar 按需读取，但要求引擎支持 sidecar 读取（protocol ≥ (3,7)）。旧引擎读 v2 checkpoint 需降级回放完整 json 日志——向后兼容的代价。",
        ("h3", "与 Hudi FileSystemView 缓存的对比"),
        "Delta 的 checkpoint 是全量快照（重放归零）；Hudi 的 FileSystemView 是增量刷新（只加载新 instant 引用的文件）。Delta 的模型在大表上需要 checkpoint 控制重放成本；Hudi 的模型在增量刷新时更轻量但需要全量重建的兜底。两者最终都走向「服务端缓存」的架构。",
    ],
    # 05
    [
        ("h3", "isBlindAppend 的判定与优化"),
        "<code>isBlindAppend=true</code> 表示事务没有读任何已有文件（纯追加写入）。ConflictChecker 对 blind append 走快速路径：只要没有并发删除/元数据变更就自动通过（不需要逐文件比对）。WriteIntoDelta 的 Append 模式默认 isBlindAppend——这意味着纯追加的流管道可以无限并行，没有 OCC 冲突。",
        ("h3", "txn 的 readFiles 与 readPredicates"),
        "事务读过的文件通过 <code>txn.readFiles</code>（Set[AddFile]）登记——这使 ConflictChecker 能精确判断「我读的文件是否被并发删/改」。readPredicates 是更高级的登记方式（只记谓词不记文件），Delta 用分区/统计裁剪来判断谓词范围内是否有并发变更。两种方式的精度与性能的权衡在 ConflictChecker 的源码中有详细注释。",
        ("h3", "post-commit hooks 的执行顺序"),
        "提交成功后按序触发：① checkpoint hook（版本为 checkpointInterval 倍数时）② UniForm 同步 hook（如开启）③ metrics 上报 hook ④ cleanup hook（清理临时文件）。每个 hook 失败不影响主表正确性——它们都可以安全重试。读 OptimisticTransaction 的 postCommit() 方法可以看到完整的注册顺序。",
    ],
    # 06
    [
        ("h3", "Delete 的物理路径两路对比"),
        "全文件命中（所有行都满足条件）：只写 remove，不读不写数据文件——这是最快的删除。部分命中：需要重写文件（读旧 → 过滤 → 写新）或使用 DV（只写位图）。Delta 自动选择：如果命中行数/总行数超过阈值，重写更快；否则 DV 更省。这个自适应逻辑在 DeleteCommand 的源码中有完整的判定条件。",
        ("h3", "Overwrite 与 replaceWhere 的语义"),
        "<code>mode(\"overwrite\").option(\"replaceWhere\", \"ts >= '2024-01-15'\")</code>：只覆写满足条件的文件（remove 旧 + add 新），其他分区不动。这是 Delta 的「条件覆写」语义——与传统 Parquet 目录的整目录覆盖完全不同。replaceWhere 谓词不满足时（有数据但不在条件内）可选报错或忽略，由 <code>overwriteSchema</code> 与配置决定。",
        ("h3", "column mapping：列重命名不重写"),
        "column mapping 模式（delta.columnMapping.mode=name）让列重命名/删除只产生 meta action（物理 Parquet 不变）：add 的 physicalName 保持不变，逻辑名映射由 meta 的 schemaString 维护。代价是 protocol 版本抬升（旧引擎不可读）。这是 Delta 列级演进的核心机制——与 Iceberg 的 column mapping 异曲同工。",
    ],
    # 07
    [
        ("h3", "Optimize 的 metrics 与监控"),
        "Optimize 完成后 commitInfo 记录 metrics：numFilesAdded/Removed、filesSkipped（裁剪效果）、zOrderStats（zOrderCols 的 IO 统计）。这些 metrics 通过 Spark listener 或 DeltaLog API 可查询——是表维护效果的量化依据。生产建议：监控 Optimize 后的文件大小分布与 stats 覆盖率。",
        ("h3", "liquid clustering 的实现"),
        "Liquid clustering（delta.clusteringColumns）用 Hilbert 曲线替代 Z-Order 的 Z 曲线（更高维度的空间填充效率），且支持增量聚类（只重排新写入的文件，不需要全量重排）。clustering columns 是表属性，写入时自动按聚类键组织——比 Optimize+Z-Order 的手动模式更简单。",
        ("h3", "Vacuum 与 DV 的关系"),
        "DV 位图文件（puffin）附着在 add 引用的文件上，Vacuum 以「add 是否被引用」决定 puffin 的存废。Optimize 重写时融合 DV：被 DV 标记删除的行在新文件中不再出现，DV 位图本身也被移除。这就是 DV 的生命周期管理：写入 → 读时过滤 → Optimize 时融合 → Vacuum 时清理。",
    ],
    # 08
    [
        ("h3", "Kernel 的 Java API 示例"),
        "Java Kernel 的核心接口：<code>Table.forPath(path)</code> → <code>getSnapshot(version)</code> → <code>getScanBuilder()</code> → <code>build().getScanFiles()</code> + <code>getReadSchema()</code> → 引擎自行读 Parquet 并过滤 DV。Kernel 还提供 <code>getLogReplay()</code> 接口自定义日志重放逻辑——这是嵌入式引擎（如 StarRocks 的 Delta reader）的集成入口。",
        ("h3", "UniForm 的 IcebergCompatV1/V2 差异"),
        "V1 要求表启用 column mapping（physicalName 映射），在每次提交后异步生成 Iceberg metadata；V2 额外要求 DV 支持并将 Iceberg 元数据写入 _delta_log/iceberg/ 子目录。V2 是推荐版本：它使外部 Iceberg 引擎能完整看到 DV 过滤后的数据（V1 的 DV 行对 Iceberg 引擎不可见）。",
        ("h3", "Delta 与 Hudi/Iceberg 的互操作终局"),
        "三者的互操作方向：UniForm（Delta→Iceberg/Hudi）、DeltaStamp（Hudi→Delta）、Iceberg 的 REST Catalog（协议级统一）。终局形态：一份物理数据 + N 份元数据视图，每份视图服务一类引擎的读写需求。源码级的启示：不要在引擎层做表格式绑定——把「读表」抽象为独立库（如 Delta Kernel），把「写表」留给专用引擎。",
    ],
]
