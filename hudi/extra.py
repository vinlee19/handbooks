# -*- coding: utf-8 -*-
"""Hudi 手册每章追加的深度小节（面面俱到补充）。"""

EXTRA = [
    # 01 总体架构 补充
    [
        ("h3", "表类型在 DDL 与配置层的体现"),
        "建表时 <code>hoodie.datasource.write.table.type</code>（或 Flink 的 <code>table.type</code>）决定 COW/MOR，写入 <code>hoodie.properties</code> 的 <code>hoodie.table.type</code> 字段，此后不可更改（只能重建表）。 preorder 字段还有 <code>hoodie.table.name</code>、<code>hoodie.table.version</code>、<code>hoodie.timeline.layout.version</code>、<code>hoodie.table.base.file.format</code>（PARQUET/ORC）等。MetaClient 初始化时严格校验这些字段——读 <code>HoodieTableConfig</code> 就是读一张表的身份证。",
        ("h3", "HoodieWriteConfig：全库参数的收口"),
        "所有写侧行为都由 <code>HoodieWriteConfig</code>（构建器模式）承载：索引选择、并行度、小文件阈值、compaction/clustering/clean 触发、marker 模式、schema 演进策略、锁配置……参数超过 400 个，按 <code>hoodie.xxx.yyy</code> 命名。源码里每个引擎的 ConfigClass 会把 <code>SQLConf</code>/<code>FlinkConfig</code> 的键映射过来。读参数文档不如直接读 <code>HoodieWriteConfig.Builder</code> 的 setter——每个 setter 的 javadoc 就是语义说明。",
        ("h3", "Timeline Server：集中式架构"),
        "默认架构下每个 Spark executor 都要建 FileSystemView、查索引、写 marker——写放大与重复扫描随并行度线性增长。Timeline Server 模式把这三件事集中到一个常驻服务：executor 通过 RPC 请求视图分片与 marker 代写。相关配置 <code>hoodie.embed.timeline.server</code>（Driver 内嵌）或独立进程部署。这是大集群 + 对象存储场景的推荐形态，也是理解 Hudi「服务化演进」的关键。",
        ("h3", "三大表格式对比中的 Hudi 定位"),
        "与 Iceberg（纯快照 + 隐藏分区，无内置更新索引）、Delta（日志即表，写路径绑定 Spark/Databricks 生态）相比，Hudi 的差异化在：<strong>内置更新索引</strong>（upsert 的一等公民）、<strong>记录级增量语义</strong>（incremental/CDC 不需要额外 diff 计算）、<strong>表服务一体机</strong>（compaction/clustering/clean/rollback 全内置）。代价是概念复杂度最高——这也是本手册存在的原因。",
    ],
    # 02 Timeline 补充
    [
        ("h3", "instantTime 的并发安全生成"),
        "createNewInstantTime 内部用「上次时间戳 + 1ms 下界」保证单调：如果系统时钟回拨或两次调用间隔过短，会在旧值基础上强制递增，避免出现时间倒流的时间线。多写者场景下 timestamp 由各自客户端生成，冲突由 CH08 的锁与校验裁决——时间戳本身不承担唯一性职责（文件系统层面的原子性才是）。",
        ("h3", "inline compaction 的嵌套记录"),
        "MOR 表开 <code>hoodie.compact.inline=true</code> 后，一次数据提交的末尾可能跟着触发 compaction——此时该 commit 的 metadata 里会记录 <code>compactInstants</code>（本次触发的 compaction instant 列表）。读源码时注意：这使「数据提交」与「表服务提交」在 timeline 上交错出现，增量消费者要按 action 类型过滤而不是按位置。",
        ("h3", "rollback 的并发语义"),
        "rollback 执行器在删除文件前会重新检查目标 instant 的状态：如果并发写者已经在它之上提交了新 instant（lamport 意义上的后继），直接回滚会破坏后继的可见性——此时 rollback 会连同后继一起回滚（级联回滚），或按 <code>hoodie.rollback.style</code> 策略处理。读 <code>RollbackUtils</code> 可以看到完整的回滚计划构建逻辑。",
        ("h3", "Timeline 与 MDT 的关系"),
        "元数据表（MDT）自己也有 timeline（.hoodie 在 _metadata 目录下），主表的每次提交会同步触发 MDT 的一次提交（更新文件列表/bloom/record index 分区）。两者的一致性靠「主表先提交、MDT 同步提交、失败重试」保证；MDT 落后时 Hudi 会按需重建对应分区。理解这种「表中有表」的提交链是读 MDT 相关代码的前提。",
    ],
    # 03 文件布局 补充
    [
        ("h3", "文件大小治理：target size 与小文件"),
        "<code>hoodie.parquet.max.file.size</code>（默认 120MB）与 <code>hoodie.parquet.small.file.limit</code>（默认 104MB）共同决定写入时的新建/追加决策：小于 limit 的文件组被视为「可填充」，insert 优先进它们；超过 max size 的关闭。COW 表靠这个机制在写入时自动控制小文件；MOR 靠 compaction/clustering。",
        ("h3", "FileSlice 的状态：inflight 切片"),
        "FileSystemView 里切片有两种：completed slice（instant 已 completed）与 <strong>inflight slice</strong>（对应 instant 还在 inflight）。默认视图只暴露 completed 切片；compaction 调度器会额外请求 inflight 切片（避免重复调度）。这解释了为什么 FileSystemView 的 API 都带一个 <code>includeInflight</code> 之类的变体。",
        ("h3", "Bootstrap：把存量 Parquet 表变成 Hudi 表"),
        "<code>bootstrap</code> 模块把既有分区目录（海量 Parquet）转换为 Hudi 表而不重写数据：META BOOT（记录原文件与 Hudi fileGroup 的映射）+ DEFAULT BOOT（数据文件原样保留）。之后增量写入正常走 Hudi 路径。这让存量 PB 级表可以零拷贝接入 Hudi——读源码看 <code>HoodieBootstrapHandler</code> 与两种 boot 的 views。",
        ("h3", "HoodieBaseFile / HoodieLogFile 的字段"),
        "两个轻量类承载文件元信息：<code>HoodieBaseFile</code>（path、fileSize、latestCommitTime、versionId）与 <code>HoodieLogFile</code>（path、fileSize、iterator 缓存）。FileSlice 持有 Optional&lt;HoodieBaseFile&gt; 与 List&lt;HoodieLogFile&gt;（按 generation 排序）。这些类的 equals/hashCode 基于 path——视图缓存的正确性依赖它。",
    ],
    # 04 COW 写路径 补充
    [
        ("h3", "Delete 路径：soft 与 hard"),
        "delete 走同一主干：<code>delete()</code> 用 EmptyHoodieRecordPayload 标记删除（soft delete：行还在但 payload 空）或直接物理删除（hard delete：COW 重写时剔除该行，MOR 写 DELETE_BLOCK）。soft delete 保留审计痕迹且 Time Travel 可见；hard delete 等待 clean/vacuum 后物理消失。",
        ("h3", "insert 去重：deduplication"),
        "同一批输入里可能有重复 key：<code>hoodie.combine.before.insert</code>（默认 false）与 <code>hoodie.combine.before.upsert</code>（默认 true）控制是否在写入前按 key 合并。开启后 insert 走 <code>DeduplicationOperator</code>（本地 + 全局两阶段去重），代价是一次额外 shuffle——按业务语义决定，索引层不会帮你去重。",
        ("h3", "错误处理与 WriteStatus 细节"),
        "每条记录的写入结果都进 <code>WriteStatus</code>：成功统计（文件路径、行数、大小、hoodie 元数据列）或失败记录（<code>hoodie.upsert.fail.mode</code>：NONE 忽略错误继续 / GLOBAL 任何失败整体失败）。globalIndex 还会校验「同 key 是否写进了两个分区」。提交后 status 里失败的记录不会出现在任何文件中。",
        ("h3", "与 compaction 的 inline 交互"),
        "COW 表没有 compaction，但 clustering 可以 inline 触发（<code>hoodie.cluster.inline</code>）。clustering 同样是 replacecommit：它把多个小 fileGroup 重写为少量大 fileGroup——与 COW 写路径共用 handle 层，只是输入输出选择策略不同（<code>ClusteringPlanStrategy</code>）。",
    ],
    # 05 MOR 补充
    [
        ("h3", "CompactionPlan 的结构与验证"),
        "plan 是一个 <code>CompactionOperation</code> 列表（fileId、basePath、dataFileBootstrappingPath、deltaFilePaths、metrics）。执行前 <code>CompactionPlanValidator</code> 会校验每个操作的有效性：base 是否还存在、log 是否被回滚、是否已被并发 compaction 消费——避免执行过期计划。这个验证器是「两阶段可恢复」的安全网。",
        ("h3", "Flink 的 compaction 算子"),
        "Flink MOR 表把 compaction 做成流图里的常驻算子：<code>CompactionPlanEventSink</code> 调度、<code>CompactFunction</code> 执行、<code>CompactionCommitSink</code> 提交。算子间用 mini-batch 协调，checkpoint 对齐后保证 compaction 与数据提交的事务一致性。这是「表服务融合进流引擎」的独特实现——Spark 则是独立的批任务。",
        ("h3", "调度策略：UnboundedMerge 与 IO bins"),
        "默认 <code>UnboundedMergeCompactionStrategy</code> 不限制合并的 log 总量（一次合并整个 slice 的全部日志）；<code>BoundedIOCompactionStrategy</code> 按 <code>compaction.target.io</code>（默认 500GB）限制单次合并的 IO，避免单次 compaction 任务过大。选择影响 compaction 频率与读放大的平衡。",
        ("h3", "log compaction 详解"),
        "log compaction（<code>hoodie.log.compaction.block.types</code>，类 <code>HoodieLogCompactor</code>）只合并 log 块不产出 base：把分散在多个 .log 的小块合并成大块，减少读时打开的文件数。适合「写入频繁但查询全走 ReadOptimized」的表——它是 compaction 与 clean 之间的中间态优化。",
    ],
    # 06 索引 补充
    [
        ("h3", "keyGenerator 家族"),
        "索引的前提是 key 的构造：<code>keyGenerator.class</code> 决定如何从输入行生成 HoodieKey（recordKey + partitionPath）。家族包括 Simple/Complex/Timestamp/GlobalDeleted/NonPartitioned/Custom 等，支持嵌套字段、时间戳格式化、多列组合 partition path。key 生成错误是 Hudi 使用事故的高发区——比如 timestamp 类型的 partition path 时区错一天，数据就写进了错误的分区。",
        ("h3", "global index 的一致性语义"),
        "<code>isGlobal=true</code> 的索引保证 key 跨分区唯一：update 一条记录时即使分区路径变了，索引也会定位到旧分区的文件并触发 <strong>分区迁移</strong>（旧分区 remove + 新分区 add）。代价是索引查询不能按分区裁剪。false 时同 key 在不同分区是不同记录——按业务语义选择，选错会导致重复数据。",
        ("h3", "索引 bootstrap 与重建"),
        "存量表开启新索引需要 bootstrap：Bloom 无需（随文件自带）；Record Index 需要全表扫描构建（<code>bootstrap</code> 命令分批写 MDT）；HBase 需要批量导入。构建期间表可以正常读写吗？Record Index 的 bootstrap 支持增量（边写边建）。hudi-cli 提供 <code>metadata bootstrap</code> 系列命令。",
        ("h3", "二级索引（secondary index）"),
        "0.14+ 支持在非主键列上建索引（<code>CREATE INDEX idx ON table(col)</code>），底层是 MDT 的二级分区：按列值 → record 位置。查询命中二级索引时先定位 record keys，再经 Record Index 定位文件。这让 Hudi 具备了点查/过滤场景的列级加速——是「湖上数据库化」的重要一步。",
    ],
    # 07 读路径 补充
    [
        ("h3", "Spark datasource 的读入口"),
        "<code>DefaultSource</code>（format=hu di/hudi）实现 Spark 的 TableProvider：<code>getTable</code> 返回 <code>HoodieSparkTable</code> 的 V2 表（DeltaTableV2 类似的 <code>HoodieInternalV2Table</code>），批次读构建 <code>HoodieFileIndex</code>（对应 Delta 的 file index），流读构建 <code>StreamTable</code>。谓词下推在这一层完成分区与 stats 裁剪。",
        ("h3", "增量查询的实现细节"),
        "Incremental 查询的过滤分两级：timeline 级（哪些 instant 在区间内）与文件级（哪些 FileSlice 含区间内数据）。CDC 模式会额外读取 before 镜像（需要 <code>hoodie.cdc.source=true</code> 时写入前镜像到 log）。拉取的记录带 _hoodie_commit_time 列，消费者可以按位点续读。",
        ("h3", "Flink 流读"),
        "Flink 的 <code>ContinuousFileStoreSource</code> 支持增量流读 MOR/COW：初始全量（bounded）+ 增量 monitor。MOR 流读需要 merge on read（含 compaction 前的 log），由 <code>StreamReadMonitoringFunction</code> 与 <code>StreamReadOperator</code> 实现。checkpoint 对齐后端到端 exactly-once。",
        ("h3", "查询与 MDT 的关系"),
        "查询时 MDT 提供三类加速：① 文件列举（getAllLeafFiles 替代 List）；② column stats（谓词下推的文件级裁剪）；③ bloom（避免读 footer）。开启 MDT 后这些查询加速自动生效——但 MDT 本身的提交与主表是异步的，查询时可能读到稍旧的统计（最终一致）。",
    ],
    # 08 并发 补充
    [
        ("h3", "多写者场景矩阵"),
        "常见组合与可行性：① 两个流写不同分区（同一索引、Snapshot Isolation）→ 支持；② 流 + 批 compaction（不同 instant 类型）→ 支持，compaction 也走锁；③ 两个流写同一 fileGroup → 文件集相交，必冲突，靠 key 分桶规避；④ 跨集群写同一表 → 需要 DynamoDB/ZK 等共享锁 + 对象存储直连。",
        ("h3", "冲突校验的 metadata 细则"),
        "ConflictChecker 除文件集外还校验：<strong>schema 冲突</strong>（并发提交改了 schema → 后者失败，避免列语义漂移）；<strong>tableConfig 冲突</strong>（如同时改索引类型）；<strong>app 级冲突</strong>（自定义 ConflictResolutionStrategy SPI 可插入业务规则，如按管道名互斥）。",
        ("h3", "锁重试与超时治理"),
        "锁获取失败按 <code>hoodie.lock.wait_time_ms</code> / <code>hoodie.lock.max_retry_times</code> 重试；持锁期间写心跳（ZK session / DDB lease 心跳），心跳丢失视为持锁失败，写者必须中止——防止持锁进程假死导致死锁。监控锁的持有时长与重试次数是多写者表运维的必要项。",
        ("h3", "与 Delta/Hudi 并发模型对比"),
        "Delta 的并发基于 LogStore 的条件写（S3 上是 DynamoDB putIfAbsent），冲突判定读日志对比读写集合；Hudi 基于显式 LockProvider + timeline 比对。两者本质都是 OCC，差异在「互斥原语」与「冲突判定的存储位置」。Hudi 的优势是锁服务独立可选；Delta 的优势是无外部依赖（在支持的存储上）。",
    ],
]
