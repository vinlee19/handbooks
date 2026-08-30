# -*- coding: utf-8 -*-
"""Delta 手册第三轮深度补充（每章 3-4 节）。"""
EXTRA3 = [
    # 01 总体架构
    [
        ("h3", "LogStore 抽象的接口与实现"),
        "LogStore 接口的核心方法：writeEntry（原子写日志文件）、listFrom(version)（版本序列出）、read(version)（读日志）、get_FileHandle。HDFSLogStore 靠 rename 原子性；S3SingleDriverLogStore 靠 DynamoDB 条件写（putIfAbsent 抢版本号）+ 重试；AzureLogStore 靠 rename-if-absent。每个实现都应对「同版本号并发提交」的竞争——输者读取赢者的提交进 ConflictChecker。LogStoreProvider 按 scheme（s3://, hdfs://, file://, abfs://…）分发。",
        ("h3", "异常与恢复语义"),
        "Delta 的失败恢复不需要协调：提交 json 写完整即成功，写一半（连接断开）则文件不完整、JSON 解析失败被跳过（CRC 校验兜底）。Optimize/Vacuum 的失败都是安全的——它们的输入输出在日志里有完整记录，重试幂等。唯一的例外是 LogStore 的并发竞争：同版本号冲突由 ConflictChecker 或 LogStore 锁判定。",
        ("h3", "与 Iceberg/Hudi 的架构对比"),
        "Iceberg 的元数据是 manifest list → manifest → data file 三层树（快照不可变、写 manifest 文件）；Hudi 的元数据是 timeline + file group 视图；Delta 的元数据是扁平的 json 日志序列。三者的共识是「数据文件不可变 + 元数据原子提交」，差异在元数据的组织方式与更新语义的丰富程度——Hudi 的 record-level 索引与 Delta 的 DV 是两种不同的行级删除实现。",
    ],
    # 02 Transaction Log
    [
        ("h3", "stats 的 JSON 结构与 skipping 效果"),
        "add.stats 字段的 JSON 结构：{\"numRecords\":1000,\"minValues\":{\"ts\":\"2024-01-15\",\"price\":10.0},\"maxValues\":{\"ts\":\"2024-01-15\",\"price\":99.9},\"nullCount\":{\"ts\":0,\"price\":5}}。查询时 DeltaFileIndex 读取每个文件的 stats，用 min/max 谓词决定跳过哪些文件。1000 文件的表上，一次 WHERE ts=X 的查询通常只读 5-20 个文件——数据 skipping 是 Delta 查询性能的第一道裁剪。",
        ("h3", "remove 的 deletionTimestamp"),
        "remove action 携带 deletionTimestamp 但它只是信息字段：真正决定「文件是否在某个版本有效」的是日志重放时 add 集合减去 remove 集合。deletionTimestamp 的用途是 Vacuum（判断文件是否可以被物理删除）与审计（记录删除发生的时间）。注意 remove 不携带行级信息——行级删除由 deletion vectors 承担。",
        ("h3", "LogStore 的并发竞争处理"),
        "S3 上两个写者同时提交版本 N：DynamoDB putIfAbsent 只有一个成功。赢者的 json 出现在 _delta_log；输者收到 ConditionalCheckFailedException → 读取赢者的 json → 进 ConflictChecker → 可重试则递增版本号重新提交。整个循环在 doCommitRetryLoop 中自动完成——调用方无感知（除非最终重试次数耗尽）。HDFS 上靠 rename 原子性：重命名到已存在的路径会失败，语义等价。",
    ],
    # 03 Snapshot
    [
        ("h3", "SnapshotManagement 的缓存策略"),
        "每个 SparkSession 的 DeltaLog 持有当前 Snapshot 引用与固定大小的历史 Snapshot 缓存（spark.databrowse.delta.snapshotCache... 相关）。getSnapshotForVersion 会从当前快照向前/向后增量重放。多线程访问靠不可变 Snapshot 保证线程安全——这是 Delta 并发读的设计基石。",
        ("h3", "分区裁剪与文件列举"),
        "Snapshot 暴露 filesForDelivery(predicates)：先用分区值裁剪（meta 的 partitionColumns），再用 add.stats 的 min/max/nullCount 做文件级裁剪。stats parquet（v2 可选）可把这些统计下推给 Spark 的统计框架做更智能的 join 优化。",
        ("h3", "变化语义的边界"),
        "Snapshot 是「某版本的真相」，但并发提交会让它过期——Delta 的策略是 Snapshot 不可变：事务开始时绑定版本，提交时用 ConflictChecker 判定与最新版本是否兼容，而不是让 Snapshot 动态变化。理解这一点就理解了 Delta 并发模型的静态性。",
    ],
    # 04 Checkpoint
    [
        ("h3", "checkpoint 的写入时序"),
        "严格顺序：① 写 N.checkpoint.parquet（10 parts 并行，内容为版本 N 的全量 action 快照）② 原子更新 _last_checkpoint（指向 N）③ 可选 CRC 文件。崩溃在 ① 时留下未引用 part（安全）；在 ② 前则 _last_checkpoint 仍指旧版本（安全）；② 成功后新 checkpoint 生效。这个顺序保证任何时刻崩溃都不损坏快照构建。",
        ("h3", "CheckpointMetadata 与表特性"),
        "checkpoint 里有一条 CheckpointMetadata action 记录 checkpoint 自身的元信息（版本、协议）。v2 checkpoint 引入 sidecar 后，主文件只存 AddFile/RemoveFile 等高频 action 的代表样本，其余进 sidecar 按需读取——大表的 checkpoint 体积从 GB 级降到 MB 级。",
        ("h3", "与 Vacuum 的联动"),
        "checkpoint 引用的文件不会被 Vacuum 删除（Vacuum 以「最新快照 + 保留窗口」为准）。checkpoint 频率过低 → _delta_log json 过多；过高 → checkpoint 写开销频繁。默认 10 是经验平衡，大表可调大并配合更长的日志保留。",
    ],
    # 05 乐观事务
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
