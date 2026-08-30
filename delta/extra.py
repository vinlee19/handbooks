# -*- coding: utf-8 -*-
"""Delta 手册每章追加的深度小节（面面俱到补充）。"""

EXTRA = [
    # 01 总体架构 补充
    [
        ("h3", "协议版本（Protocol）与特性门槛"),
        "protocol action 记录 minReaderVersion / minWriterVersion：任何引擎读到高于自身支持版本的 protocol 必须拒绝访问表。这是 Delta 防止「不认识表特性的引擎破坏数据」的门槛机制。deletion vectors、column mapping、v2 checkpoint 等特性都会抬升 protocol 版本——读源码时遇到 featureNotSupportedException，第一反应就是查 protocol。",
        ("h3", "LogStore 抽象与云存储适配"),
        "LogStore 接口的核心方法：writeEntry（原子写日志文件）、listFrom（版本序列出）、read（读日志）、getFileHandle。HDFSLogStore 靠 rename；S3SingleDriverLogStore 靠 DynamoDB 条件写（putIfAbsent 抢版本号）+ 重试；AzureLogStore 靠 rename-if-absent。每个实现都应对「同版本号并发提交」的竞争——输者读取赢者的提交进 ConflictChecker。",
        ("h3", "异常与恢复语义"),
        "Delta 的失败恢复同样不需要协调：提交 json 写完整即成功，写一半（连接断开）则文件不可见或被视为损坏（CRC/JSON 解析失败跳过）。Optimize/Vacuum 的失败都是安全的——它们的输入输出都在日志里有记录，重试幂等。",
    ],
    # 02 Transaction Log 补充
    [
        ("h3", "checkpoint 里 tombstones 的截断"),
        "checkpoint 不保存全部 tombstones：只保留最近 N 个版本相关的删除记录（delta.checkpoint.tombstone.retention 相关配置）。这意味着太旧的版本从 checkpoint 出发构建 Snapshot 时可能「缺少部分 tombstone」——即 Time Travel 的窗口同时受 checkpoint 截断策略约束。",
        ("h3", "commitInfo 与操作审计"),
        "commitInfo 记录：timestamp、operation（WRITE/MERGE/DELETE/OPTIMIZE…）、operationParameters、engineInfo（引擎版本）、isBlindAppend、txnId 等。审计场景（谁在何时改了什么）与 Confluent 式 CDC 管道都依赖它。isBlindAppend=true 表示提交者没有读任何现有文件（纯追加），ConflictChecker 可走快速路径。",
        ("h3", "domainMetadata 与可扩展性"),
        "domainMetadata 是表级 KV 配置域（如 clusteringDomain / delta-feature 域），带删除标记（removeDomainMetadata）。它让第三方特性在不改 action 协议的前提下扩展表语义——clustering、row tracking 等新特性都走这个通道。",
    ],
    # 03 Snapshot 补充
    [
        ("h3", "SnapshotManagement 的缓存策略"),
        "每个 SparkSession 的 DeltaLog 持有当前 Snapshot 引用与固定大小的历史 Snapshot 缓存（spark.databrowse.delta.snapshotCache... 相关）。getSnapshotForVersion 会从当前快照向前/向后增量重放。多线程访问靠不可变 Snapshot 保证线程安全——这是 Delta 并发读的设计基石。",
        ("h3", "分区裁剪与文件列举"),
        "Snapshot 暴露 filesForDelivery(predicates)：先用分区值裁剪（meta 的 partitionColumns），再用 add.stats 的 min/max/nullCount 做文件级裁剪。stats parquet（v2 可选）可把这些统计下推给 Spark 的统计框架做更智能的 join 优化。",
        ("h3", "变化语义的边界"),
        "Snapshot 是「某版本的真相」，但并发提交会让它过期——Delta 的策略是 Snapshot 不可变：事务开始时绑定版本，提交时用 ConflictChecker 判定与最新版本是否兼容，而不是让 Snapshot 动态变化。理解这一点就理解了 Delta 并发模型的静态性。",
    ],
    # 04 Checkpoint 补充
    [
        ("h3", "checkpoint 的写入时序"),
        "严格顺序：① 写 N.checkpoint.parquet（10 parts 并行，内容为版本 N 的全量 action 快照）② 写 _last_checkpoint（原子覆盖，指向 N）③ 可选 CRC 文件。崩溃在 ① 时留下未引用 part（安全）；崩溃在 ② 前则 _last_checkpoint 仍指旧版本（安全）；② 成功后新 checkpoint 生效。这个顺序保证任何时刻崩溃都不损坏快照构建。",
        ("h3", "CheckpointMetadata 与表特性"),
        "checkpoint 里还有一条 CheckpointMetadata action 记录 checkpoint 自身的元信息（版本、协议）。v2 checkpoint 引入 sidecar 后，主文件只存 AddFile/RemoveFile 等高频 action 的代表样本，其余进 sidecar 按需读取——大表的 checkpoint 体积从 GB 级降到 MB 级。",
        ("h3", "与 Vacuume 的联动"),
        "checkpoint 引用的文件不会被 Vacuum 删除（Vacuum 以「最新快照 + 保留窗口」为准）。checkpoint 频率过低 → _delta_log json 过多；过高 → checkpoint 写开销频繁。默认 10 是经验平衡，大表可调大并配合更长的日志保留。",
    ],
    # 05 乐观事务 补充
    [
        ("h3", "ConflictChecker 的具体判定序列"),
        "checkForMetadataAgainstConcurrentCommit（并发改 metadata → 冲突）；checkForAddedFilesThatShouldHaveBeenReadByCurrentTxn（并发 add 落在我的读谓词范围内 → WriteSerializable 下视操作而定）；checkForDeletedFilesAgainstCurrentTxn（我读的文件被并发删除 → 冲突）；checkForUpdatedFilesThatShouldHaveBeenRead...；checkForConcurrentSetTransaction。每个判定都返回 Conflict 或 Allow，源码里有完整的注释解释每个分支的语义。",
        ("h3", "winners-vs-losers 的语义"),
        "提交竞争的输者不是简单失败：ConflictChecker 会比较输者与赢者的读写集合。若输者是纯追加（isBlindAppend）且赢者没有删除输者读过的文件 → 允许重试提交到新版本；否则抛 ConcurrentModificationException。这个「输者可重试」的语义是多写者管道高并行的关键。",
        ("h3", "coordinated commits（多表/多写者协调）"),
        "新版本引入 coordinated commits：提交的最终裁定交给外部协调器（如 S3 的 commit coordinator），写者只负责准备 action。这把「谁赢」的裁决从客户端挪到服务端，支持多集群写同一张表。",
    ],
    # 06 DML 补充
    [
        ("h3", "WriteIntoDelta 的两种模式"),
        "Append 模式直接写新文件 add；Overwrite 模式产出 remove(旧文件)+add(新文件)，replaceWhere 谓词会把覆写限制在匹配分区（不匹配的分区若有数据则报错，除非 overwriteSchema）。动态分区覆写（dynamic partition overwrite）只覆盖本次写入涉及的分区值——Spark 写 parquet 的老习惯在 Delta 里是事务安全的。",
        ("h3", "DV 的读路径"),
        "启用 DV 后，读取器需要把 add 的 Parquet 与其 DV 位图（puffin blob）合并：位图中置位的行号视为已删除。Kernel 与 Spark reader 都实现了这套过滤。DV 让 Delete/Update 从「重写文件」变成「写位图」，代价是读取时多一次过滤——这是 Delta 在「读放大」与「写放大」之间的又一层权衡。",
        ("h3", "Merge 的执行计划"),
        "MergeIntoDelta 会产出两个分支的 Spark 计划：matched 分支（update/delete 目标行）与 notMatched 分支（insert 新行）。优化器把两个分支的文件重写合并成一次扫描。源码里 MergeIntoDeltaCommand 的 whole-stage 生成逻辑是最复杂的 DML——读它之前建议先读 WriteIntoDelta。",
    ],
    # 07 表维护 补充
    [
        ("h3", "Optimize 的 bin-packing 细节"),
        "OptimizeExecutor 把候选文件按 maxFileSize（默认 1GB）做贪心装箱：超大的文件跳过（已是好文件），小文件合并直到接近目标大小。产出 dataChange=false 的 add/remove 对。where 谓词可以只优化部分分区；predicate 推断还会结合分区裁剪。",
        ("h3", "Z-Order 的数学"),
        "Z-Order 把多列的值交织成一个一维排序键（位交错），使相近的多维点落在相近的文件。重写后每个文件的 stats（min/max）更紧，Spark 的 dynamic file prune 与 Spark 3.3+ 的 DPP 都能受益。代价是全量重写选中分区——所以 Z-Order 通常配合分区裁剪与低峰调度。",
        ("h3", "Vacuum 的安全边界"),
        "Vacuum 默认拒绝删除 7 天内的文件（即使日志未引用），给并发读者留缓冲。保留窗口必须 ≥ 最长的事务时长 + 最大的 Time Travel 回溯需求 + 流消费者的最大延迟，三者取最大。dry-run（VACUUM ... DRY RUN）返回待删文件清单供人工审核。",
    ],
    # 08 内核生态 补充
    [
        ("h3", "Delta Kernel 的分层"),
        "Kernel 分两层：Kernel API（日志重放、快照、文件列表、谓词翻译）与引擎 SPI（Parquet 读、文件系统访问）。引擎实现 SPI 后即可读任何 Delta 表——这使 StarRocks/ClickHouse/DuckDB 等引擎无需移植完整的 Delta Scala 代码。写入协议暂不下沉（仍以 Spark 命令为主）。",
        ("h3", "UniForm 的实现机制"),
        "UniForm 开启后（delta.universalFormat.enabledFormats=iceberg），每次 Delta 提交会异步触发 Iceberg 元数据转换（IcebergCompatV2 要求列映射等前置特性）：把 delta 的 add/remove 翻译成 Iceberg 的 data file / delete file 记录并生成 Iceberg metadata json。外部 Iceberg 引擎读到的表与 Delta 表数据完全一致。",
        ("h3", "与 Hudi 的互操作"),
        "Hudi 侧的 DeltaStamp/同步机制与 UniForm 方向一致：一张物理表同时暴露两种协议的元数据。这说明表格式竞争的终局是「一份物理数据 + 多协议元数据视图」——存储层收敛到 Parquet + 对象存储，上层协议互操作。",
    ],
]
