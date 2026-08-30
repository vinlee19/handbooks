# -*- coding: utf-8 -*-
"""Hudi 手册 05-08 章内容。"""
from site_fw import B, A, T, R, FIG

C = "#00e5cc"
CP = "#a78bfa"
CY = "#fbbf24"
CG = "#34d399"
CR = "#fb7185"

CHAPTERS_B = []

# ---------------- 05 MOR 与 Compaction ----------------
fig_mor = FIG("hudi-mor", "图 5-1 · MOR 写入与 Compaction：deltacommit 追加日志，compaction 异步合成新 base", 1040, 520, (
    T(30, 38, "MOR + COMPACTION · 写读分离的代价交换", 13, "#8fa5c8", True)
    + B(40, 90, 220, 90, "#0f2438", C, "deltacommit", "只写 log，秒级返回", tcolor=C)
    + T(60, 148, "日志块按大小滚动成 .log_1/.log_2", 11, "#8fa5c8")
    + B(40, 220, 220, 90, "#121a30", "#31435f", "调度：ScheduleCompaction", "生成 compaction plan", )
    + T(60, 278, "plan 写入 .compaction.requested", 11, "#8fa5c8")
    + B(400, 90, 240, 110, "#2a2010", CY, "Compaction 执行", "BaseCompactor", tcolor=CY)
    + T(420, 140, "读 base + 全部 log", 11.5, "#8fa5c8")
    + T(420, 160, "payload.merge 合并重复 key", 11.5, "#8fa5c8")
    + T(420, 180, "产出新 base file", 11.5, "#8fa5c8")
    + B(400, 240, 240, 90, "#121a30", "#31435f", "FileSlice 轮转", "新切片替换旧切片")
    + T(420, 298, "旧 log 归 clean 服务回收", 11, "#8fa5c8")
    + B(760, 90, 240, 110, "#0f2a1c", CG, "读路径变纯", "Snapshot 读只碰 base", tcolor=CG)
    + T(780, 148, "ReadOptimized 读旧 slice", 11.5, "#8fa5c8")
    + B(760, 240, 240, 90, "#121a30", "#31435f", "调度策略", "CompactionStrategy")
    + T(780, 298, "选 slice：IO 放大 vs 延迟", 11, "#8fa5c8")
    + A(260, 135, 400, 135, "异步/inline 触发", color="#5f7ba6", dash=True)
    + A(520, 130, 520, 240, "写新 base", color="#5f7ba6")
    + A(640, 135, 760, 135, "", color="#5f7ba6")
    + A(520, 310, 760, 285, "instant: compaction completed", color="#5f7ba6", dash=True, lx=690)
))

CHAPTERS_B.append(dict(
    file="05-mor-compaction.html", title="MOR 写路径与 Compaction：把合并变成异步服务",
    kicker="APACHE HUDI SOURCE STUDY · CH 05",
    sub="MOR 用「追加日志 + 异步合并」换取写入低延迟。compaction 是一个标准的表服务：先在 timeline 上调度一个 plan（requested），再由执行器消费（inflight → completed），全程可独立部署、可重试。",
    stats=[("2 阶段", "调度与执行分离"), ("8-32MB", "log 块滚动阈值"), ("payload.merge", "去重合并语义"), ("独立部署", "compactor 可异构引擎")],
    sections=[
        ("deltacommit：只追加", [
            ("fig", fig_mor),
            "MOR 的写入瞬间是 <code>.deltacommit</code>：update 记录追加到既有 fileGroup 的 log file，insert 可走 log（log-only）或新 base。日志块类型仍由 CH03 的 <code>HoodieLogBlock</code> 家族承担。",
        ]),
        ("Compaction：调度与执行分离", [
            "<strong>调度</strong>（<code>ScheduleCompactionActionExecutor</code>）扫描所有带 log 的 file slice，按 <code>CompactionStrategy</code>（默认 <code>UnboundedMergeCompactionStrategy</code>）挑出要合并的 slice，生成 <code>CompactionPlan</code> 写成 <code>.compaction.requested</code> instant。",
            "<strong>执行</strong>（<code>HoodieCompactor</code> / <code>BaseCompactor</code>）消费 requested 计划：对每个 (base, logs) 对做 merge，产出新 base，最后把 instant 推到 completed。因为计划先落盘，执行者可以是任何引擎（Spark/Flink/独立进程），崩溃后重放即恢复。",
        ]),
        ("调参要点", [
            "compaction 触发频率：<code>hoodie.compact.inline</code> + <code>hoodie.compact.inline.max.delta.commits</code>；并发上限与并行度由 plan 的 shuffle 参数控制。clean 服务随后回收被替换 slice 的旧文件（受 <code>hoodie.cleaner.commits.retained</code> 约束，与 Time Travel 窗口联动）。",
        ]),
    ],
    cards=[
        ("#00e5cc", "调度器", ["CompactionStrategy 选 slice", "plan = requested instant", "可 inline 也可独立服务"]),
        ("#fbbf24", "执行器", ["BaseCompactor 消费 plan", "base+log → 新 base", "崩溃后重放 plan 即恢复"]),
        ("#a78bfa", "代价交换", ["写延迟低（只追加）", "读延迟高（merge on read）", "compaction 后读路径变纯"]),
    ],
))

# ---------------- 06 索引 ----------------
fig_index = FIG("hudi-index", "图 6-1 · 索引家族：把 record key 映射到 fileGroup 的不同实现", 1040, 500, (
    T(30, 38, "INDEX FAMILY · tagLocation: key → fileId", 13, "#8fa5c8", True)
    + B(40, 90, 280, 100, "#0f2438", C, "Bloom Index", "SparkHoodieBloomIndex", tcolor=C)
    + T(60, 148, "base file bloom header + 全文件比对兜底", 11, "#8fa5c8")
    + T(60, 168, "对象存储友好：可借 MDT 加速", 11, "#8fa5c8")
    + B(380, 90, 280, 100, "#121a30", "#31435f", "Simple Index", "全表 join 比对")
    + T(400, 148, "小表 / 无索引依赖的朴素方案", 11, "#8fa5c8")
    + B(720, 90, 280, 100, "#1a1430", CP, "Bucket Index", "hash(record key) → bucket", tcolor=CP)
    + T(740, 148, "Consistent Hash 支持扩缩 bucket", 11, "#8fa5c8")
    + B(40, 240, 280, 100, "#2a2010", CY, "HBase Index", "外部 KV：key → fileId", tcolor=CY)
    + T(60, 298, "低延迟点查 · 引入外部依赖", 11, "#8fa5c8")
    + B(380, 240, 280, 100, "#0f2a1c", CG, "Record Index (MDT)", "Hudi 自管的 KV 索引表", tcolor=CG)
    + T(400, 298, "元数据表内 · 支持二级定位", 11, "#8fa5c8")
    + B(720, 240, 280, 100, "#121a30", "#31435f", "InMemory / Java", "测试与轻量场景")
    + T(740, 298, "lookupIndex / tagLocation 接口", 11, "#8fa5c8")
    + R(40, 380, 960, 80, "#0c1322", 10, "#31435f")
    + T(60, 408, "接口：HoodieIndex.tagLocation(records) → 带 location 的 records；updateLocation 回写新增 key", 12, "#93a5c0")
    + T(60, 434, "canIndexLogFiles 决定 MOR 是否索引 log 记录；isGlobal 决定跨分区唯一性", 12, "#6b7d99")
))

CHAPTERS_B.append(dict(
    file="06-index.html", title="索引体系：record key 如何找到自己的文件组",
    kicker="APACHE HUDI SOURCE STUDY · CH 06",
    sub="索引是 Hudi 更新效率的命门：<code>HoodieIndex.tagLocation()</code> 把每条待写记录映射到它所属的 fileGroup。实现可插拔——从对象存储友好的 Bloom 到外部 KV 的 HBase，再到自管的 Record Index。",
    stats=[("6+", "索引实现"), ("2 接口", "tagLocation / updateLocation"), ("MDT", "可托管 bloom 与 record index"), ("global?", "跨分区唯一性开关")],
    sections=[
        ("接口与职责", [
            ("fig", fig_index),
            "<code>HoodieIndex</code> 抽象类只要求两个能力：<code>tagLocation</code>（给记录打上 fileId 位置）与 <code>updateLocation</code>（提交后把新 key 写回索引）。是否索引 log 记录（<code>canIndexLogFiles</code>）、是否全局唯一（<code>isGlobal</code>）决定了各实现的行为分叉。",
        ]),
        ("Bloom Index：对象存储的原住民", [
            "<code>SparkHoodieBloomIndex</code> 先用 interval 树按 key 范围裁剪候选文件，再并行读每个文件的 <strong>bloom filter</strong>（写 base 时由 <code>HoodieCreateHandle</code> 写进 footer，MDT 模式下改从元数据表读取），命中者再做精确比对。代价模型由 <code>HoodieGlobalSimpleKeyGenerator</code> 等键生成器配合。",
        ]),
        ("Bucket 与 Record Index", [
            "<code>HoodieBucketIndex</code> 直接按 key 哈希到固定 bucket（一个 bucket = 一个 fileGroup），彻底跳过查找：写入路径 O(1)，代价是 bucket 数固定（<code>ConsistentBucketIndex</code> 用一致性哈希支持扩容）。<strong>Record Index</strong> 是新方向：把 key→location 存进元数据表，随表自愈、无需外部系统。",
        ]),
    ],
    cards=[
        ("#00e5cc", "选型直觉", ["对象存储 + 大表：Bloom/Record Index", "低延迟点查：HBase", "固定 key 分布：Bucket"]),
        ("#fbbf24", "MOR 细节", ["canIndexLogFiles 索引 log 记录", "否则靠 MDT/bloom 定位 log", "index-only 语义影响 merge"]),
        ("#a78bfa", "与并发的关系", ["索引写入与提交同事务", "HBase/Record Index 需处理回滚", "rollback 会回写索引撤销"]),
    ],
))

# ---------------- 07 读路径 ----------------
fig_read = FIG("hudi-read", "图 7-1 · 三种查询：Snapshot / Read Optimized / Incremental", 1040, 500, (
    T(30, 38, "QUERY TYPES · 同一张表的三个读法", 13, "#8fa5c8", True)
    + B(40, 90, 300, 150, "#0f2438", C, "Snapshot Query", "最新数据 · COW 纯 base", tcolor=C)
    + T(60, 148, "MOR：base + log 实时合并", 11, "#8fa5c8")
    + T(60, 168, "InputFormat：HoodieParquetRealtimeInputFormat", 10.5, "#6b7d99", mono=True)
    + T(60, 188, "迭代器链在 map 端完成 merge", 10.5, "#6b7d99")
    + B(400, 90, 300, 150, "#121a30", "#31435f", "Read Optimized", "只读最新完成 compaction 的 base")
    + T(420, 148, "MOR 下牺牲新鲜度换性能", 11, "#8fa5c8")
    + T(420, 168, "HoodieParquetInputFormat", 10.5, "#6b7d99", mono=True)
    + T(420, 188, "COW 下两者等价", 10.5, "#6b7d99")
    + B(760, 90, 240, 150, "#1a1430", CP, "Incremental", "给定起止 instant 的变更流", tcolor=CP)
    + T(780, 148, "拉取区间内新增/变更文件", 11, "#8fa5c8")
    + T(780, 168, "CDC 模式输出前后镜像", 11, "#8fa5c8")
    + T(780, 188, "下游物化视图 / 同步", 10.5, "#6b7d99")
    + R(40, 280, 960, 170, "#121a30", 10, "#31435f")
    + T(60, 310, "视图装配：FileSystemView → FileSlice 选择", 12, "#7fc8e8")
    + T(60, 338, "Snapshot：取每个 fileGroup 的 latest completed slice（MOR 需 merge base+log）", 12, "#8fa5c0")
    + T(60, 366, "ReadOptimized：取 latest completed compaction 之前的纯 base slice", 12, "#8fa5c0")
    + T(60, 394, "Incremental：filterInstantsBefore/After 圈定 instant 区间，仅输出涉及的文件与记录", 12, "#8fa5c0")
    + T(60, 428, "Schema：TableSchemaResolver 统一 avro → spark/parquet 映射", 11.5, "#6b7d99")
))

CHAPTERS_B.append(dict(
    file="07-read-path.html", title="读路径：Snapshot、Read Optimized 与 Incremental",
    kicker="APACHE HUDI SOURCE STUDY · CH 07",
    sub="同一张 Hudi 表提供三种读法，本质是对 FileSlice 的三种选择策略。查询引擎通过 InputFormat / Catalog 接入，视图层负责把「时间线上的某一刻」翻译成「一组可读文件」。",
    stats=[("3 种", "查询类型"), ("1 个", "FileSystemView 视图层"), ("LSN", "instant 区间即增量"), ("0 拷贝", "schema 由 TableSchemaResolver 统一")],
    sections=[
        ("三种查询", [
            ("fig", fig_read),
            "<strong>Snapshot Query</strong> 返回「此刻」的完整表：COW 只读最新 base；MOR 在读时合并 log（merge on read 由此得名）。<strong>Read Optimized</strong> 只读已完成 compaction 的纯 base，牺牲新鲜度换取稳定性能。<strong>Incremental Query</strong> 输出指定 instant 区间内的变更，是下游物化视图与流式管道的基础。",
        ]),
        ("视图层如何选文件", [
            "<code>FileSystemViewManager</code> 为每个表维护视图缓存（可本地内存或服务端化）。<code>HoodieTableFileSystemView.getLatestFileSlices()</code> 等方法按 latest completed instant 选取切片；ReadOptimized 则额外过滤「compaction 已完成」的切片。所有选择都以 CH02 的 timeline 为事实来源。",
        ]),
        ("引擎接入", [
            "Hive/Presto/Trino 走 <code>hudi-hadoop-mr</code> 的 InputFormat（Snapshot 用 Realtime 版，RO 用普通版）；Spark 走 datasource（<code>hudi-spark-datasource</code>）；Flink 走 <code>hudi-flink-datasource</code> 的连贯流读。Schema 由 <code>TableSchemaResolver</code> 把 avro（timeline 与日志块内嵌）映射为引擎类型。",
        ]),
    ],
    cards=[
        ("#00e5cc", "新鲜度 vs 性能", ["Snapshot 最新但 MOR 要 merge", "ReadOptimized 只碰 base", "两者由 compaction 桥接"]),
        ("#a78bfa", "Incremental 用途", ["下游物化视图增量刷新", "CDC 消费（前后镜像）", "与 Flink 流读共享语义"]),
        ("#fbbf24", "实现要点", ["FileSystemView 缓存与失效", "InputFormat 的 split 生成", "删除在 merge 阶段生效"]),
    ],
))

# ---------------- 08 并发控制 ----------------
fig_cc = FIG("hudi-cc", "图 8-1 · 提交协议：锁 + 冲突校验 + timeline 原子推进", 1040, 480, (
    T(30, 38, "CONCURRENCY · OCC 提交协议", 13, "#8fa5c8", True)
    + B(60, 100, 250, 90, "#121a30", "#31435f", "Writer A 完成", "WriteStatus 汇总")
    + B(60, 230, 250, 90, "#121a30", "#31435f", "Writer B 完成", "同一表并发写")
    + B(420, 100, 260, 90, "#2a2010", CY, "TransactionManager", "begin / commit / end", tcolor=CY)
    + T(440, 158, "LockProvider 可插拔", 11, "#8fa5c8")
    + B(420, 230, 260, 90, "#0f2438", C, "ConflictChecker", "与并发 instant 比对文件集", tcolor=C)
    + T(440, 288, "SimpleConcurrentFileWrites…", 11, "#8fa5c8", mono=True)
    + B(780, 165, 220, 90, "#0f2a1c", CG, "通过 → 提交", "completed instant", tcolor=CG)
    + B(780, 280, 220, 90, "#2a1414", CR, "冲突 → 失败", "早期冲突检测可中断", tcolor=CR)
    + A(310, 145, 420, 145, "取锁", color="#5f7ba6")
    + A(310, 275, 420, 275, "取锁", color="#5f7ba6")
    + A(550, 190, 550, 230, "校验", color="#5f7ba6")
    + A(680, 145, 780, 200, "无冲突", color="#5f7ba6")
    + A(680, 275, 780, 320, "有冲突", color="#fb7185", dash=True)
    + R(60, 360, 940, 90, "#121a30", 10, "#31435f")
    + T(80, 390, "隔离级别：Snapshot Isolation（默认）——不同 fileGroup 可并行；Repeatable Read/Serializable 可收紧", 12, "#93a5c0")
    + T(80, 418, "多写者：Zookeeper / DynamoDB / FileSystem 锁；单进程内亦可乐观重试", 12, "#6b7d99")
))

CHAPTERS_B.append(dict(
    file="08-concurrency.html", title="并发控制与 ACID：锁、冲突校验与时间线原子性",
    kicker="APACHE HUDI SOURCE STUDY · CH 08",
    sub="Hudi 的 ACID 建立在三件事上：timeline 文件的原子重命名、可插拔的 LockProvider、以及提交前的 <strong>OCC 冲突校验</strong>。默认 Snapshot Isolation 允许不同 fileGroup 并行写，冲突只在文件集相交时发生。",
    stats=[("OCC", "提交时校验"), ("Snapshot", "默认隔离级别"), ("4+", "LockProvider 实现"), ("单表", "ACID 边界（跨表需外部事务）")],
    sections=[
        ("提交协议", [
            ("fig", fig_cc),
            "每个写客户端在提交前通过 <code>TransactionManager</code> 获取锁（<code>LockProvider</code> 实现：Zookeeper / DynamoDB / FileSystem / 存储 SQL 等），随后 <code>ConflictChecker</code> 拿自己的写入文件集与「并发未完成 instant」的文件集比对，相交即失败。",
        ]),
        ("冲突的粒度", [
            "默认 <strong>Snapshot Isolation</strong>：两个写者只要不写同一个 fileGroup 就能同时提交；这使多管道（流批）写同一张表的不同分区成为常态。需要更严格时开启 <code>hoodie.write.concurrency.mode</code> 与早期冲突检测（写入过程中周期性比对，尽早失败省算力）。",
            "元数据表自身也是 Hudi 表，其提交复用同一套协议；对 HBase / Record Index 这类外部索引，rollback 时会回写撤销记录，保证索引与数据最终一致。",
        ]),
        ("与 Timeline 的配合", [
            "锁只保护「校验 + 提交」的临界区；真正的原子性来自 timeline 文件的重命名。锁丢失或进程崩溃时，inflight instant 由后续写者按 CH02 的恢复语义处理（rollback 或续跑）。",
        ]),
    ],
    cards=[
        ("#00e5cc", "锁提供者", ["ZookeeperBasedLockProvider", "DynamoDBBasedLockProvider（AWS）", "FileSystem/Storage 锁 + 自定义 SPI"]),
        ("#fb7185", "冲突场景", ["同 fileGroup 并发 upsert", "clustering 与写入的文件相交", "schema 演进与写入竞争"]),
        ("#a78bfa", "最佳实践", ["流批写不同分区/表", "开启早期冲突检测省算力", "锁服务监控与超时治理"]),
    ],
))
