# -*- coding: utf-8 -*-
"""Delta Lake 手册 8 章内容（深度版）。"""
from site_fw import B, A, T, R, FIG

CD = "#4f8cff"
CY = "#fbbf24"
CG = "#34d399"
CP = "#a78bfa"
CR = "#fb7185"

CHAPTERS = []

# ================ 01 总体架构 ================
CHAPTERS.append(dict(
    file="01-overview.html", title="Delta Lake 总体架构：以事务日志为唯一真相",
    kicker="DELTA LAKE SOURCE STUDY · CH 01",
    sub="Delta Lake 的全部魔法浓缩成一句话：<strong>一张表就是一个事务日志目录（_delta_log）</strong>。提交 = 追加一个 JSON 文件（原子可见），读取 = 重放日志构建快照，删除 = 逻辑记账。本手册基于 spark/src/main/scala/org/apache/spark/sql/delta 的逐模块分析，把这条主线拆开看透。",
    stats=[("1 目录", "_delta_log 即表"), ("7 类", "核心 action"), ("OCC", "乐观并发提交"), ("2 内核", "Spark + Rust Kernel")],
    sections=[
        ("要解决什么问题", [
            "对象存储上的 Parquet 目录没有事务：并发写互相覆盖、更新只能全量重写、无法回滚。Delta Lake 用<strong>预写日志（Write-Ahead Log）</strong>逐一破解：每次提交是原子可见的 JSON 文件，记录「新增哪些文件、删除哪些文件、元数据如何变化」。",
            "这条设计让 Delta 用最朴素的文件原语获得了 ACID，也让 Time Travel、Schema 演进、审计成为免费副产品——它们都只是「读日志的另一种方式」。",
        ]),
        ("总体架构图", [
            ("fig", FIG("delta-arch", "图 1-1 · Delta 总体架构：引擎、事务日志、数据文件与事务管理", 1040, 540, (
                T(30, 40, "DELTA ARCHITECTURE · 引擎、事务日志与数据文件", 13, "#8fa5c8", True)
                + R(30, 70, 250, 130, "#121a30", 10, "#31435f")
                + T(50, 98, "查询/写入引擎", 12, "#7fc8e8", True)
                + T(50, 124, "Spark · Flink · Trino", 12, "#dbe6f5", True)
                + T(50, 148, "经 DeltaTableV2 / Catalog", 11, "#6b7d99")
                + T(50, 172, "或 Delta Kernel 接入", 11, "#6b7d99")
                + R(380, 70, 280, 130, "#0f2438", 10, CD)
                + T(400, 98, "_delta_log/（核心）", 12.5, CD, True)
                + T(400, 124, "00000N.json（增量提交）", 11.5, "#dbe6f5", mono=True)
                + T(400, 148, "N.checkpoint.parquet", 11.5, "#dbe6f5", mono=True)
                + T(400, 172, "_last_checkpoint / CRC", 11.5, "#8fa5c8", mono=True)
                + T(400, 194, "唯一真相 · 文件级原子可见", 11, CY, mono=True)
                + R(380, 240, 280, 110, "#121a30", 10, "#31435f")
                + T(400, 268, "Snapshot", 12.5, "#dbe6f5", True)
                + T(400, 292, "重放日志的内存视图", 11, "#8fa5c8")
                + T(400, 316, "activeFiles / tombstones /", 11, "#8fa5c8", mono=True)
                + T(400, 338, "setTransactions 三集合", 11, "#8fa5c8", mono=True)
                + R(740, 70, 270, 130, "#121a30", 10, "#31435f")
                + T(760, 98, "数据文件（Parquet）", 12, "#7fc8e8", True)
                + T(760, 124, "文件本身不可变", 12, "#dbe6f5", True)
                + T(760, 148, "删除 = remove action（逻辑删）", 11, "#8fa5c8")
                + T(760, 172, "Vacuum 才物理清理", 11, "#8fa5c8")
                + R(740, 240, 270, 110, "#2a2010", 10, CY)
                + T(760, 268, "OptimisticTransaction", 12, CY, True)
                + T(760, 292, "提交前 ConflictChecker 校验", 11.5, "#dbe6f5")
                + T(760, 316, "隔离级别：WriteSerializable", 11, "#8fa5c8", mono=True)
                + R(30, 240, 250, 110, "#121a30", 10, "#31435f")
                + T(50, 268, "Checkpoints / CRC", 12, "#7fc8e8", True)
                + T(50, 292, "加速快照构建", 11.5, "#dbe6f5")
                + T(50, 316, "CheckpointProvider 定位", 11, "#8fa5c8", mono=True)
                + A(280, 135, 380, 135, "读写日志", color="#5f7ba6", lx=330, ly=126)
                + A(520, 200, 520, 240, "重放", color="#5f7ba6", lx=570, ly=225)
                + A(660, 135, 740, 135, "引用文件", color="#5f7ba6", lx=700, ly=126)
                + A(740, 300, 660, 300, "提交校验", color="#5f7ba6", dash=True, lx=700, ly=290)
                + A(180, 200, 180, 240, "加速", color="#5f7ba6", dash=True, lx=180, ly=225)
                + R(30, 400, 980, 110, "#121a30", 10, "#31435f")
                + T(50, 428, "读引擎只需三个存储原语", 12, "#7fc8e8", True)
                + T(50, 454, "① 原子 put（写完整 JSON）　② List 前缀（找日志文件）　③ 读文件——这就是 Delta Kernel 与各云厂商广泛接入的原因", 11.5, "#dbe6f5")
                + T(50, 482, "S3 缺原子 rename，由 LogStore 抽象补齐：S3SingleDriverLogStore + DynamoDB 条件写锁", 11.5, "#8fa5c8")
            ))),
            "引擎侧只需要三个存储原语：原子 put、前缀 List、顺序读文件——这就是 Delta Kernel 与各大云厂商能广泛建立接入的原因。",
        ]),
        ("仓库地图（逐目录）", [
            "核心在 <code>spark/src/main/scala/org/apache/spark/sql/delta/</code>：<strong>actions/</strong>（日志协议的 case class）、<strong>commands/</strong>（DML 实现）、<code>OptimisticTransaction.scala</code>、<code>ConflictChecker.scala</code>、<code>Checkpoints.scala</code>、<code>SnapshotManagement.scala</code>、<code>catalog/</code>（目录集成）。",
            "<code>delta-kernel/</code> 与独立仓库 <code>delta-io/delta-kernel-rs</code> 是 Rust 通用读内核；<code>connectors/</code> 承载 Flink/Presto 连接器；<code>storage-s3-dynamodb</code> 提供 S3 上的锁实现。",
        ]),
    ],
    cards=[
        ("#4f8cff", "三大设计", ["日志即表：_delta_log 唯一真相", "数据文件不可变", "提交原子可见"]),
        ("#fbbf24", "免费副产品", ["Time Travel：读旧版本日志", "审计：CommitInfo 全记录", "Schema 演进：meta action"]),
        ("#a78bfa", "读源码主线", ["DeltaLog → Snapshot → 算子", "OptimisticTransaction 提交", "ConflictChecker 并发语义"]),
    ],
))

# ================ 02 Transaction Log ================
CHAPTERS.append(dict(
    file="02-transaction-log.html", title="Transaction Log：七个 action 定义一张表",
    kicker="DELTA LAKE SOURCE STUDY · CH 02",
    sub="<code>_delta_log/00000N.json</code> 里每行一个 action（JSON）。七类 action 组合起来就是 Delta 表在某一刻的完整描述：文件账本（add/remove）、表定义（meta/protocol）、流幂等（setTransaction）、审计（commitInfo）与扩展位（domainMetadata）。",
    stats=[("7 类", "核心 action"), ("1 行", "一个 action（JSON）"), ("原子", "文件级可见性"), ("00000N", "零填充版本号")],
    sections=[
        ("action 协议全景", [
            ("fig", FIG("delta-actions", "图 2-1 · 一次提交的 JSON 内容与七类 action 的职责分工", 1040, 560, (
                T(30, 40, "TRANSACTION LOG ACTIONS · 000005.json 内容解剖", 13, "#8fa5c8", True)
                + R(30, 70, 470, 250, "#121a30", 10, "#31435f")
                + T(50, 98, "一次 append 提交的实际 JSON（节选）", 12, "#7fc8e8", True)
                + T(50, 126, '{"commitInfo":{"timestamp":1690000000000,', 11, "#8fa5c8", mono=True)
                + T(66, 148, '"operation":"WRITE","operationParameters":{"mode":"Append"}}}', 11, "#8fa5c8", mono=True)
                + T(50, 174, '{"meta":{"id":"...","format":{…},"schemaString":"…"}}', 11, "#8fa5c8", mono=True)
                + T(50, 200, '{"add":{"path":"part-0000-….snappy.parquet","partitionValues":{},', 11, "#8fa5c8", mono=True)
                + T(66, 222, '"size":1024,"modificationTime":169…,', 11, "#8fa5c8", mono=True)
                + T(66, 244, '"dataChange":true,"stats":"{numRecords:1000,…}"}}', 11, "#8fa5c8", mono=True)
                + T(50, 274, "stats 内嵌 numRecords/minValues/maxValues/nullCount", 11, "#93a5c0")
                + T(50, 300, "→ 查询时按文件级 min/max 裁剪的原料", 11, "#93a5c0")
                + R(540, 70, 470, 250, "#121a30", 10, "#31435f")
                + T(560, 98, "七类 action 的职责分工", 12, "#7fc8e8", True)
                + T(560, 126, "add        新文件入账本（path/size/stats）", 11.5, CG, mono=True)
                + T(560, 150, "remove     逻辑删除（dataChange 区分）", 11.5, CR, mono=True)
                + T(560, 174, "meta       schemaString / 分区列 / 配置", 11.5, "#dbe6f5", mono=True)
                + T(560, 198, "protocol   minReader / minWriter 门槛", 11.5, "#dbe6f5", mono=True)
                + T(560, 222, "setTransaction  appId+version 流幂等", 11.5, "#dbe6f5", mono=True)
                + T(560, 246, "commitInfo 时间戳/操作/用户/隔离级别", 11.5, "#dbe6f5", mono=True)
                + T(560, 270, "domainMetadata  表级扩展配置", 11.5, "#dbe6f5", mono=True)
                + T(560, 300, "定义于 actions/ 包：AddFile.scala 等", 11, "#6b7d99", mono=True)
                + R(30, 340, 980, 230, "#121a30", 10, "#31435f")
                + T(50, 368, "关键语义", 12, "#7fc8e8", True)
                + T(50, 396, "① dataChange:false：Optimize/Clustering 产出的 add/remove 不改逻辑数据，增量消费者据此过滤", 11.5, "#dbe6f5")
                + T(50, 422, "② remove 的 deletionTimestamp 只是信息字段：真正的删除 = 日志重放时 add 集合减去 remove 集合", 11.5, "#dbe6f5")
                + T(50, 448, "③ protocol 是门槛：旧引擎读到高 protocol 版本必须拒绝，防止不支持特性的引擎破坏表", 11.5, "#dbe6f5")
                + T(50, 474, "④ setTransaction 幂等：Structured Streaming 以 (appId, version) 标记进度，重复提交被日志直接拒绝", 11.5, "#dbe6f5")
                + T(50, 500, "⑤ 版本号零填充：00000000000000000001.json —— 字典序 = 版本序，List 后无需排序细节", 11.5, "#dbe6f5")
                + T(50, 528, "反序列化：Action 伴生对象 + JsonUtils（Jackson），接受未知字段（前向兼容）", 11.5, "#6b7d99")
            ))),
        ]),
        ("原子性与 LogStore", [
            "对象存储上「文件写完整即完整可见」，所以 Delta 的原子提交 = <strong>把整个 JSON 写完再让它出现</strong>。HDFS 有原子 rename 天然支持；S3 没有，由 <code>LogStore</code> 抽象补齐：S3SingleDriverLogStore 配合 DynamoDB 条件写（putIfAbsent）实现「同版本号只有一个提交者赢」。",
            "这个抽象也是社区争议最多的地方（早期 Azure/S3 行为差异），读源码时注意 <code>LogStoreProvider</code> 按 scheme 分发的逻辑与 <code>delta.logStore.*</code> 配置族。",
        ]),
    ],
    cards=[
        ("#4f8cff", "七个 action", ["add / remove：文件账本", "meta / protocol：表定义", "setTransaction / commitInfo / domain"]),
        ("#fbbf24", "stats 的价值", ["min/max/nullCount 内嵌", "文件级裁剪的原料", "checkpoint 时聚合"]),
        ("#a78bfa", "LogStore 抽象", ["HDFS：rename 原子", "S3：DynamoDB 锁补齐", "自定义 SPI 可插拔"]),
    ],
))

# ================ 03 Snapshot ================
CHAPTERS.append(dict(
    file="03-snapshot.html", title="Snapshot：重放日志构建表的内存视图",
    kicker="DELTA LAKE SOURCE STUDY · CH 03",
    sub="Snapshot 是 Delta 的大脑：把 checkpoint parquet + 增量 JSON 重放成 <strong>activeFiles / tombstones / setTransactions</strong> 三个集合，再暴露分区裁剪、文件列举与 Time Travel 能力。SnapshotManagement 负责缓存与版本切换。",
    stats=[("3 集合", "active/tombstone/txn"), ("最短路径", "checkpoint + 增量 json"), ("TT", "version/timestamp AsOf"), ("缓存", "SnapshotManagement")],
    sections=[
        ("构建过程", [
            ("fig", FIG("delta-snapshot", "图 3-1 · Snapshot 构建：从 _last_checkpoint 到最新版本的最短重放", 1040, 480, (
                T(30, 40, "SNAPSHOT BUILD · SnapshotManagement.loadSnapshot", 13, "#8fa5c8", True)
                + B(40, 90, 220, 90, "#121a30", "#31435f", "① _last_checkpoint", "version · parts · size")
                + B(340, 90, 220, 90, "#0f2438", CD, "② checkpoint parquet", "全量状态一次装入", tcolor=CD)
                + B(640, 90, 200, 90, "#121a30", "#31435f", "③ 重放增量 json", "checkpoint+1 → N")
                + B(40, 250, 220, 90, "#2a2010", CY, "CRC 校验和", "action/file 计数一致性", tcolor=CY)
                + B(640, 250, 200, 90, "#0f2a1c", CG, "④ Snapshot N", "三集合 + 分区谓词缓存", tcolor=CG)
                + A(260, 135, 340, 135, "", color="#5f7ba6")
                + A(560, 135, 640, 135, "", color="#5f7ba6")
                + A(840, 135, 880, 135, "", color="#5f7ba6")
                + A(150, 180, 150, 250, "校验", color="#5f7ba6", dash=True, lx=150)
                + A(740, 180, 740, 250, "", color="#5f7ba6")
                + T(40, 390, "重放语义：activeFiles = add 集合 − remove 集合；tombstones 保留最近窗口（冲突检测需要）；", 12, "#93a5c0")
                + T(40, 416, "setTransactions 保留用于流幂等。Time Travel 直接从目标版本的 checkpoint/json 重放，无需回放全史。", 12, "#93a5c0")
                + T(40, 442, "_last_checkpoint 让快照构建免 List：对象存储上 List 前缀又慢又贵，这个指针文件是关键加速器。", 12, "#93a5c0")
            ))),
            "<code>SnapshotManagement</code> 缓存当前 Snapshot 与最近历史；<code>CheckpointProvider</code> 按 _last_checkpoint（含 version/parts/size）定位 checkpoint 文件族。",
        ]),
        ("Time Travel 与 Schema", [
            "<code>versionAsOf</code> / <code>timestampAsOf</code> 触发历史版本 Snapshot 构建：从「≤ 目标版本的最近 checkpoint」开始重放到目标版本。meta action 携带 <code>schemaString</code>，每个版本自带 schema——列裁剪与分区值映射基于它。",
            "vacuum 会清理不再被任何保留版本引用的物理文件，因此 Time Travel 的窗口与 <code>delta.deletedFileRetentionDuration</code>（默认 7 天）直接相关——读太旧的版本会报文件缺失。",
        ]),
    ],
    cards=[
        ("#4f8cff", "三集合", ["activeFiles：当前有效文件", "tombstones：冲突检测用", "setTransactions：流幂等"]),
        ("#fbbf24", "加速设计", ["_last_checkpoint 免 List", "checkpoint parquet 一次装入", "CRC 校验和防损坏"]),
        ("#a78bfa", "Time Travel", ["versionAsOf / timestampAsOf", "从目标版本 checkpoint 重放", "受 retention 窗口约束"]),
    ],
))

# ================ 04 Checkpoint ================
CHAPTERS.append(dict(
    file="04-checkpoint.html", title="Checkpoint：让快照构建从 O(日志) 变 O(1)",
    kicker="DELTA LAKE SOURCE STUDY · CH 04",
    sub="日志无限增长会让重放越来越慢。Checkpoint 把全量状态写成结构化 Parquet（可多 part 并行），此后快照构建只需 checkpoint + 少量增量 JSON。v2 引入 sidecar 文件与 CRC 校验。",
    stats=[("Parquet", "checkpoint 格式"), ("10 parts", "可并行的分片文件"), ("v2", "sidecar + CRC"), ("默认 10 次", "checkpointInterval")],
    sections=[
        ("Checkpoint 结构", [
            ("fig", FIG("delta-checkpoint", "图 4-1 · Checkpoint 文件族与 last_checkpoint 元信息", 1040, 460, (
                T(30, 40, "CHECKPOINT · Checkpoints.scala", 13, "#8fa5c8", True)
                + R(40, 90, 300, 130, "#0f2438", 10, CD)
                + T(60, 114, "N.checkpoint.parquet", 12, CD, True, mono=True)
                + T(60, 138, "v1：最多 10 个 part 并行写", 10.5, "#dbe6f5")
                + T(60, 164, "内容 = 全部 action 的当前态：", 10.5, "#8fa5c8")
                + T(76, 186, "active add 集合 · tombstones（截断）", 10.5, "#8fa5c8", mono=True)
                + T(76, 208, "setTransactions · meta · protocol", 10.5, "#8fa5c8", mono=True)
                + R(400, 90, 300, 110, "#121a30", 10, "#31435f")
                + T(420, 114, "_last_checkpoint", 12, "#dbe6f5", True, mono=True)
                + T(420, 138, "version · parts · size", 10.5, "#8fa5c8", mono=True)
                + T(420, 164, "List 前缀之前先读它", 10.5, "#8fa5c8")
                + T(420, 186, "对象存储加速的关键", 10.5, "#8fa5c8")
                + R(760, 90, 240, 110, "#2a2010", 10, CY)
                + T(780, 114, "CRC 校验文件", 12, CY, True)
                + T(780, 138, "action/file 计数", 10.5, "#dbe6f5", mono=True)
                + T(780, 164, "构建后快速一致性验证", 10.5, "#8fa5c8")
                + R(40, 250, 300, 110, "#121a30", 10, "#31435f")
                + T(60, 274, "v2：sidecar 文件", 12, "#dbe6f5", True)
                + T(60, 298, "大动作溢出到 .sidecar", 10.5, "#8fa5c8")
                + T(60, 322, "主 checkpoint 保持精简", 10.5, "#8fa5c8")
                + T(60, 344, "读取时按需加载 sidecar", 10.5, "#8fa5c8")
                + R(400, 250, 300, 110, "#0f2a1c", 10, CG)
                + T(420, 274, "触发", 12, CG, True)
                + T(420, 298, "delta.checkpointInterval", 10.5, "#dbe6f5", mono=True)
                + T(420, 322, "默认每 10 次提交", 10.5, "#8fa5c8")
                + T(420, 344, "post-commit hook 驱动", 10.5, "#8fa5c8")
                + A(340, 135, 400, 135, "v2 溢出", color="#5f7ba6", dash=True, lx=370, ly=124)
                + A(190, 220, 190, 250, "指向", color="#5f7ba6", lx=240)
                + A(550, 200, 550, 250, "每 N 次提交", color="#5f7ba6", dash=True, lx=610)
            ))),
            "<code>Checkpoints.scala</code> 的 <code>writeCheckpointFiles</code> 用 Spark 并行写 parts；v2 checkpoint 主文件只含少量代表性 action，大体积内容进 sidecar，读取时按需加载。",
        ]),
        ("触发与校验", [
            "默认每 <code>delta.checkpointInterval</code>（10）次提交触发；由 post-commit hook 驱动。写入流程：先写 checkpoint parts → 再原子更新 _last_checkpoint——中途失败只留下未引用的 part，不影响正确性，重试即恢复。",
            "checksum（<code>Checksum.scala</code>，v2）：记录 tableFeature/协议版本、action 计数、文件数等指纹；下次快照构建后比对，及早发现日志损坏或 List 遗漏。",
        ]),
    ],
    cards=[
        ("#4f8cff", "读路径收益", ["快照构建 O(1) 起步", "免 List 对象存储友好", "并行读多个 part"]),
        ("#fbbf24", "v2 sidecar", ["大 add 集合溢出存储", "主文件保持精简", "按需加载 sidecar"]),
        ("#a78bfa", "一致性", ["CRC 校验和", "_last_checkpoint 先行", "失败可安全重做"]),
    ],
))

# ================ 05 乐观事务 ================
CHAPTERS.append(dict(
    file="05-optimistic-tx.html", title="乐观事务：OptimisticTransaction 与冲突判定",
    kicker="DELTA LAKE SOURCE STUDY · CH 05",
    sub="所有写入都运行在 <code>OptimisticTransaction</code> 里：读快照做修改，提交时用 <code>ConflictChecker</code> 与并发提交比对，赢者落日志、输者重试或失败。隔离级别可配置，流式写入用 setTransaction 保证恰好一次。",
    stats=[("OCC", "无锁乐观并发"), ("2 级", "WriteSerializable/Serializable"), ("重试", "冲突自动重试 N 次"), ("幂等", "setTransaction 防重放")],
    sections=[
        ("事务生命周期", [
            ("fig", FIG("delta-txn", "图 5-1 · 事务生命周期：读快照 → 修改 → 校验 → 提交（失败重试）", 1040, 480, (
                T(30, 40, "OPTIMISTIC TRANSACTION · OptimisticTransaction.scala", 13, "#8fa5c8", True)
                + R(40, 90, 230, 120, "#0f2438", 10, CD)
                + T(60, 114, "txn 开始", 12, CD, True)
                + T(60, 138, "绑定 Snapshot 版本 V0", 10.5, "#dbe6f5", mono=True)
                + T(60, 162, "readFiles / readWholeTable", 10.5, "#8fa5c8", mono=True)
                + T(60, 186, "readPredicates 登记读谓词", 10.5, "#8fa5c8", mono=True)
                + R(340, 90, 230, 120, "#121a30", 10, "#31435f")
                + T(360, 114, "读写文件", 12, "#dbe6f5", True)
                + T(360, 138, "touchedFiles 登记", 10.5, "#8fa5c8", mono=True)
                + T(360, 162, "add/remove 进事务缓冲", 10.5, "#8fa5c8", mono=True)
                + R(640, 90, 210, 120, "#2a2010", 10, CY)
                + T(660, 114, "prepareCommit", 12, CY, True, mono=True)
                + T(660, 138, "组装 action 序列", 10.5, "#8fa5c8")
                + T(660, 162, "commitInfo + add/remove…", 10.5, "#8fa5c8", mono=True)
                + R(340, 250, 230, 120, "#121a30", 10, "#31435f")
                + T(360, 274, "doCommitRetryLoop", 12, "#dbe6f5", True, mono=True)
                + T(360, 298, "写 V0.json → 已存在?", 10.5, "#8fa5c8", mono=True)
                + T(360, 322, "冲突 → ConflictChecker", 10.5, "#8fa5c8", mono=True)
                + R(640, 250, 210, 120, "#0f2438", 10, CD)
                + T(660, 274, "判定", 12, CD, True)
                + T(660, 298, "可重试 → V1 重来", 10.5, "#dbe6f5", mono=True)
                + T(660, 322, "不可重试 → 抛异常", 10.5, "#8fa5c8", mono=True)
                + R(40, 250, 230, 120, "#0f2a1c", 10, CG)
                + T(60, 274, "提交成功", 12, CG, True)
                + T(60, 298, "post-commit hooks", 10.5, "#dbe6f5", mono=True)
                + T(60, 322, "checkpoint / UniForm / metrics", 10.5, "#8fa5c8", mono=True)
                + A(270, 138, 340, 138, "", color="#5f7ba6")
                + A(570, 138, 640, 138, "", color="#5f7ba6")
                + A(745, 186, 745, 250, "写 V0.json", color="#5f7ba6", lx=810)
                + A(570, 298, 640, 298, "冲突?", color="#5f7ba6", lx=605, ly=288)
                + A(340, 298, 155, 298, "成功", color="#5f7ba6", dash=True, lx=250, ly=288)
                + A(455, 250, 455, 186, "重试 V+1", color="#5f7ba6", dash=True, lx=390)
            ))),
            "提交核心是 <code>doCommitRetryLoop</code>：把 action 写成版本号 (读取版本+重试次数) 的 json；目标文件已存在（他人先提交）则进入 ConflictChecker 判定可否重试。",
        ]),
        ("冲突判定细则", [
            "<code>ConflictChecker</code> 依次回答：<strong>①</strong> 并发提交是否改了 metadata（schema/分区/协议 → 必失败）；<strong>②</strong> 是否删除了我读过的文件；<strong>③</strong> 是否添加了我读过范围内的文件（WriteSerializable 下纯追加与纯追加不冲突）；<strong>④</strong> 是否有 setTransaction 重复。",
            "隔离级别：<strong>WriteSerializable</strong>（默认）——纯追加之间不冲突（可并行），但与读改写操作按文件集判定；<strong>Serializable</strong> 更严格，读过的文件被并发改动也算冲突。append-only 配置可走快速路径跳过大部分校验。",
            "流式查询用 <code>setTransaction(appId, version)</code> 恰好一次：同一 (appId, version) 重复提交被日志直接拒绝——这是 Structured Streaming checkpoint 与 Delta 的握手点。",
        ]),
    ],
    cards=[
        ("#4f8cff", "重试策略", ["版本号冲突 → 递增重试", "可重试冲突自动重放", "不可重试抛并发异常"]),
        ("#fbbf24", "隔离级别", ["WriteSerializable 默认", "Serializable 全序化", "append-only 快速路径"]),
        ("#a78bfa", "后置钩子", ["checkpoint 触发", "UniForm/Iceberg 同步", "统计与 metrics 上报"]),
    ],
))

# ================ 06 DML ================
CHAPTERS.append(dict(
    file="06-dml.html", title="DML 实现：Write、Delete、Update、Merge 的物理路径",
    kicker="DELTA LAKE SOURCE STUDY · CH 06",
    sub="commands/ 包是 Delta 的四肢：四种 DML 最终都翻译成「读相关文件 → 计算新文件集 → 产出 add/remove」。理解这个统一模式，四种语法的源码就只剩各自的优化点（Delete 的 DV 分支、Merge 的两阶段等）。",
    stats=[("4 类", "核心 DML"), ("统一", "add/remove 输出"), ("2 路", "Delete 重写 or DV"), ("Merge", "matched/notMatched 双阶段")],
    sections=[
        ("统一模式", [
            ("fig", FIG("delta-dml", "图 6-1 · DML 统一：四种命令都产出 add/remove 对，一并提交", 1040, 500, (
                T(30, 40, "DML COMMANDS · commands/ 包", 13, "#8fa5c8", True)
                + R(30, 70, 240, 360, "#121a30", 10, "#31435f")
                + T(50, 98, "四种命令", 12, "#7fc8e8", True)
                + T(50, 128, "WriteIntoDelta", 12, CD, True, mono=True)
                + T(50, 150, "Append / Overwrite", 10.5, "#8fa5c8")
                + T(50, 190, "DeleteCommand", 12, CR, True, mono=True)
                + T(50, 212, "全文件 → remove", 10.5, "#8fa5c8")
                + T(50, 250, "UpdateCommand", 12, CP, True, mono=True)
                + T(50, 272, "重写受影响文件", 10.5, "#8fa5c8")
                + T(50, 310, "MergeIntoDelta", 12, CG, True, mono=True)
                + T(50, 332, "matched/notMatched", 10.5, "#8fa5c8")
                + R(340, 70, 300, 360, "#0f2438", 10, CD)
                + T(360, 98, "统一物理计划", 12.5, CD, True)
                + T(360, 128, "① 读命中文件（分区/统计裁剪）", 11.5, "#dbe6f5")
                + T(360, 156, "② 计算 → 写新文件", 11.5, "#dbe6f5")
                + T(360, 184, "③ 产出 add/remove 对", 11.5, "#dbe6f5")
                + T(360, 212, "④ OptimisticTransaction 提交", 11.5, "#dbe6f5")
                + T(360, 252, "Delete 的两路：", 11.5, CY, True)
                + T(360, 280, "全文件命中 → 纯 remove（快）", 11, "#8fa5c8")
                + T(360, 308, "部分命中 → 重写文件或 DV 位图", 11, "#8fa5c8")
                + T(360, 336, "Overwrite replaceWhere 条件替换", 11, "#8fa5c8")
                + T(360, 364, "动态分区覆写：仅写匹配分区", 11, "#8fa5c8")
                + R(720, 70, 290, 200, "#1a1430", 10, CP)
                + T(740, 98, "Deletion Vectors（DV）", 12.5, CP, True)
                + T(740, 126, "行级删除位图（puffin 格式）", 11.5, "#dbe6f5")
                + T(740, 150, "免重写整文件", 11.5, "#8fa5c8")
                + T(740, 174, "delta.enableDeletionVectors", 11, "#8fa5c8", mono=True)
                + T(740, 198, "读取时按位图过滤行", 11, "#8fa5c8")
                + R(720, 310, 290, 120, "#121a30", 10, "#31435f")
                + T(740, 338, "MergeIntoDelta 两阶段", 12, "#dbe6f5", True)
                + T(740, 364, "源 join 目标 → matched 集合", 11, "#8fa5c8")
                + T(740, 388, "whenMatched/notMatched 子句", 11, "#8fa5c8")
            ))),
        ]),
        ("Merge 的两阶段", [
            "<code>MergeIntoDelta</code> 先用源表 join 目标表找出 matched / notMatched 集合，再分别生成 update/insert 文件；整个 merge 是一次事务（一个版本的 add/remove），失败整体回滚。频繁小 merge 会造成读放大，配合 Optimize 与 DV 收益最佳。",
        ]),
    ],
    cards=[
        ("#4f8cff", "Write", ["Append / Overwrite / replaceWhere", "动态分区覆写", "schema 演进 mergeSchema"]),
        ("#fb7185", "Delete 两路", ["全文件命中 → 纯 remove", "部分命中 → 重写或 DV", "DV 由表属性启用"]),
        ("#a78bfa", "Merge 要点", ["matched/notMatched 两集合", "whenMatched/notMatched 子句", "一次事务整体可见"]),
    ],
))

# ================ 07 表维护 ================
CHAPTERS.append(dict(
    file="07-maintenance.html", title="表维护：Optimize、Z-Order 与 Vacuum",
    kicker="DELTA LAKE SOURCE STUDY · CH 07",
    sub="Delta 的维护三板斧：<strong>Optimize</strong> 合并小文件（可选 Z-Order 重排），<strong>Vacuum</strong> 清理孤儿文件，二者都建立在「日志是逻辑真相、文件是物理残留」的二元性上。",
    stats=[("bin-pack", "Optimize 文件合并"), ("Z-Order", "多维聚类重排"), ("默认 7 天", "Vacuum 保留窗口"), ("dry-run", "预览模式")],
    sections=[
        ("Optimize 与 Z-Order", [
            ("fig", FIG("delta-optimize", "图 7-1 · Optimize bin-packing 与 Z-Order 重排", 1040, 460, (
                T(30, 40, "OPTIMIZE / ZORDER · OptimizeTableCommand", 13, "#8fa5c8", True)
                + B(40, 90, 220, 110, "#121a30", "#31435f", "候选文件", "where 谓词选分区")
                + T(60, 148, "小文件按大小分桶", 11, "#8fa5c8")
                + T(60, 170, "minSize/maxSize 控制分桶", 10.5, "#6b7d99")
                + B(340, 90, 220, 110, "#0f2438", CD, "bin-pack 合并", "目标 ~1GB 输出文件", tcolor=CD)
                + T(360, 148, "dataChange=false", 11, "#8fa5c8", mono=True)
                + T(360, 170, "不影响增量消费者", 11, "#8fa5c8")
                + B(640, 90, 360, 110, "#1a1430", CP, "Z-Order 重排", "zOrderCols 多列交错排序", tcolor=CP)
                + T(660, 148, "先重排行再写 → 数据局部性", 11, "#8fa5c8")
                + T(660, 170, "每个文件的 min/max 更紧", 11, "#8fa5c8")
                + B(40, 250, 220, 110, "#121a30", "#31435f", "输出与提交", "add/remove + replacecommit 语义")
                + T(60, 308, "commitInfo 记录 zOrderBy", 11, "#8fa5c8")
                + T(60, 330, "失败可整体回滚", 11, "#8fa5c8")
                + B(340, 250, 220, 110, "#2a2010", CY, "收益来源", "stats 驱动的查询裁剪", tcolor=CY)
                + T(360, 308, "区间更紧 → 跳过更多文件", 11, "#8fa5c8")
                + T(360, 330, "与 DV 一起在重写时融合", 11, "#8fa5c8")
                + B(640, 250, 360, 110, "#0f2a1c", CG, "Liquid Clustering 演进", "增量式聚类，避免全量重排", tcolor=CG)
                + T(660, 308, "clustering columns 表属性", 11, "#8fa5c8", mono=True)
                + T(660, 330, "写入时自动组织", 11, "#8fa5c8")
                + A(260, 145, 340, 145, "", color="#5f7ba6")
                + A(560, 145, 640, 145, "zOrderCols 指定", color="#5f7ba6", dash=True, lx=600, ly=134)
                + A(450, 200, 450, 250, "", color="#5f7ba6")
                + A(340, 305, 260, 305, "", color="#5f7ba6")
            ))),
        ]),
        ("Vacuum", [
            "<code>VacuumCommand</code> 列出表目录中所有物理文件，凡不在当前（及保留期内）日志引用且早于 <code>retentionDuration</code>（默认 168h）的都删除。dry-run 先列出待删清单。保留窗口是 Time Travel 安全边界的另一面：窗口太短会让并发读者/长事务读到「文件已被删」。",
            "Vacuum 与 DV 的关系：携带删除位图的文件被引用时不可删；Optimize 重写会融合 DV 使位图失效的行真正消失。",
        ]),
    ],
    cards=[
        ("#4f8cff", "Optimize", ["bin-pack 小文件合并", "按分区/谓词圈定范围", "dataChange=false 不影响增量"]),
        ("#a78bfa", "Z-Order", ["多维聚类改善局部性", "stats 聚集 → 更强裁剪", "liquid clustering 演进"]),
        ("#fb7185", "Vacuum", ["删日志未引用的物理文件", "retention 是 TT 安全窗", "dry-run 先看清单"]),
    ],
))

# ================ 08 内核与生态 ================
CHAPTERS.append(dict(
    file="08-kernel-ecosystem.html", title="通用内核与生态：Kernel、UniForm 与 Catalog",
    kicker="DELTA LAKE SOURCE STUDY · CH 08",
    sub="Delta 正在把「读表」能力下沉到 <strong>Delta Kernel</strong>（Rust/Java 独立库），把「表格式」通过 <strong>UniForm</strong> 同时暴露为 Iceberg/Hudi，让任意引擎零绑定接入——这是理解 Delta 生态演进的两把钥匙。",
    stats=[("Kernel", "Rust 独立读内核"), ("UniForm", "同时是 Iceberg/Hudi"), ("Catalog", "UC/Hive/Glue 绑定"), ("Streaming", "Structured Streaming 深度集成")],
    sections=[
        ("Delta Kernel", [
            ("fig", FIG("delta-kernel", "图 8-1 · Kernel 与 UniForm：把表格式开放给任意引擎", 1040, 480, (
                T(30, 40, "KERNEL & UNIFORM · 开放的表格式", 13, "#8fa5c8", True)
                + R(30, 70, 280, 150, "#0f2438", 10, CD)
                + T(50, 98, "Delta Kernel (Rust)", 12.5, CD, True)
                + T(50, 124, "读日志 + 扫描 Parquet 的最小库", 11.5, "#dbe6f5")
                + T(50, 148, "引擎只需实现文件读取 SPI", 11, "#8fa5c8")
                + T(50, 172, "Java Kernel：JVM 轻量接入", 11, "#8fa5c8")
                + T(50, 196, "写路径仍以 Spark 为主", 10.5, "#6b7d99")
                + R(30, 260, 280, 130, "#121a30", 10, "#31435f")
                + T(50, 288, "读流程（Kernel 视角）", 12, "#7fc8e8", True)
                + T(50, 314, "日志重放 → 文件列表 + 谓词", 11.5, "#dbe6f5", mono=True)
                + T(50, 338, "DV/puffin 过滤", 11.5, "#dbe6f5", mono=True)
                + T(50, 362, "扫描回调给引擎", 11.5, "#dbe6f5", mono=True)
                + R(380, 70, 300, 150, "#1a1430", 10, CP)
                + T(400, 98, "UniForm", 12.5, CP, True)
                + T(400, 124, "一份 delta 日志 → 异步生成", 11.5, "#dbe6f5")
                + T(400, 148, "Iceberg 元数据（IcebergCompat）", 11.5, "#dbe6f5", mono=True)
                + T(400, 172, "Hudi 同步（DeltaStamp）", 11.5, "#8fa5c8", mono=True)
                + T(400, 196, "表格式之争 → 互操作之争", 10.5, "#6b7d99")
                + R(380, 260, 300, 130, "#121a30", 10, "#31435f")
                + T(400, 288, "Catalog 与流", 12, "#7fc8e8", True)
                + T(400, 314, "Unity Catalog / Glue / Hive", 11.5, "#dbe6f5", mono=True)
                + T(400, 338, "setTransaction 恰好一次", 11.5, "#dbe6f5", mono=True)
                + T(400, 362, "streaming table / CDC 视图", 11.5, "#dbe6f5", mono=True)
                + R(740, 70, 270, 320, "#0f2a1c", 10, CG)
                + T(760, 98, "接入的引擎", 12.5, CG, True)
                + T(760, 126, "Spark（原生）", 11.5, "#dbe6f5", mono=True)
                + T(760, 150, "Flink / Presto / Trino", 11.5, "#dbe6f5", mono=True)
                + T(760, 174, "Snowflake / ClickHouse", 11.5, "#dbe6f5", mono=True)
                + T(760, 198, "经 Iceberg 协议接入", 10.5, "#6b7d99")
                + T(760, 240, "Databricks Runtime", 11.5, "#dbe6f5", mono=True)
                + T(760, 264, "闭源增强：Photon /", 10.5, "#6b7d99")
                + T(760, 286, "Predictive Optimize", 10.5, "#6b7d99")
                + T(760, 320, "Kernel 让读不再绑定", 10.5, "#8fa5c8")
                + T(760, 344, "Spark 版本", 10.5, "#8fa5c8")
                + A(310, 145, 380, 145, "读日志", color="#5f7ba6", dash=True, lx=345, ly=136)
                + A(310, 325, 380, 325, "读日志", color="#5f7ba6", dash=True, lx=345, ly=316)
                + A(680, 145, 740, 145, "暴露表", color="#5f7ba6", lx=710, ly=136)
            ))),
        ]),
        ("UniForm 的意义", [
            "UniForm 让一张 Delta 表在对象存储上同时呈现为 Iceberg 表（元数据异步物化）：Trino/ClickHouse 等只讲 Iceberg 协议的引擎可以零拷贝接入。这与 Hudi 生态的互操作方向一致——<strong>表格式之争正在变成互操作之争</strong>。",
        ]),
    ],
    cards=[
        ("#4f8cff", "Kernel", ["Rust 实现 + Java 封装", "只做读：日志重放 + 扫描", "写仍走 Spark 命令"]),
        ("#a78bfa", "UniForm", ["IcebergCompat 开关", "异步生成 Iceberg 元数据", "Hudi 双向互通"]),
        ("#34d399", "流与目录", ["setTransaction 恰好一次", "Catalog 绑定 UC/Glue", "streaming table / CDC 视图"]),
    ],
))
