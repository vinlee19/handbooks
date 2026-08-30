# -*- coding: utf-8 -*-
"""Delta 手册每章追加的深度小节（第二轮）。"""

EXTRA2 = [
    # 01 总体架构
    [
        ("h3", "表属性（Table Properties）全解"),
        "Delta 的表级配置存储在 meta action 的 configuration 字段：delta.appendOnly（只追加）、delta.enableChangeDataFeed（CDC）、delta.enableDeletionVectors（DV）、delta.checkpointInterval、delta.deletedFileRetentionDuration、delta.logRetentionDuration、delta.columnMapping.mode 等。SET TBLPROPERTIES 修改后写入新的 meta action——配置变更也是一次版本提交，可审计可回滚。",
        ("h3", "Protocol 的特性矩阵"),
        "protocol 的 minReader/minWriter 版本与 feature 列表（v3+ 的 readerFeatures/writerFeatures）共同构成特性门槛：deletionVectors 需要 protocol ≥ (3,7) 且 feature 列表包含 deletionVectors；columnMapping 需要 (2,5)+columnMapping。旧引擎读新表会在 metadata 解析时直接报错——这是 Delta 防止「不认识特性的引擎破坏表」的门槛机制。",
        ("h3", "异常与恢复语义"),
        "Delta 的失败恢复不需要协调：提交 json 写完整即成功，写一半（连接断开）则文件不完整、JSON 解析失败被跳过（CRC 校验兜底）。Optimize/Vacuum 的失败都是安全的——它们的输入输出在日志里有完整记录，重试幂等。唯一的例外是 LogStore 的并发竞争：同版本号冲突由 ConflictChecker 或 LogStore 锁判定。",
    ],
    # 02 Transaction Log
    [
        ("h3", "stats 的 parquet 结构与 skipping"),
        "add.stats 字段内嵌 JSON：numRecords、minValues/maxValues（每列）、nullCount、tightBounds。Delta 的 data skipping 用这些统计构造 per-file 谓词：查询 WHERE ts > X 时跳过 maxValues.ts ≤ X 的文件。stats 收集的列由 delta.dataSkippingNumIndexedCols 控制（默认 32），列太多会影响写入性能——column mapping 模式的 delta.dataSkippingStatsColumns 可以只收集指定列。",
        ("h3", "LogStore 的 S3 实现细节"),
        "S3LogStore 的核心问题：S3 的 put 是原子的但没有 list-after-write 一致性（老版本）。解法：S3SingleDriverLogStore 用 DynamoDB 表记录「版本号 → 持有者」的条件写（putIfAbsent）实现互斥，写者先抢 DynamoDB 锁再写 json。DynamoDB 表的 TTL 与清理策略是运维要点。新版本引入 S3LogStoreFactory 改进与 VACUUM 兜底。",
        ("h3", "Log 与 Checkpoint 的一致性"),
        "checkpoint 写入与 json 提交之间存在窗口：checkpoint N 完成后，json N+1 才开始追加。读取时 _last_checkpoint 指向 N，从 N+1 开始重放。如果 checkpoint 写失败（部分 part），_last_checkpoint 未更新——旧的 checkpoint 仍有效，新 checkpoint 重做即可。这种「先写数据再更新指针」的模式与 Hudi 的 completed 重命名同构。",
    ],
    # 03 Snapshot
    [
        ("h3", "Snapshot 的惰性加载"),
        "SnapshotManagement 的缓存策略：当前 Snapshot 常驻内存，历史 Snapshot 按需构建（Time Travel 触发）并缓存固定数量。惰性构建的好处：Time Travel 的重放成本只在查询时付出。getSnapshotForVersion 会从当前快照向前（读 json）或向后（从更早的 checkpoint 重放）增量计算。",
        ("h3", "分区裁剪的实现"),
        "Snapshot.filesForDelivery(predicates) 的分区裁剪：meta 的 partitionColumns 定义分区键，add.partitionValues 记录每个文件的分区值。谓词先做分区等值/范围裁剪（HadoopFsRelation 的 partition pruning），再走 stats 裁剪。两层裁剪都在 Driver 端完成——这是 Delta 查询启动快的原因之一。",
        ("h3", "Snapshot 的不可变与并发"),
        "Snapshot 一旦构建就不可变（线程安全的读视图）。并发提交不会改变已有 Snapshot——事务开始时绑定版本，提交时用 ConflictChecker 判定与最新版本的兼容性。这种「静态快照 + OCC」模型让读操作天然线程安全，也让 Time Travel 的实现极其简单。",
    ],
    # 04 Checkpoint
    [
        ("h3", "checkpoint 的写入时序"),
        "严格顺序：① 写 N.checkpoint.parquet（10 parts 并行，内容为版本 N 的全量 action 快照）② 原子更新 _last_checkpoint（指向 N）③ 可选 CRC 文件。崩溃在 ① 时留下未引用 part（安全）；在 ② 前则 _last_checkpoint 仍指旧版本（安全）；② 成功后新 checkpoint 生效。任何时刻崩溃都不损坏快照构建——这个「先写数据再更新指针」的模式与 Hudi 的 completed 重命名同构。",
        ("h3", "CheckpointMetadata 与表特性"),
        "checkpoint 里有一条 CheckpointMetadata action 记录 checkpoint 自身的元信息（版本、协议）。v2 checkpoint 引入 sidecar 后，主文件只存 AddFile/RemoveFile 等高频 action 的代表样本，其余进 sidecar 按需读取——大表的 checkpoint 体积从 GB 级降到 MB 级。",
        ("h3", "与 Vacuum 的联动"),
        "checkpoint 引用的文件不会被 Vacuum 删除（Vacuum 以「最新快照 + 保留窗口」为准）。checkpoint 频率过低 → _delta_log json 过多；过高 → checkpoint 写开销频繁。默认 10 是经验平衡，大表可调大并配合更长的日志保留（delta.logRetentionDuration 默认 30 天）。",
    ],
    # 05 乐观事务
    [
        ("h3", "ConflictChecker 的具体判定序列"),
        "checkForMetadataAgainstConcurrentCommit（并发改 metadata → 冲突）；checkForAddedFilesThatShouldHaveBeenReadByCurrentTxn（并发 add 落在我的读谓词范围内 → WriteSerializable 下视操作而定）；checkForDeletedFilesAgainstCurrentTxn（我读的文件被并发删除 → 冲突）；checkForUpdatedFilesThatShouldHaveBeenRead...；checkForConcurrentSetTransaction。每个判定都返回 Conflict 或 Allow，源码里有完整注释解释每个分支的语义。",
        ("h3", "winners-vs-losers 的语义"),
        "提交竞争的输者不是简单失败：ConflictChecker 会比较输者与赢者的读写集合。若输者是纯追加（isBlindAppend）且赢者没有删除输者读过的文件 → 允许重试提交到新版本；否则抛 ConcurrentModificationException。这个「输者可重试」的语义是多写者管道高并行的关键。",
        ("h3", "coordinated commits（多写者协调）"),
        "新版本引入 coordinated commits：提交的最终裁定交给外部协调器（如 S3 的 commit coordinator），写者只负责准备 action。这把「谁赢」的裁决从客户端挪到服务端，支持多集群写同一张表——与 Hudi 的 Timeline Server 集中提交架构异曲同工。",
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
