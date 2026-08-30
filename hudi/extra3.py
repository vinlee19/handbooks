# -*- coding: utf-8 -*-
"""Hudi 手册第三轮补充。"""
EXTRA3 = [
    # 01
    [],
    # 02
    [],
    # 03
    [
        ("h3", "Table Format v6 的文件名与布局"),
        "v6 扁平化布局下，base/log 文件直接放在分区目录（甚至表根）下，文件名格式扩展为带 instantTime 前缀：{instantTime}-{fileId}-{writeToken}-{bucket}.parquet。目录层级从「分区/文件组/文件」退化为「分区/文件」，List 一次即可见全部文件。视图层按文件名重建 FileGroup。这是 Hudi 为超大规模分区（十万级 fileGroup）做的布局优化。",
        ("h3", "Log 块的 schema 演进处理"),
        "log 块头携带写入时的 avro schema：读时若 base 与 log 的 schema 不一致，由 InternalSchemaUtils 做 schema evolution 对齐（列加改删、类型提升）。这是 MOR 表改 schema 后旧日志仍可读的机制——也是 InternalSchema（v0.11+）模块存在的意义。",
        ("h3", "分区与桶的双层组织"),
        "Bucket Index 表的布局是「分区/bucketId/fileGroup」三层：bucket 是物理固定分区（哈希预分配），fileGroup 在 bucket 内演进。这让 upsert 的定位变成两级常量计算（分区→bucket→fileGroup），彻底消灭索引查找。代价是 bucket 内数据倾斜需要 re-bucket（clustering 的 bucket split/merge）。",
    ],
    # 04
    [
        ("h3", "EmptyHoodieRecordPayload 与 soft delete"),
        "soft delete 用 EmptyHoodieRecordPayload 写一条空记录：读取 merge 时该 key 输出 null（对下游等于删除），但 Time Travel 与审计仍能看到完整历史。hard delete 则让记录从最新视图中消失。两者在 log 中都是 DELETE 块或空 payload 记录，区别只在 merge 语义。",
        ("h3", "commit 的原子性来源总结"),
        "COW 提交的原子性链条：① 每个数据文件的写出是原子的（完整文件才可见）；② marker 校验排除半成品；③ completed instant 的重命名是原子的；④ 冲突校验在重命名前完成。四层防线叠加，使「读到不一致」需要同时突破四层——概率意义上的不可能。",
        ("h3", "Spark 3 的 vectorized 写入"),
        "Spark 3.2+ 的 data source writer V2 接口让 Hudi 走 vectorized 路径：HoodieBulkInsertDataInternalWriter 直接消费 Arrow ColumnarBatch，避免行转换。Bulk Insert 与 insert into 在 Spark 3 上自动选择该路径，写入吞吐提升 30-50%。",
    ],
    # 05
    [
        ("h3", "CompactionPlan 的调度触发链"),
        "MOR 表每次 deltacommit 后检查：距上次 compaction 计划的 deltacommit 数是否达到 hoodie.compact.inline.max.delta.commits；达到则 schedule（生成 requested instant）。async 模式下由独立的 ScheduleCompactionJob 定时调度。plan 一旦存在，执行者（任何引擎/进程）可以在任意时间消费——调度与执行的时间解耦。",
        ("h3", "Flink Compaction 的 checkpoint 对齐"),
        "Flink MOR 表的 compaction 算子嵌入流图后，与数据写入共享 checkpoint barrier：compaction 的提交必须在对齐的 barrier 内完成，否则会阻塞 checkpoint。这保证了「compaction 产出的新 base 与数据提交的顺序」在 Flink 语义下一致。参数 task.cpus 与 compaction 并发度的平衡是 Flink MOR 调优的核心。",
        ("h3", "MOR 的读合并成本量化"),
        "Snapshot 读的合并成本 ≈ base 行数 + log 行数的归并 + DELETE 块的过滤。log 与 base 的比例（log/base ratio）是核心指标：超过 3-5 倍时读延迟显著上升，应立即 compaction。生产上用 hudi-cli 的 stats 命令或 metrics 监控该比率。",
    ],
    # 06
    [
        ("h3", "Record Index 的分区与分片"),
        "Record Index 在 MDT 内按 hash(record key) 分成固定分区（默认按文件数分桶），每个分区内按 key 排序存储。读取时：hash → 定位分区 → 二分查找。写入时：随主表提交同步更新（upsert 到 MDT 的 record index 分区）。分片数在 bootstrap 时确定，扩容需要重建。",
        ("h3", "Bucket Index 与 COW/MOR 的组合"),
        "Bucket Index + MOR 是流式 upsert 的黄金组合：写入 O(1) 定位 + 追加 log（低延迟），compaction 异步合并。Bucket Index + COW 则是高频覆盖写场景的最优解（如用户画像宽表每日全量按 key 更新）。两者都要求 bucket 数预分配——这是它与传统索引最大的心智差异。",
        ("h3", "索引失效与重建的场景"),
        "索引失效的触发：key 列类型变更、分区分裂/合并、MDT 损坏、HBase 表重建。重建方式：Bloom 随 compaction 自然恢复；Record Index 走 bootstrap（全量）；HBase 需要批量导入工具。监控指标：索引命中率、MDT 延迟、bloom 误报率——三者异常即索引需要关注。",
    ],
    # 07
    [
        ("h3", "Time Travel 查询的实现"),
        "Time Travel（versionAsOf/timestampAsOf）的本质：FileSystemView 从「目标 instant」重建而非最新 instant。旧的 base/log 文件必须在 clean 保留窗口内（否则文件已被物理删除）。Hudi 的 clean 保留策略因此也是 Time Travel 的窗口策略——两者共用配置族。",
        ("h3", "查询下推与 MDT stats"),
        "MDT 的 column stats 分区按「列 → 分区 → 文件」三级组织，存储每个文件每列的 min/max/nullCount/总行数。查询时 Spark 的 stats 规则读取这些统计并构造 per-file 谓词，交给 FileSystemView 过滤。效果：WHERE price > 100 这类谓词在文件枚举阶段就裁剪掉 90% 的文件。",
        ("h3", "HoodieFileIndex 与 Spark 计划融合"),
        "Spark 3 的 V2 表接口让 Hudi 能把文件裁剪直接注入 Spark 的 BatchScanExec：HoodieFileIndex.listFilesAndPartitions 返回裁剪后的文件分区列表，Spark 的 file source scan 直接消费。这避免了旧版 InputFormat 的行级过滤开销——是 Spark 3 集成性能提升的主要来源。",
    ],
    # 08
    [
        ("h3", "多写者的生产架构模式"),
        "模式一：按分区/管道分表（最强的隔离）。模式二：同表多写者 + 锁服务（需要 ConflictChecker 兜底）。模式三：Timeline Server 集中提交（所有写者通过 RPC 提交，Server 内部串行化——彻底避免冲突但 Server 是单点）。生产按数据管道的独立性选择。",
        ("h3", "锁服务的高可用与降级"),
        "锁服务不可用时写者全部失败——这是故意的（fail-safe）。DynamoDB 锁支持条件写自旋重试；ZK 锁依赖 session 存活。降级策略：切到 FileSystem 锁（如果表在 HDFS）或等待锁服务恢复。绝不能在锁不可用时绕过锁提交——那会破坏 OCC 的前提。",
        ("h3", "与 Delta 并发模型的对比"),
        "Delta 靠 LogStore 的「条件写」实现互斥（S3 上是 DynamoDB 条件写或 Azure 的 etag），冲突判定读日志对比；Hudi 靠显式 LockProvider + timeline 比对。两者本质都是 OCC，但 Delta 的互斥原语内嵌在存储适配层，Hudi 的互斥原语是独立可选的服务——哲学差异决定了各自的运维形态。",
    ],
]
