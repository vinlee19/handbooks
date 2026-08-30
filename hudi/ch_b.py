# -*- coding: utf-8 -*-
"""Hudi 手册 05-08 章内容（深度版）。"""
from site_fw import B, A, T, R, FIG

C = "#00e5cc"
CP = "#a78bfa"
CY = "#fbbf24"
CG = "#34d399"
CR = "#fb7185"

CHAPTERS_B = []

# ================ 05 MOR 与 Compaction ================
fig_mor = FIG("hudi-mor", "图 5-1 · MOR 生命周期：deltacommit 追加 → 调度 plan → 执行合并 → 切片轮转 → clean", 1040, 620, (
    T(30, 40, "MOR + COMPACTION · 五个阶段的完整循环", 13, "#8fa5c8", True)
    # 阶段 1：deltacommit
    + R(30, 70, 300, 150, "#0f2438", 10, C)
    + T(50, 98, "① deltacommit（写入瞬间）", 12, C, True)
    + T(50, 124, "update 记录 → 追加到 fileGroup 的 .log", 11.5, "#dbe6f5")
    + T(50, 148, "insert 可选 log-only 或新建 base", 11.5, "#dbe6f5")
    + T(50, 172, "block 达到 max.size 滚动 .log_N", 11.5, "#8fa5c8", mono=True)
    + T(50, 198, "index 可选：canIndexLogFiles", 11, "#6b7d99")
    # 阶段 2：调度
    + R(370, 70, 300, 150, "#121a30", 10, "#31435f")
    + T(390, 98, "② 调度 ScheduleCompaction", 12, "#7fc8e8", True)
    + T(390, 124, "扫描有 log 的 file slice", 11.5, "#dbe6f5")
    + T(390, 148, "CompactionStrategy 打分选片", 11.5, "#dbe6f5")
    + T(390, 172, "生成 CompactionPlan（FileSlice 列表）", 11.5, "#8fa5c8", mono=True)
    + T(390, 198, "落盘 .compaction.requested instant", 11.5, CY, mono=True)
    # 阶段 3：执行
    + R(710, 70, 300, 150, "#2a2010", 10, CY)
    + T(730, 98, "③ 执行 HoodieCompactor", 12, CY, True)
    + T(730, 124, "消费 requested plan（幂等）", 11.5, "#dbe6f5")
    + T(730, 148, "读 base + 全部 log → merge", 11.5, "#dbe6f5")
    + T(730, 172, "payload.merge 按序去重", 11.5, "#8fa5c8", mono=True)
    + T(730, 198, "写出新 base + compaction completed", 11.5, "#8fa5c8", mono=True)
    # 中部箭头
    + A(330, 145, 370, 145, "达到阈值/定时", color="#5f7ba6", dash=True, lx=350, ly=135)
    + A(670, 145, 710, 145, "任何引擎接手", color="#5f7ba6", lx=690, ly=135)
    # 阶段 4：切片轮转（时间线视角）
    + R(30, 280, 980, 160, "#121a30", 10, "#31435f")
    + T(50, 308, "④ FileSlice 轮转（同一 fileGroup 内的版本交替）", 12, "#7fc8e8", True)
    + B(50, 326, 280, 64, "#0e2a20", CG, "slice @ t1（已 compaction）", "base v1", tcolor=CG)
    + B(400, 326, 280, 64, "#241a12", CY, "slice @ t2（MOR 追加中）", "base v2 + log_1..2", tcolor=CY)
    + B(750, 326, 240, 64, "#0e2a20", CG, "slice @ t5（compaction 后）", "base v3 = v2+logs", tcolor=CG)
    + A(330, 358, 400, 358, "deltacommit", color="#5f7ba6", lx=365, ly=346)
    + A(680, 358, 750, 358, "compaction", color="#5f7ba6", lx=715, ly=346)
    + T(50, 416, "Read Optimized 查询只读纯 base 切片（t1/t5）；Snapshot 查询读最新（t2 需实时合并）", 11.5, "#93a5c0")
    # 底部：clean 与参数
    + R(30, 470, 980, 120, "#121a30", 10, "#31435f")
    + T(50, 498, "⑤ Clean：compaction completed 后，旧 log 与被替换 base 不再被最新视图引用", 12, "#7fc8e8", True)
    + T(50, 524, "cleaner.commits.retained 控制保留多少个历史 commit（与 Time Travel 窗口对齐）；hoodie.clean.async 控制是否异步", 11.5, "#dbe6f5")
    + T(50, 550, "inline 模式：hoodie.compact.inline=true 在写入后同步触发；生产推荐独立表服务 + schedule/execute 分离", 11.5, "#8fa5c8")
    + T(50, 574, "触发参数：hoodie.compact.inline.max.delta.commits（默认 5）——MOR 微批节奏的时钟", 11.5, "#6b7d99")
))

CHAPTERS_B.append(dict(
    file="05-mor-compaction.html", title="MOR 写路径与 Compaction：把合并变成异步服务",
    kicker="APACHE HUDI SOURCE STUDY · CH 05",
    sub="MOR 用「追加日志 + 异步合并」换取写入低延迟。compaction 是一个标准的两阶段表服务：调度（schedule）产生 plan 落盘为 requested instant，执行（execute）消费 plan 产出新 base——全程幂等、可独立部署、可换引擎。本章把这两阶段与切片轮转、clean 的联动讲透。",
    stats=[("2 阶段", "schedule / execute 分离"), ("幂等", "plan 落盘崩溃可恢复"), ("异步", "compactor 可异构引擎"), ("5", "默认触发阈值 commits")],
    sections=[
        ("deltacommit：只追加不重写", [
            "MOR 的写入瞬间是 <code>.deltacommit</code>。update 记录不重写 base，而是追加到所属 fileGroup 的 log file（CH03 的 AVRO_DATA_BLOCK）；insert 可选两种落地：log-only（进一步降低延迟，代价是读合并更多）或新建 base（<code>hoodie.datasource.write.operation</code> 配置与 <code>handleEachPartition</code> 策略决定）。",
            "log file 的大小滚动由 <code>hoodie.logfile.data.block.max.size</code> 控制；block 内记录按 commit 分组并带 sequence number，merge 时按序回放保证语义正确。",
        ]),
        ("两阶段 Compaction", [
            ("fig", fig_mor),
            "<strong>调度阶段</strong>：<code>ScheduleCompactionActionExecutor</code> 调用 <code>CompactionUtils.getAllFileSlicesWithLogs</code> 找出有日志的切片，由 <code>CompactionStrategy</code>（默认 <code>UnboundedMergeCompactionStrategy</code>，按 IO 放大过滤）筛选并组装 <code>CompactionPlan</code>——一个 (sliceId, basePath, deltaFilePaths) 的列表。",
            "<strong>执行阶段</strong>：<code>HoodieCompactor</code>（Spark 实现 <code>SparkCompactor</code>）把 plan 转成并行任务，对每个 fileGroup 做 <code>CompactionHandler</code> 合并：读 base → 逐条回放 log → payload.merge 去重 → 写新 base。最后把 instant 从 requested 推到 completed。",
        ]),
        ("为什么两阶段是关键设计", [
            "计划先落盘意味着：① 执行器崩溃后计划仍在，重试不丢工作；② 执行可以换引擎——Spark 调度、Flink 执行完全合法；③ 多个 compactor 可以分片消费同一 plan（fileGroup 粒度去重）。这也是 Flink MOR 表把 compaction 做成常驻算子的基础。",
        ]),
        ("与 Read Optimized 的联动", [
            "compaction completed 之后，最新纯 base 切片前进到 t5——Read Optimized 查询「看到」的数据就此更新。MOR 表的新鲜度 = 最后一次 compaction 时间；对新鲜度敏感的下游应该用 Snapshot Query 或把 compaction 频率调高（代价是 IO 放大）。",
        ]),
        ("Clean：最后一环", [
            "compaction 后，旧 slice 的 log 与 base 失去引用，但 Time Travel / 增量查询可能还要用它们。<code>CleanActionExecutor</code> 按 <code>hoodie.cleaner.commits.retained</code> 保留最近 N 个 commit 的文件，其余删除。保留窗口要 ≥ 下游消费延迟，否则增量消费者会读到「文件已被删」的异常。",
        ]),
    ],
    cards=[
        ("#00e5cc", "两阶段协议", ["schedule：plan 落盘 requested", "execute：任意引擎幂等消费", "崩溃恢复 = 重放 plan"]),
        ("#fbbf24", "参数速查", ["compact.inline.max.delta.commits=5", "cleaner.commits.retained", "logfile.data.block.max.size"]),
        ("#a78bfa", "生产架构", ["独立表服务集群做 compaction", "Timeline Server 集中视图", "clean 与 TT 窗口对齐"]),
    ],
))

# ================ 06 索引 ================
fig_index = FIG("hudi-idx", "图 6-1 · 索引家族全景：tagLocation 的六种实现与两种关键开关", 1040, 620, (
    T(30, 40, "INDEX FAMILY · HoodieIndex 抽象的六个实现", 13, "#8fa5c8", True)
    # 上排三个
    + R(40, 70, 300, 130, "#0f2438", 10, C)
    + T(60, 96, "Bloom Index · SparkHoodieBloomIndex", 12, C, True)
    + T(60, 122, "① 范围裁剪：interval tree 按 key", 10.5, "#8fa5c8")
    + T(60, 142, "② bloom filter（footer 或 MDT）", 10.5, "#8fa5c8", mono=True)
    + T(60, 162, "③ 精确比对（读候选文件 key 列）", 10.5, "#8fa5c8", mono=True)
    + T(60, 182, "④ keyGenerator 决定 key 的构造", 10.5, "#6b7d99")
    + R(370, 70, 300, 130, "#1a1430", 10, CP)
    + T(390, 96, "Bucket Index · HoodieBucketIndex", 12, CP, True)
    + T(390, 122, "hash(record key) → bucket_id", 10.5, "#dbe6f5", mono=True)
    + T(390, 142, "bucket = fileGroup（跳过查找）", 10.5, "#8fa5c8")
    + T(390, 162, "ConsistentHash 支持扩缩容", 10.5, "#8fa5c8")
    + T(390, 182, "要求：主键分布稳定", 10.5, "#6b7d99")
    + R(700, 70, 300, 130, "#0f2a1c", 10, CG)
    + T(720, 96, "Record Index · MDT 自管 KV", 12, CG, True)
    + T(720, 122, "key → location 存进元数据表", 10.5, "#dbe6f5", mono=True)
    + T(720, 142, "读 O(1)：哈希分片 + 本地缓存", 10.5, "#8fa5c8")
    + T(720, 162, "随表自愈：无外部依赖", 10.5, "#8fa5c8")
    + T(720, 182, "0.14+ 推荐的默认演进方向", 10.5, "#6b7d99")
    # 下排三个
    + R(40, 240, 300, 100, "#2a2010", 10, CY)
    + T(60, 264, "HBase Index · 外部 KV", 12, CY, True)
    + T(60, 290, "低延迟点查 · 写放大在 HBase", 10.5, "#8fa5c8")
    + T(60, 310, "rollback 回写撤销记录", 10.5, "#8fa5c8")
    + T(60, 330, "适合高吞吐低延迟 upsert", 10.5, "#6b7d99")
    + R(370, 240, 300, 100, "#121a30", 10, "#31435f")
    + T(390, 264, "Simple Index · 全表 join 比对", 12, "#dbe6f5", True)
    + T(390, 290, "无前置条件 · 朴素全量", 10.5, "#8fa5c8")
    + T(390, 310, "小表 / 一次性修正场景", 10.5, "#6b7d99")
    + R(700, 240, 300, 100, "#121a30", 10, "#31435f")
    + T(720, 264, "InMemory / Java", 12, "#dbe6f5", True)
    + T(720, 290, "单机测试与轻量用法", 10.5, "#8fa5c8")
    + T(720, 310, "与 Simple 同层的轻实现", 10.5, "#8fa5c8")
    # 底部：两个关键开关 + 接口
    + R(30, 400, 980, 190, "#121a30", 10, "#31435f")
    + T(50, 428, "两个决定行为分叉的开关", 12, "#7fc8e8", True)
    + T(50, 454, "canIndexLogFiles：MOR 的 log 记录是否也索引。false（默认）时 update 记录先与 base bloom 比对，log 记录靠 merge 阶段去重；true 时 tagLocation 直接定位 log 位置（Bloom 不支持，Bucket/Record 支持）", 11.5, "#dbe6f5")
    + T(50, 480, "isGlobal：key 是否跨分区唯一。true（GlobalBloom/GlobalSimple）定位不依赖分区值，记录可以「漂移」到其他分区；false 时按记录自带分区直接定位，性能更好", 11.5, "#dbe6f5")
    + T(50, 510, "接口契约（HoodieIndex 抽象类）", 12, "#7fc8e8", True)
    + T(50, 536, "tagLocation(records) → 打上 HoodieRecordLocation{instantTime, fileId}；updateLocation(writestatus) → 提交成功后回写新 key 位置", 11.5, "#dbe6f5", mono=True)
    + T(50, 564, "索引与提交同事务：rollback 时 Bloom 无需处理（随文件消失），HBase/Record Index 必须回写撤销（CH08 并发联动）", 11.5, "#6b7d99")
))

CHAPTERS_B.append(dict(
    file="06-index.html", title="索引体系：record key 如何找到自己的文件组",
    kicker="APACHE HUDI SOURCE STUDY · CH 06",
    sub="索引是 Hudi 更新效率的命门：<code>HoodieIndex.tagLocation()</code> 把每条待写记录映射到它所属的 fileGroup，这个映射的实现决定了写入的延迟与扩展性。六个实现各有清晰的适用边界，两个开关（canIndexLogFiles / isGlobal）决定行为分叉。",
    stats=[("6", "索引实现"), ("2 接口", "tagLocation / updateLocation"), ("MDT", "Record Index 的宿主"), ("0 外部依赖", "Bloom/Bucket/Record")],
    sections=[
        ("接口契约", [
            ("fig", fig_index),
            "<code>HoodieIndex</code> 抽象类只有两个核心方法：<code>tagLocation(HoodieRecordRDD)</code> 给每条记录打上 <code>HoodieRecordLocation</code>（instantTime + fileId，update 语义）；<code>updateLocation(WriteStatus)</code> 在提交成功后回写新增 key。两个配置 <code>canIndexLogFiles</code>（MOR 日志是否索引）与 <code>isGlobal</code>（key 跨分区唯一性）在每个实现里有不同答案。",
        ]),
        ("Bloom Index：为对象存储而生", [
            "默认实现。四步：① <code>bucketRecords</code> 用 interval tree 按 key 范围把记录与候选文件配对（依赖 keyGenerator 生成可比对的 key）；② 并行读每个候选文件的 bloom filter（base file footer 内嵌，或 MDT 托管版本——后者避免为查索引而随机读数据文件）；③ bloom 可能误报，命中的文件再读实际 key 列精确比对（<code>KeyLookupHandle</code> 批处理）；④ 比对命中 → update，未命中 → insert。",
            "代价模型：一次 upsert 的索引成本 ≈ 候选文件数 × bloom 读取。数据按 key 聚得越紧（排序/聚簇），候选越少越快——这就是「写入前排序」对 Hudi 特别重要的原因。",
        ]),
        ("Bucket Index：用布局换查找", [
            "<code>HoodieBucketIndex</code> 彻底跳过「查找」：hash(record key) 决定 bucket（<code>BucketIdentifier.bucketId</code>），bucket 即 fileGroup——写入 O(1)，且天然把同 key 数据聚在一起。代价：bucket 数量建表时固定（<code>hoodie.bucket.index.num.buckets</code>）。<code>ConsistentBucketIndex</code> 用一致性哈希环支持扩缩容，代价是需要额外的迁移元数据。",
        ]),
        ("Record Index：元数据表托管", [
            "0.14+ 的演进方向：key→location 存进 Metadata Table 的 record index 分区，由 Hudi 自管（随表 commit 自愈、随 rollback 撤销）。读取 O(1)（哈希分片 + 执行器本地缓存），无外部依赖，天然支持 MOR 的 log 索引与二级索引（secondary index）构建。开启方式 <code>hoodie.metadata.record.index.enable=true</code> + 一次性 bootstrap。",
        ]),
        ("选型决策树", [
            "外部 KV 可接受 + 超低延迟 → HBase；key 分布稳定 → Bucket（性能最稳）；要跨分区更新 → GlobalBloom/Record Index(globally)；其余 → Bloom 或 Record Index。所有索引都要回答一个问题：<strong>rollback 之后索引如何自愈</strong>——Bloom 随文件消失自动正确，HBase/Record Index 靠回写撤销记录。",
        ]),
    ],
    cards=[
        ("#00e5cc", "六个实现", ["Bloom / Simple / InMemory", "Bucket / ConsistentBucket", "HBase / Record Index(MDT)"]),
        ("#fbbf24", "两个开关", ["canIndexLogFiles：log 是否索引", "isGlobal：跨分区唯一性", "二者组合出行为矩阵"]),
        ("#a78bfa", "性能杠杆", ["key 聚簇减少候选文件", "MDT 托管 bloom 免读 footer", "Record Index O(1) 定位"]),
    ],
))

# ================ 07 读路径 ================
fig_read = FIG("hudi-read", "图 7-1 · 三种查询的切片选择策略：同一 FileSystemView 的三种消费方式", 1040, 600, (
    T(30, 40, "QUERY TYPES · FileSystemView 的三种消费", 13, "#8fa5c8", True)
    # Snapshot
    + R(30, 70, 320, 200, "#0f2438", 10, C)
    + T(50, 98, "Snapshot Query（最新）", 12.5, C, True)
    + T(50, 124, "COW：latest base slice 直读", 11.5, "#dbe6f5")
    + T(50, 148, "MOR：latest slice = base + logs", 11.5, "#dbe6f5")
    + T(50, 172, "log 在 map 端实时 merge", 11, "#8fa5c8")
    + T(50, 196, "Hive: HoodieParquetRealtimeInputFormat", 10.5, "#6b7d99", mono=True)
    + T(50, 216, "Spark: 实时合并迭代器链", 10.5, "#6b7d99", mono=True)
    + T(50, 244, "新鲜度最高，MOR 读延迟波动", 10.5, "#6b7d99")
    # ReadOptimized
    + R(390, 70, 320, 200, "#121a30", 10, "#31435f")
    + T(410, 98, "Read Optimized Query", 12.5, "#7fc8e8", True)
    + T(410, 124, "只读「最近一次 compaction 前」", 11.5, "#dbe6f5")
    + T(410, 148, "的纯 base 切片", 11.5, "#dbe6f5")
    + T(410, 172, "MOR 牺牲新鲜度换稳定延迟", 11, "#8fa5c8")
    + T(410, 196, "COW 下与 Snapshot 等价", 11, "#8fa5c8")
    + T(410, 216, "Hive: HoodieParquetInputFormat", 10.5, "#6b7d99", mono=True)
    + T(410, 244, "延迟曲线平稳，OLAP 友好", 10.5, "#6b7d99")
    # Incremental
    + R(750, 70, 260, 200, "#1a1430", 10, CP)
    + T(770, 98, "Incremental Query", 12.5, CP, True)
    + T(770, 124, "beginInstant / endInstant 区间", 11.5, "#dbe6f5", mono=True)
    + T(770, 148, "输出区间内变更文件与记录", 11.5, "#dbe6f5")
    + T(770, 172, "CDC 模式：前后镜像 + delete", 11.5, "#8fa5c8", mono=True)
    + T(770, 196, "下游物化视图 / 同步管道", 10.5, "#6b7d99")
    + T(770, 220, "timeline 区间即变更集", 10.5, "#6b7d99")
    + T(770, 244, "消费落后过快会遇 clean", 10.5, "#6b7d99")
    # 底部：视图装配细节
    + R(30, 320, 980, 250, "#121a30", 10, "#31435f")
    + T(50, 348, "视图装配的源码细节", 12, "#7fc8e8", True)
    + T(50, 376, "① MetaClient.reloadActiveTimeline() → 取最新 completed instant 作为查询水位", 11.5, "#dbe6f5", mono=True)
    + T(50, 402, "② FileSystemView 按 partition 缓存 FileGroup → 每个 group 选 slice：", 11.5, "#dbe6f5", mono=True)
    + T(66, 426, "Snapshot：getLatestFileSlice()（MOR 返回含 log 的切片，读取时套实时 merge 迭代器）", 11, "#8fa5c8", mono=True)
    + T(66, 450, "ReadOptimized：getLatestFileSliceInRangeBeforeOrOn(lastCompaction)，跳过含 log 的切片", 11, "#8fa5c8", mono=True)
    + T(66, 474, "Incremental：按 commit 元数据过滤出区间内有变更的 fileGroup，输出变更记录", 11, "#8fa5c8", mono=True)
    + T(50, 502, "③ 删除语义：MOR 的 merge 迭代器按 DELETE 块与 payload.isDeleted 过滤；COW 的删除在重写时就已消失", 11.5, "#dbe6f5")
    + T(50, 528, "④ Schema：TableSchemaResolver 从 base/log 头部与 meta action 解析 avro schema，映射引擎类型；schema 演进兼容规则在此收敛", 11.5, "#dbe6f5")
))

CHAPTERS_B.append(dict(
    file="07-read-path.html", title="读路径：Snapshot、Read Optimized 与 Incremental 的视图装配",
    kicker="APACHE HUDI SOURCE STUDY · CH 07",
    sub="同一张表的三种读法，本质是 FileSystemView 对 FileSlice 的三种选择策略。查询引擎通过 InputFormat / Datasource 接入，视图层把「时间线上的某一刻」翻译成「一组可读文件 + 合并迭代器」。",
    stats=[("3 种", "查询类型"), ("5 列", "MetaColumns 元数据"), ("1 个", "TableSchemaResolver"), ("区间", "instant 即增量语义")],
    sections=[
        ("三种查询", [
            ("fig", fig_read),
            "Snapshot 返回「此刻」完整表；Read Optimized 返回「最后完成 compaction 时刻」的表——两者在 COW 上等价，在 MOR 上由 compaction 进度分隔；Incremental 返回 instant 区间的变更集，是增量管道的数据源。",
        ]),
        ("MOR 实时合并的迭代器链", [
            "Snapshot 查询读到含 log 的切片时，读取器构造一条合并迭代器：<code>HoodieMergedFileScanStreamReader</code>（base iterator + 各 log 块 iterator，按 key 归并 + DELETE 过滤 + payload 合并）。这条链运行在 map 端，因此 merge 的代价由查询引擎的算力承担——log 越长首查越慢，这又反哺了 compaction 的调度紧迫性。",
            "Presto/Trino 等 MPP 引擎的实时读由各自的 hudi 插件实现同样语义；不实时合并的场景直接退化为 Read Optimized。",
        ]),
        ("Incremental 与 CDC", [
            "增量查询先从 timeline 取区间 [beginInstant, endInstant] 的 completed commit/deltacommit/replacecommit，取出涉及的 fileGroup，再只读这些切片中属于该区间的记录（利用 MetaColumns 的 _hoodie_commit_time 过滤）。CDC 模式（<code>hoodie.datasource.query.incremental.format=cdc</code>）额外输出 before/after 镜像与删除标记，前提是表开启了 <code>cdc.enabled</code>。",
            "一个容易被忽略的坑：增量消费者的落后程度受 clean 保留窗口约束——被 clean 掉的 slice 无法再输出变更。生产上要把 <code>cleaner.commits.retained</code> 与消费延迟一起治理。",
        ]),
        ("Schema 解析", [
            "<code>TableSchemaResolver</code> 汇集三处 schema 来源：meta action 的 schemaString、base file footer、log 块头，取最新并处理演进兼容（列新增/删除/类型提升规则）。它同时是 Spark / Flink / Presto 类型映射的统一入口。",
        ]),
    ],
    cards=[
        ("#00e5cc", "新鲜度谱系", ["Snapshot：最新（MOR 需 merge）", "ReadOptimized：最后 compaction", "compaction 桥接两者"]),
        ("#a78bfa", "增量语义", ["区间 = instant 对", "CDC 输出前后镜像", "落后消费受 clean 约束"]),
        ("#fbbf24", "实现要点", ["实时合并迭代器链", "MetaColumns 支撑过滤", "TableSchemaResolver 统一映射"]),
    ],
))

# ================ 08 并发控制 ================
fig_cc = FIG("hudi-cc", "图 8-1 · 提交协议时序：取锁 → 校验 → 提交 的临界区，以及两种失败路径", 1040, 620, (
    T(30, 40, "CONCURRENCY · OCC COMMIT PROTOCOL", 13, "#8fa5c8", True)
    # Writer A 时序
    + R(30, 70, 300, 170, "#121a30", 10, "#31435f")
    + T(50, 98, "Writer A（流式管道）", 12, "#7fc8e8", True)
    + T(50, 124, "写完成：WriteStatus 汇总", 11.5, "#dbe6f5")
    + T(50, 148, "t=A1 产生 instant（inflight）", 11.5, "#8fa5c8", mono=True)
    + T(50, 172, "写数据文件（带 marker）", 11.5, "#8fa5c8")
    + T(50, 200, "准备提交：文件集 = {fg-1, fg-3}", 11.5, "#8fa5c8")
    # Writer B
    + R(30, 270, 300, 130, "#121a30", 10, "#31435f")
    + T(50, 298, "Writer B（批处理作业）", 12, "#7fc8e8", True)
    + T(50, 324, "t=B1 instant，文件集 = {fg-5}", 11.5, "#8fa5c8", mono=True)
    + T(50, 348, "与 A 无交集 → 可同时提交", 11.5, CG, mono=True)
    + T(50, 372, "Snapshot Isolation 默认语义", 11, "#6b7d99")
    # 临界区
    + R(400, 100, 260, 74, "#2a2010", 10, CY)
    + T(420, 126, "TransactionManager · begin() 取锁", 12, CY, True)
    + T(420, 158, "Zookeeper / DynamoDB / FS / SQL", 11, "#8fa5c8", mono=True)
    + R(400, 240, 260, 74, "#0f2438", 10, C)
    + T(420, 266, "ConflictChecker · 文件集比对", 12, C, True)
    + T(420, 298, "SimpleConcurrentFileWrites…", 11, "#8fa5c8", mono=True)
    + R(400, 380, 260, 74, "#121a30", 10, "#31435f")
    + T(420, 404, "早期冲突检测", 12, "#dbe6f5", True)
    + T(420, 428, "写入过程中周期校验", 10.5, "#8fa5c8")
    + T(420, 452, "hoodie.write.concurrency.…", 10.5, "#8fa5c8", mono=True)
    # 结果
    + R(760, 120, 240, 100, "#0f2a1c", 10, CG)
    + T(780, 146, "通过 → 提交", 12, CG, True)
    + T(780, 170, "completed 原子重命名", 10.5, "#dbe6f5", mono=True)
    + T(780, 194, "锁释放 → 时间线前进", 10.5, "#8fa5c8")
    + R(760, 260, 240, 100, "#2a1414", 10, CR)
    + T(780, 286, "冲突 → 失败", 12, CR, True)
    + T(780, 310, "HoodieWriteConflictException", 10.5, "#dbe6f5", mono=True)
    + T(780, 334, "调用方决定重试或告警", 10.5, "#8fa5c8")
    # 箭头
    + A(330, 145, 400, 145, "", color="#5f7ba6")
    + A(530, 200, 530, 240, "", color="#5f7ba6")
    + A(660, 145, 760, 155, "无冲突", color="#5f7ba6", lx=710, ly=135)
    + A(660, 285, 760, 300, "相交", color="#fb7185", dash=True, lx=710, ly=275)
    # 底部横条
    + R(30, 480, 980, 110, "#121a30", 10, "#31435f")
    + T(50, 508, "隔离级别与边界", 12, "#7fc8e8", True)
    + T(50, 534, "默认 Snapshot Isolation：并发提交只要文件集不相交即可同时成功；Repeatable Read / Serializable 需要额外读取冲突校验", 11.5, "#dbe6f5")
    + T(50, 560, "ACID 边界是单表：跨表事务需外部协调；元数据表（MDT）自身也是 Hudi 表，其提交复用同一协议", 11.5, "#8fa5c8")
))

CHAPTERS_B.append(dict(
    file="08-concurrency.html", title="并发控制与 ACID：锁、冲突校验与时间线原子性",
    kicker="APACHE HUDI SOURCE STUDY · CH 08",
    sub="Hudi 的 ACID 建立在三件事上：timeline 文件的原子重命名（真相）、可插拔的 LockProvider（互斥）、提交前的 <strong>OCC 冲突校验</strong>（正确性）。默认 Snapshot Isolation 允许不同 fileGroup 并行写，冲突只在文件集相交时发生。",
    stats=[("OCC", "提交时校验"), ("Snapshot", "默认隔离级别"), ("4+", "LockProvider 实现"), ("单表", "ACID 边界")],
    sections=[
        ("提交协议的临界区", [
            ("fig", fig_cc),
            "临界区很短：取锁 → <code>ConflictChecker.hasConflict()</code> → 写 completed instant → 放锁。数据写入本身在临界区之外——这正是乐观并发的意义：锁的争用只发生在提交瞬间。",
            "校验逻辑（<code>SimpleConcurrentFileWritesConflictResolutionStrategy</code>）：拿自己成功的文件集，与 timeline 上所有「并发未完成/已完成」instant 的文件集求交集；相交 → <code>HoodieWriteConflictException</code>。metadata 变更（schema）与表服务 instant 有专门的比对规则。",
        ]),
        ("隔离级别", [
            "默认 <strong>Snapshot Isolation</strong>：只校验写写文件集冲突，允许「A 读的文件被 B 改写」这类可串行化理论上的异常（对湖仓场景通常无害）。开 <code>hoodie.write.concurrency.mode=optimistic_transaction_control</code> 后可选 Repeatable Read / Serializable：提交时会检查「本事务读过的文件是否被并发提交修改」。",
            "<strong>早期冲突检测</strong>（early conflict detection）让写客户端在写入过程中周期性比对并发 timeline，尽早失败、节省算力——长任务对撞时收益明显。",
        ]),
        ("锁提供者与恢复", [
            "<code>LockProvider</code> 接口的实现：<code>ZookeeperBasedLockProvider</code>、<code>DynamoDBBasedLockProvider</code>（AWS 官方推荐，含条件写自旋）、<code>FileSystemBasedLockProvider</code>（HDFS 原子 rename）、存储 SQL 锁。锁配置（路径/表/重试）全部在 <code>HoodieLockConfig</code>。",
            "锁过期后的正确性由 timeline 兜底：即使锁服务失灵导致两个写者同时进入临界区，completed 文件的重命名仍只允许一个成功（存储层原子性），另一个会发现目标 instant 已存在而失败。",
        ]),
        ("元数据表与外部索引的并发", [
            "MDT 自身是一张 Hudi 表：主表提交时同步提交 MDT（文件清单、bloom、record index 的更新），复用同一套锁与冲突校验。HBase / Record Index 等索引在 rollback 时回写撤销记录——因此「索引与数据最终一致」由协议保证，而非碰运气。",
        ]),
    ],
    cards=[
        ("#00e5cc", "锁提供者", ["Zookeeper / DynamoDB / FS", "SQL 锁与自定义 SPI", "配置在 HoodieLockConfig"]),
        ("#fb7185", "冲突场景", ["同 fileGroup 并发 upsert", "clustering 与写入相交", "schema 演进竞争"]),
        ("#a78bfa", "最佳实践", ["流批写不同分区/表", "开早期冲突检测省算力", "锁监控 + 超时治理"]),
    ],
))
