# -*- coding: utf-8 -*-
"""Hudi 手册每章追加的第二轮深度小节。"""

EXTRA2 = [
    # 01 总体架构
    [
        ("h3", "一次 INSERT 的端到端旅程（快速预览）"),
        "以 COW 表的 <code>spark.write.format(\"hudi\").mode(\"append\")</code> 为例：① DefaultSource 构建 HoodieInternalV2Table → ② WriteIntoHoodieTable 命令 → ③ HoodieSparkSession.createHoodieWriteClient（含 MetaClient 加载、索引初始化、锁管理器）→ ④ tagLocation 打标 → ⑤ WorkloadProfile + UpsertPartitioner → ⑥ 各分区任务写 parquet（marker 先行）→ ⑦ WriteStatus 收集 → ⑧ 提交协议。后续章节就是这条链的逐站放大。",
        ("h3", "多模态写入：precombined validator"),
        "输入流可能自带重复 key（CDC 上下游重试），<code>hoodie.combine.before.upsert=true</code> 时 Hudi 在写入前按 key 做 preCombine（用 payload 的 combineVal 比较保留最新）。preCombine 的比较函数由 payload 决定（DefaultHoodieRecordPayload 按 ordering field 比较）——这也是「ordering field 设错导致数据回退」事故的根源。",
        ("h3", "Hudi 的失败模式总览"),
        "写失败的三类：① 提交前失败（数据写了一半）→ marker 检测 + rollback 清理；② 提交临界区失败（锁丢失/冲突）→ inflight 残留由后续写者 rollback；③ 提交后失败（post-commit hook 如 MDT 同步失败）→ 表数据正确但索引滞后，MDT 按需重建。三类失败都不需要人工介入数据修复——这是「timeline 即真相」的直接收益。",
    ],
    # 02 Timeline
    [
        ("h3", "rollback instant 的内容解剖"),
        "rollback 的 metadata（HoodieRollbackMetadata）包含：rollbackInstant（被回滚的目标）、commitsToRollback 列表、partitionToRollbackStats（每个分区删除了哪些文件、删除的字节数）。它让「表曾经回滚过什么」完全可查——hudi-cli 的 <code>commits show_rollback</code> 系列命令直接消费它。",
        ("h3", "savepoint：时间线的锚点"),
        "savepoint action 把某个 instant 标记为「受保护点」：clean 服务不会删除 savepoint 引用的文件（即使超出保留窗口）。它是 Time Travel 的手动锚点——重大变更前打一个 savepoint，出错可无条件恢复。savepoint 的删除也有对应 instant（被审计记录）。",
        ("h3", "timeline 与多表的联动顺序"),
        "主表提交成功后按序触发：MDT 同步提交 → index 回写 → inline 表服务 → archival 检查。任一环节失败不影响主表数据正确性（post-commit 阶段失败可重试）。读 BaseHoodieTableServiceClient 的 runTableServicesInline() 可以看到完整的调度顺序与条件判断。",
        ("h3", "timeline 的存储成本"),
        "每个 instant 文件只有 KB 级，但高频写入（每秒一次）一年就是 3000 万个小文件——archival 之前 List 会慢到不可用。MDT 的文件列表分区正是为此：active timeline 的 List 被 MDT 查询替代，扫描成本从 O(文件数) 降为 O(分区数)。",
    ],
    # 03 文件布局
    [
        ("h3", "base file 的文件名解析规则"),
        "COW base：{fileId}-{writeToken}-{instantTime}.parquet（如 fg-uuid-0-20240115103000000.parquet）；MOR base 同格式；log：.log_{generation}_{writeToken}_{instantTime}.log。writeToken 是同一写者同一文件在同一次提交内的原子序号（防并发写同文件）。解析逻辑在 <code>FSUtils.getCommitTime / getFileId</code>——正则严格，文件名被人工改动会直接导致 MetaClient 初始化失败。",
        ("h3", "文件大小与布局策略的演进"),
        "老版本靠 <code>hoodie.parquet.small.file.limit</code> 在写入时「填充」小文件；新版本推荐 <strong>clustering</strong>（异步重排，支持按列排序 z-order/linear）+ <code>hoodie.layout.optimize.strategy</code>。布局治理从「写入时顺带」演进为「独立表服务」，这与 compaction 的演进路径一致。",
        ("h3", "与 Hive 式目录的兼容"),
        "Hudi 的分区目录名遵循 Hive 约定（partition_col=value），使 Hive/Presto 的原生分区发现可用。非 Hive 风格分区（URL encode 与否）由 <code>hoodie.datasource.write.keygenerator.class</code> 与 <code>hoodie.datasource.hive_sync.*</code> 同步控制——分区路径的编码不一致是查询引擎读不到数据的常见原因。",
    ],
    # 04 COW 写路径
    [
        ("h3", "HoodieMergeHandle 的合并语义"),
        "MergeHandle 打开旧 base file 的读取迭代器与内存中的更新记录（按 key 索引），逐行推进：旧 key 在更新集 → 输出 payload.merge 后的新值；不在 → 原样输出（数据不会丢）；更新集中未被消费的记录（新 insert）→ 追加输出。这个「三指针归并」就是 COW 更新的核心算法——源码在 <code>HoodieMergeHandle.write()</code>。",
        ("h3", "文件级原子性：writeToken 与幂等"),
        "同一次提交内，同一 fileId 可能由多个 task 写（重试），writeToken 保证文件名唯一。WriteStatus 的统计在 Driver 端去重合并。task 重试时 marker 机制保证旧的部分文件不会被提交——重试产出的是新文件名。",
        ("h3", "配置联动：写入路径的常用参数组"),
        "一组常用的 COW 调参组合：<code>hoodie.upsert.shuffle.parallelism</code>=2×分区数、<code>hoodie.parquet.small.file.limit</code>=100MB、<code>hoodie.copyonwrite.insert.split.size</code>=500000、<code>hoodie.combine.before.upsert</code>=true。每个参数的变更都会影响 CH04 流程中的某一站——调优就是沿着这条链找瓶颈。",
    ],
    # 05 MOR 补充
    [
        ("h3", "MOR 的 insert 两种落地对比"),
        "log-only insert：记录进 log block，写入最快，但 compaction 前该 fileGroup 无 base（纯 log slice），读取必须实时合并。base insert：走 CreateHandle 新建小 base，读取较快但有小文件问题。<code>hoodie.datasource.write.record.merge.mode</code>（v0.14+ 的统一合并模式配置）与索引类型共同决定默认行为。",
        ("h3", "compaction 的调度时机：inline vs async vs 独立"),
        "inline（写入进程内、提交后同步执行）：简单但影响写入延迟；async（写入进程内异步线程）：不阻塞提交但共享资源；独立部署（表服务集群 / Flink compaction 算子）：完全解耦，生产推荐。schedule 与 execute 也分离：<code>hoodie.compact.schedule.inline</code> 只调度不执行，执行交给独立服务消费 requested plan。",
        ("h3", "compaction 与 clustering 的协同"),
        "MOR 表的 compaction 解决「log → base」，clustering 解决「小 base → 大 base + 按列重排」。两者都产出 replacecommit（clustering）或 compaction（MOR），执行顺序有约束：先 compaction 后 clustering（避免对含 log 的 slice 重排）。<code>HoodieTableServiceManager</code> 会自动编排这个顺序。",
    ],
    # 06 索引补充
    [
        ("h3", "Bucket Index 的扩容：consistent hash",
        "数据增长后 bucket 数需要扩容。<code>ConsistentBucketIndex</code> 维护哈希环的元数据（bucket 到节点的映射表，存在 MDT），扩容时按「最大 bucket 优先分裂」策略拆分，新旧映射在过渡期并存——写入按新映射，读取兼容旧映射，直到 clustering 完成数据迁移。读源码看 <code>ConsistentBucketStateIdentifier</code>。"),
        ("h3", "索引与 schema 演进"),
        "加列/改列类型会影响索引：Bloom 按 key 列构建（key 列类型变化需重写全部文件）；Record Index 与 key 列类型解耦（存的是序列化后的 key）；二级索引列被删除时索引自动失效。schema 演进的兼容性检查（TableSchemaResolver）会在写入时拦截不兼容变更。",
        ("h3", "索引的开销实测视角"),
        "以 1TB 表、10 亿行、COW 为例：Bloom Index 每次 upsert 需读约 100-1000 个文件的 bloom（每个 64KB-1MB），总 IO 约 0.5-2GB；Bucket Index 零 IO（纯计算）；Record Index 约 10 万次 MDT 点查（本地缓存后大幅减少）。写入延迟从数十秒降到亚秒——这就是「索引决定写入扩展性」的量化含义。",
    ],
    # 07 读路径补充
    [
        ("h3", "谓词下推的三级裁剪"),
        "查询的文件裁剪分三级：① 分区裁剪（partition path 精确匹配）；② stats 裁剪（MDT column stats 或 base file footer 的 min/max）；③ bloom 裁剪（key 点查）。三级依次递减候选文件数。MDT 的 column stats 分区按「列名+分区」组织，查询时只读相关列的统计页——这是 MDT 让查询「免 List、免全扫」的核心。",
        ("h3", "快照查询的隔离语义"),
        "查询启动时绑定一个 completed instant（快照水位），之后即使有新提交也不影响本次查询的一致性——这是「快照隔离的读」。长查询的风险是水位切片被 clean 删除：需要 <code>hoodie.cleaner.commits.retained</code> ≥ 查询时长对应的 commit 数，或对长查询开启 <code>hoodie.datasource.read.slice.begin</code> 固定版本。",
        ("h3", "Trino/Presto 的接入细节"),
        "Trino 的 hudi 连接器基于 hudi-hadoop-mr 的 InputFormat 封装：SplitManager 从 FileSystemView 拿文件分片，MOR 实时读通过 HoodieRealtimeRecordCursor 合并 log。谓词下推受限于 InputFormat 的能力——stats 裁剪在 Trino 侧通过 column stats 同步（run sync tool）到 Hive metastore 实现。",
    ],
    # 08 并发补充
    [
        ("h3", "Timeline Server 的并发角色"),
        "Timeline Server 不只缓存视图：它还是 marker 的集中管理者（executors 通过 RPC 创建/检查 marker，写放大从 O(task×file) 降为 O(1) RPC）与 writer 的互斥协调点。嵌入式模式（Driver 内嵌）适合中小集群；独立部署支持多集群共享视图。它是 Hudi 从「库」走向「服务」的架构分水岭。",
        ("h3", "冲突校验的性能成本"),
        "ConflictChecker 的成本 = 并发 instant 数 × 比对文件数。高并发（数十个写者）时建议：① 缩小写者粒度（按分区拆表/分桶）；② 开 early conflict detection（写一半就失败，不等提交）；③ 升级到 Record Index + Bucket 组合减少文件集大小。",
        ("h3", "故障演练：三写者两两相交"),
        "极端场景：A/B/C 同时提交且文件集两两相交——只有一个能赢，另外两个收到异常后必须重新读取新 snapshot 重算（或放弃）。Hudi 不自动合并冲突的写入（不像 git merge）：数据一致性由调用方负责重放。这就是为什么流管道通常按 key 分区写、避免 fileGroup 相交的设计纪律。",
    ],
]
