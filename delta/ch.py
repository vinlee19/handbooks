# -*- coding: utf-8 -*-
"""Delta Lake 手册 8 章内容。"""
from site_fw import B, A, T, R, FIG

CD = "#4f8cff"
CY = "#fbbf24"
CG = "#34d399"
CP = "#a78bfa"
CR = "#fb7185"

CHAPTERS = []

# ---------------- 01 总体架构 ----------------
CHAPTERS.append(dict(
    file="01-overview.html", title="Delta Lake 总体架构：以事务日志为唯一真相",
    kicker="DELTA LAKE SOURCE STUDY · CH 01",
    sub="Delta Lake 的全部魔法浓缩成一句话：<strong>一张表就是一个事务日志目录（_delta_log）</strong>。提交 = 追加一个 JSON 文件，读取 = 重放日志构建快照。本手册基于 spark/src/main/scala/org/apache/spark/sql/delta 的逐模块分析，把这条主线拆开看透。",
    stats=[("1 目录", "_delta_log 即表"), ("7 类", "核心 action"), ("OCC", "乐观并发提交"), ("2 内核", "Spark + Rust Kernel")],
    sections=[
        ("要解决什么问题", [
            "对象存储上的 Parquet 目录没有事务：并发写互相覆盖、更新只能全量重写、无法回滚。Delta Lake 用<strong>预写日志（Write-Ahead Log）</strong>解决：每次提交是一个原子可见的 JSON 文件，记录「新增了哪些文件、删除了哪些文件、元数据如何变化」。",
            "这条设计让 Delta 用最朴素的文件语义获得了 ACID，也让 Time Travel、Schema 演进、审计成为免费副产品。",
        ]),
        ("总体架构图", [
            ("fig", FIG("delta-arch", "图 1-1 · Delta 总体架构：引擎、事务日志与数据文件", 1040, 520, (
                T(30, 38, "DELTA ARCHITECTURE · 架构总览", 13, "#8fa5c8", True)
                + B(40, 90, 220, 96, "#121a30", "#31435f", "查询/写入引擎", "Spark · Flink · Trino")
                + T(60, 152, "经 DeltaTableV2 / Catalog 接入", 11, "#6b7d99")
                + B(40, 220, 220, 80, "#16202f", "#3a5a75", "DeltaLog", "DeltaLog.scala")
                + B(340, 90, 260, 110, "#0f2438", CD, "_delta_log/", "N.json + N.checkpoint.parquet", tcolor=CD)
                + T(360, 160, "actions: add/remove/meta…", 11.5, "#8fa5c8", mono=True)
                + T(360, 180, "唯一真相 · 原子可见", 11.5, CY, mono=True)
                + B(340, 240, 260, 90, "#121a30", "#31435f", "Snapshot", "重放日志的内存视图")
                + T(360, 298, "SnapshotManagement 构建", 11, "#6b7d99")
                + B(680, 90, 320, 130, "#121a30", "#31435f", "数据文件（Parquet）", "add/remove 引用的物理文件")
                + T(700, 150, "文件本身不可变", 12, "#dbe6f5", True)
                + T(700, 174, "删除 = remove action（逻辑删）", 11.5, "#8fa5c8")
                + T(700, 196, "Vacuum 才物理清理", 11.5, "#8fa5c8")
                + B(680, 260, 320, 110, "#1a1430", CP, "OptimisticTransaction", "提交前冲突校验 ConflictChecker")
                + T(700, 318, " OCC + 隔离级别可配置", 11.5, "#8fa5c8")
                + B(680, 410, 320, 90, "#0f2a1c", CG, "Checkpoints / Checksum", "加速快照构建")
                + A(260, 138, 340, 138, "读写日志", color="#5f7ba6")
                + A(470, 200, 470, 240, "重放", color="#5f7ba6", lx=520)
                + A(600, 138, 680, 138, "引用文件", color="#5f7ba6")
                + A(260, 260, 340, 270, "构建快照", color="#5f7ba6", dash=True)
                + A(680, 320, 470, 410, "checkpoint", color="#5f7ba6", dash=True, lx=560)
            ))),
            "引擎侧只需要三个能力：原子 put、列出的 List、读文件——这是 Delta Kernel 与各云厂商能广泛建立连接的原因。",
        ]),
        ("仓库地图", [
            "核心在 <code>spark/src/main/scala/org/apache/spark/sql/delta/</code>：actions/（日志协议）、commands/（DML 实现）、OptimisticTransaction、ConflictChecker、Checkpoints、SnapshotManagement、catalog/。独立目录 <code>kernel/</code> 是 Rust 通用内核，<code>connectors/</code> 承载 Flink/Presto。",
        ]),
    ],
    cards=[
        ("#4f8cff", "三大设计", ["日志即表：_delta_log 唯一真相", "数据文件不可变", "提交原子可见"]),
        ("#fbbf24", "免费副产品", ["Time Travel：读旧版本日志", "审计：每次提交有 CommitInfo", "Schema 演进：meta action"]),
        ("#a78bfa", "读源码主线", ["DeltaLog → Snapshot → 算子", "OptimisticTransaction 提交", "ConflictChecker 并发语义"]),
    ],
))

# ---------------- 02 Transaction Log ----------------
CHAPTERS.append(dict(
    file="02-transaction-log.html", title="Transaction Log：七个 action 定义一张表",
    kicker="DELTA LAKE SOURCE STUDY · CH 02",
    sub="<code>_delta_log/00000N.json</code> 里每行一个 action。七个 action（add / remove / meta / protocol / setTransaction / commitInfo / domainMetadata）组合起来，就是 Delta 表在某一刻的完整描述。",
    stats=[("7 类", "核心 action"), ("1 行", "一个 action（JSON）"), ("原子", "文件级可见性"), ("00000N", "零填充版本号")],
    sections=[
        ("action 协议", [
            ("fig", FIG("delta-actions", "图 2-1 · 一次提交的 JSON 内容与各类 action 的职责", 1040, 480, (
                T(30, 38, "TRANSACTION LOG ACTIONS · 000005.json", 13, "#8fa5c8", True)
                + B(40, 80, 300, 66, "#0f2438", CD, "commitInfo", "时间戳 · 操作 · 用户 · 参数", tcolor=CD)
                + B(40, 158, 300, 66, "#121a30", "#31435f", "meta", "schemaString · 分区列 · 配置")
                + B(40, 236, 300, 66, "#121a30", "#31435f", "protocol", "minReader / minWriter 版本")
                + B(400, 80, 300, 66, "#0f2a1c", CG, "add", "path · partitionValues · size · stats", tcolor=CG)
                + B(400, 158, 300, 66, "#2a1414", CR, "remove", "逻辑删除 · deletionTimestamp", tcolor=CR)
                + B(400, 236, 300, 66, "#121a30", "#31435f", "setTransaction", "appId + version 幂等去重")
                + B(760, 80, 240, 130, "#1a1430", CP, "domainMetadata", "表级扩展配置（如 clustering）", tcolor=CP)
                + T(780, 240, "由 actions/ 包定义：", 11, "#8fa5c8")
                + T(780, 262, "AddFile · RemoveFile · Metadata", 11, "#8fa5c8", mono=True)
                + T(780, 284, "SetTransaction · CommitInfo", 11, "#8fa5c8", mono=True)
                + T(780, 306, "Protocol · CheckpointMetadata", 11, "#8fa5c8", mono=True)
                + R(40, 320, 960, 120, "#121a30", 10, "#31435f")
                + T(60, 350, "示例：一次 append 提交 = commitInfo + add×N", 12, "#dbe6f5")
                + T(60, 378, '{"commitInfo":{"timestamp":169...,"operation":"WRITE","operationParameters":{"mode":"Append"}}}', 11, "#8fa5c8", mono=True)
                + T(60, 406, '{"add":{"path":"part-0000....snappy.parquet","size":1024,"dataChange":true}}', 11, "#8fa5c8", mono=True)
                + T(60, 432, "stats 列内嵌 min/max/nullCount → 查询裁剪的原料", 11.5, "#93a5c0")
            ))),
            "每个 action 类定义在 <code>actions/</code> 包（<code>AddFile.scala</code>、<code>RemoveFile.scala</code>、<code>Metadata.scala</code>…），通过 <code>JsonUtils</code> 与 Jackson 映射，<code>Action</code> 伴生对象负责反序列化分发。",
        ]),
        ("可见性与原子性", [
            "对象存储上「文件一旦写完整即完整可见」，因此 Delta 的原子提交 = <strong>写完整个 JSON 再让它出现</strong>。不支持原子重命名的存储（如 S3）靠 LogStore 的实现（S3SingleDriverLogStore + DynamoDB 锁）补齐语义——这就是 <code>LogStore</code> 抽象存在的原因。",
            "<code>dataChange:false</code> 的 add/remove（如 Optimize 产物）不改变逻辑数据，只改变物理布局——增量feed的消费者据此过滤。",
        ]),
    ],
    cards=[
        ("#4f8cff", "七个 action", ["add / remove：文件账本", "meta / protocol：表定义", "setTransaction：幂等流写入"]),
        ("#fbbf24", "stats 的价值", ["min/max/nullCount 内嵌", "查询时数据文件级裁剪", "checkpoint 会聚合这些统计"]),
        ("#a78bfa", "LogStore 抽象", ["HDFS：rename 原子", "S3：DynamoDB 锁补齐", "自定义 SPI 可插拔"]),
    ],
))

# ---------------- 03 Snapshot ----------------
CHAPTERS.append(dict(
    file="03-snapshot.html", title="Snapshot：重放日志构建表的内存视图",
    kicker="DELTA LAKE SOURCE STUDY · CH 03",
    sub="Snapshot 是 Delta 的大脑：把 checkpoint parquet + 增量 JSON 重放成 <strong>activeFiles / tombstones / setTransactions</strong> 三集合，再暴露出分区裁剪、文件列举与 Time Travel 能力。",
    stats=[("3 集合", "active/tombstone/txn"), ("最短路径", "checkpoint + 增量 json"), ("TT", "version AsOf 时间戳"), ("缓存", "SnapshotManagement")],
    sections=[
        ("构建过程", [
            ("fig", FIG("delta-snapshot", "图 3-1 · Snapshot 构建：从 checkpoint 到最新版本的最短重放", 1040, 440, (
                T(30, 38, "SNAPSHOT BUILD · SnapshotManagement.loadSnapshot", 13, "#8fa5c8", True)
                + B(40, 90, 220, 90, "#121a30", "#31435f", "找最近 checkpoint", "CheckpointProvider")
                + B(340, 90, 220, 90, "#0f2438", CD, "读 checkpoint parquet", "全量状态一次性装入", tcolor=CD)
                + B(640, 90, 200, 90, "#121a30", "#31435f", "重放 json", "checkpoint 后的增量")
                + B(880, 90, 120, 90, "#0f2a1c", CG, "Snapshot", "version N", tcolor=CG)
                + B(340, 240, 220, 90, "#1a1430", CP, "_last_checkpoint", "定位起点 · 免 List", tcolor=CP)
                + B(640, 240, 200, 90, "#2a2010", CY, "CRC 校验和", "Checksum.scala 快速一致性验证", tcolor=CY)
                + A(260, 135, 340, 135, "", color="#5f7ba6")
                + A(560, 135, 640, 135, "", color="#5f7ba6")
                + A(840, 135, 880, 135, "", color="#5f7ba6")
                + A(450, 180, 450, 240, "定位", color="#5f7ba6", dash=True, lx=520)
                + A(750, 180, 750, 240, "校验", color="#5f7ba6", dash=True, lx=820)
                + T(60, 380, "activeFiles = add − remove；tombstones 保留用于冲突检测；setTransactions 支撑流式幂等", 12, "#93a5c0")
                + T(60, 408, "Time Travel：直接从目标版本的 checkpoint/json 重放，无需回放全史", 12, "#93a5c0")
            ))),
            "<code>SnapshotManagement</code> 负责缓存在内存中的当前 Snapshot 与历史 Snapshot；<code>CheckpointProvider</code> 用 <code>_last_checkpoint</code> 免 List 定位起点。",
        ]),
        ("Time Travel 与 Schema", [
            "<code>DataFrame.read.format(\"delta\").option(\"versionAsOf\", 5)</code> 或 <code>timestampAsOf</code> 触发历史版本 Snapshot 构建。meta action 携带 <code>schemaString</code>，每个版本自带 schema——列裁剪与分区值映射都基于它。",
            "vacuum 会清理不再被任何保留版本引用的物理文件，因此 Time Travel 的窗口与 <code>delta.deletedFileRetentionDuration</code> 直接相关。",
        ]),
    ],
    cards=[
        ("#4f8cff", "三集合", ["activeFiles：当前有效文件", "tombstones：删除记录（冲突检测用）", "setTransactions：流幂等"]),
        ("#fbbf24", "加速设计", ["_last_checkpoint 免 List", "checkpoint parquet 一次装入", "CRC 校验和防损坏"]),
        ("#a78bfa", "Time Travel", ["versionAsOf / timestampAsOf", "从目标版本 checkpoint 重放", "受 retention 窗口约束"]),
    ],
))

# ---------------- 04 Checkpoint ----------------
CHAPTERS.append(dict(
    file="04-checkpoint.html", title="Checkpoint：让快照构建从 O(日志) 变 O(1)",
    kicker="DELTA LAKE SOURCE STUDY · CH 04",
    sub="日志会无限增长，重放越来越慢。Checkpoint 把全量状态写成结构化 Parquet（可多 part），此后构建快照只需 checkpoint + 少量增量 JSON。",
    stats=[("Parquet", "checkpoint 格式"), ("10 parts", "可并行的分片文件"), ("v2", "sidecar 文件结构"), ("_last_checkpoint", "元信息指针")],
    sections=[
        ("Checkpoint 结构", [
            ("fig", FIG("delta-checkpoint", "图 4-1 · Checkpoint 文件族与 last_checkpoint 元信息", 1040, 420, (
                T(30, 38, "CHECKPOINT · Checkpoints.scala", 13, "#8fa5c8", True)
                + B(40, 90, 300, 90, "#0f2438", CD, "N.checkpoint.parquet", "v1：最多 10 个 part 并行写", tcolor=CD)
                + B(40, 220, 300, 90, "#121a30", "#31435f", "_last_checkpoint", "version · parts · size · checksum")
                + B(420, 90, 300, 90, "#121a30", "#31435f", "v2：sidecar 文件", "大动作溢出到 .sidecar")
                + B(420, 220, 300, 90, "#2a2010", CY, "CRC 校验文件", "快照构建时的完整性校验", tcolor=CY)
                + B(780, 90, 220, 220, "#0f2a1c", CG, "内容 = 全部 action", "active add 集合", tcolor=CG)
                + T(800, 150, "tombstones（截断窗口）", 11, "#8fa5c8")
                + T(800, 172, "setTransactions", 11, "#8fa5c8")
                + T(800, 194, "meta / protocol", 11, "#8fa5c8")
                + T(800, 216, "CheckpointMetadata", 11, "#8fa5c8")
                + T(800, 248, "写入前先写 _last", 10.5, "#6b7d99")
                + T(800, 270, "checkpoint 再原子收尾", 10.5, "#6b7d99")
                + A(340, 135, 420, 135, "v2 溢出", color="#5f7ba6", dash=True)
                + A(190, 180, 190, 220, "指向", color="#5f7ba6", lx=240)
            ))),
            "<code>Checkpoints.scala</code> 的 <code>writeCheckpointFiles</code> 用 Spark 并行写出 parts；v2 checkpoint 引入 sidecar：主 checkpoint 只含少量代表性 action，大体积内容进 sidecar 文件，读取时按需加载。",
        ]),
        ("触发与校验", [
            "默认每 <code>delta.checkpointInterval</code>（10）次提交触发一次；由 <code>OptimisticTransaction.commit</code> 后的 post-commit hook 驱动。checksum（v2）让快照构建后能校验 action 数与文件数是否与上次一致，及早发现损坏。",
        ]),
    ],
    cards=[
        ("#4f8cff", "读路径收益", ["快照构建 O(1) 起步", "免 List 对象存储友好", "并行读多个 part"]),
        ("#fbbf24", "v2 sidecar", ["大 add 集合溢出存储", "主文件保持精简", "按需加载 sidecar"]),
        ("#a78bfa", "一致性", ["CRC 校验和", "_last_checkpoint 先行", "失败可安全重做"]),
    ],
))

# ---------------- 05 乐观事务 ----------------
CHAPTERS.append(dict(
    file="05-optimistic-tx.html", title="乐观事务：OptimisticTransaction 与冲突判定",
    kicker="DELTA LAKE SOURCE STUDY · CH 05",
    sub="所有写入都运行在 <code>OptimisticTransaction</code> 里：读快照做修改，提交时用 <code>ConflictChecker</code> 与并发提交比对，赢者落日志、输者重试或失败。",
    stats=[("OCC", "无锁乐观并发"), ("2 级", "WriteSerializable/Serializable"), ("重试", "冲突自动重试 N 次"), ("幂等", "setTransaction 防重放")],
    sections=[
        ("事务生命周期", [
            ("fig", FIG("delta-txn", "图 5-1 · 事务生命周期：读快照 → 修改 → 校验 → 提交", 1040, 440, (
                T(30, 38, "OPTIMISTIC TRANSACTION · OptimisticTransaction.scala", 13, "#8fa5c8", True)
                + B(40, 90, 230, 90, "#0f2438", CD, "txn 开始", "绑定 Snapshot 版本", tcolor=CD)
                + B(340, 90, 230, 90, "#121a30", "#31435f", "读写文件", "readFiles / touchedFiles 登记")
                + B(640, 90, 200, 90, "#2a2010", CY, "prepareCommit", "组装 action 序列")
                + B(340, 240, 230, 90, "#121a30", "#31435f", "doCommit 循环", "写 json → 失败重试")
                + B(640, 240, 200, 90, "#0f2438", CD, "ConflictChecker", "与并发提交比对", tcolor=CD)
                + B(40, 240, 230, 90, "#0f2a1c", CG, "post-commit", "checkpoint / metrics / UniForm", tcolor=CG)
                + A(270, 135, 340, 135, "", color="#5f7ba6")
                + A(570, 135, 640, 135, "", color="#5f7ba6")
                + A(740, 180, 740, 240, "尝试写入", color="#5f7ba6", lx=800)
                + A(570, 285, 640, 285, "冲突?", color="#5f7ba6")
                + A(455, 240, 455, 180, "赢者重放", color="#5f7ba6", dash=True, lx=380)
                + A(340, 285, 155, 285, "提交成功", color="#5f7ba6", dash=True)
            ))),
            "提交的核心是 <code>doCommitRetryLoop</code>：把 action 写成版本号为 (读取版本 + 重试次数) 的 json；若目标文件已存在（别人先提交），进入 <code>ConflictChecker.checkForReads/Writes</code> 判定能否重试。",
        ]),
        ("冲突判定", [
            "<code>ConflictChecker</code> 区分：并发提交是否读取了我要改的文件（读写冲突）、是否修改了同一批文件（写写冲突）、是否改了 metadata（schema 冲突）。<strong>WriteSerializable</strong>（默认）允许「只读不写」的并发与纯追加并行；Serializable 更严格。",
            "流式查询用 <code>setTransaction(appId, version)</code> 做恰好一次语义：同一 appId 重复提交会被日志直接拒绝——这是 Structured Streaming 的 checkpoint 机制与 Delta 的握手点。",
        ]),
    ],
    cards=[
        ("#4f8cff", "重试策略", ["版本号冲突 → 递增重试", "可重试冲突自动重放", "不可重试抛 ConcurrentModification"]),
        ("#fbbf24", "隔离级别", ["WriteSerializable 默认", "Serializable 全序化", "append-only 快速路径"]),
        ("#a78bfa", "后置钩子", ["checkpoint 触发", "UniForm/Iceberg 同步", "统计与 metrics 上报"]),
    ],
))

# ---------------- 06 DML ----------------
CHAPTERS.append(dict(
    file="06-dml.html", title="DML 实现：Write、Delete、Update、Merge 的物理路径",
    kicker="DELTA LAKE SOURCE STUDY · CH 05+",
    sub="commands/ 包是 Delta 的四肢：四种 DML 最终都翻译成「读相关文件 → 计算新文件集 → 产出 add/remove」。理解这个统一模式，四种语法的源码就只剩各自的优化点。",
    stats=[("4 类", "核心 DML"), ("统一", "add/remove 输出"), ("2 路", "Delete 重写 or DV"), ("Merge", "matched/notMatched 双阶段")],
    sections=[
        ("统一模式", [
            ("fig", FIG("delta-dml", "图 6-1 · DML 统一：四种命令都产出 add/remove 对", 1040, 420, (
                T(30, 38, "DML COMMANDS · commands/ 包", 13, "#8fa5c8", True)
                + B(40, 90, 220, 70, "#0f2438", CD, "WriteIntoDelta", "Append/Overwrite 模式", tcolor=CD)
                + B(40, 180, 220, 70, "#2a1414", CR, "DeleteCommand", "重写 or 删除向量", tcolor=CR)
                + B(40, 270, 220, 70, "#2a1414", CR, "UpdateCommand", "重写受影响文件", tcolor=CR)
                + B(40, 360, 220, 70, "#1a1430", CP, "MergeIntoDelta", "matched/notMatched", tcolor=CP)
                + B(420, 90, 260, 340, "#121a30", "#31435f", "统一物理计划", "读命中文件 → 计算 → 写新文件")
                + T(440, 140, " Delete：全文件命中 → 纯 remove", 11.5, "#8fa5c8")
                + T(440, 168, " 部分命中 → 重写 + DV（deletion vectors）", 11.5, "#8fa5c8")
                + T(440, 196, " Update/Merge：重写受影响文件", 11.5, "#8fa5c8")
                + T(440, 224, " Overwrite：replaceWhere 条件替换", 11.5, "#8fa5c8")
                + T(440, 252, " 动态分区覆写：仅重写匹配分区", 11.5, "#8fa5c8")
                + T(440, 300, "输出统一为 add + remove 对", 12, "#93a5c0")
                + T(440, 328, " OptimisticTransaction 一并提交", 12, "#93a5c0")
                + B(760, 90, 240, 150, "#0f2a1c", CG, "Deletion Vectors", "行级删除位图（覆盖索引区）", tcolor=CG)
                + T(780, 150, "免重写整文件", 11.5, "#8fa5c8")
                + T(780, 174, "puffin 格式附着文件", 11.5, "#8fa5c8")
                + T(780, 198, "读取时按位图过滤", 11.5, "#8fa5c8")
                + B(760, 280, 240, 120, "#121a30", "#31435f", "分区分支", "replaceWhere / dynamic overwrite")
                + T(780, 340, "条件不满足直接失败", 11, "#8fa5c8")
                + T(780, 364, "满足则只写目标分区", 11, "#8fa5c8")
            ))),
        ]),
        ("Merge 的两阶段", [
            "<code>MergeIntoDelta</code> 先用源表 join 目标表找出 matched / notMatched 集合，再分别生成 update/insert 文件；整个 merge 是一次事务（一个版本的 add/remove），失败整体回滚。频繁小 merge 会造成读放大，配合 Optimize 与 DV 收益最佳。",
        ]),
    ],
    cards=[
        ("#4f8cff", "Write", ["Append / Overwrite / replaceWhere", "动态分区覆写", "schema 演进 mergeSchema"]),
        ("#fb7185", "Delete 两路", ["全文件命中 → 纯 remove", "部分命中 → 重写或 DV", "DV 由表属性启用"]),
        ("#a78bfa", "Merge 要点", ["matched/notMatched 两集合", "whenMatched/NotMatched 子句", "一次事务整体可见"]),
    ],
))

# ---------------- 07 表维护 ----------------
CHAPTERS.append(dict(
    file="07-maintenance.html", title="表维护：Optimize、Z-Order 与 Vacuum",
    kicker="DELTA LAKE SOURCE STUDY · CH 07",
    sub="Delta 的维护三板斧：<strong>Optimize</strong> 合并小文件（可选 Z-Order 重排），<strong>Vacuum</strong> 清理孤儿文件，二者都建立在「日志是逻辑真相、文件是物理残留」的二元性上。",
    stats=[("bin-pack", "Optimize 文件合并"), ("Z-Order", "多维聚类重排"), ("默认 7 天", "Vacuum 保留窗口"), ("dry-run", "预览模式")],
    sections=[
        ("Optimize 与 Z-Order", [
            ("fig", FIG("delta-optimize", "图 7-1 · Optimize bin-packing 与 Z-Order 重排", 1040, 400, (
                T(30, 38, "OPTIMIZE / ZORDER · OptimizeTableCommand", 13, "#8fa5c8", True)
                + B(40, 90, 220, 100, "#121a30", "#31435f", "候选文件", "where 谓词选分区")
                + T(60, 148, "小文件按大小分桶", 11, "#8fa5c8")
                + B(340, 90, 220, 100, "#0f2438", CD, "bin-pack 合并", "目标 ~1GB 输出文件", tcolor=CD)
                + B(640, 90, 360, 100, "#1a1430", CP, "Z-Order 重排", "多列交错排序 → 数据局部性", tcolor=CP)
                + T(660, 148, "zOrderCols 先重排行再写文件", 11, "#8fa5c8")
                + T(660, 170, "min/max 统计聚集 → 裁剪增强", 11, "#8fa5c8")
                + B(340, 240, 220, 100, "#121a30", "#31435f", "输出", "dataChange=false 的 add/remove")
                + B(40, 240, 220, 100, "#0f2a1c", CG, "提交", "replacecommit 语义", tcolor=CG)
                + A(260, 140, 340, 140, "", color="#5f7ba6")
                + A(560, 140, 640, 140, "zOrderCols 指定", color="#5f7ba6", dash=True)
                + A(450, 190, 450, 240, "", color="#5f7ba6")
                + A(340, 290, 260, 290, "", color="#5f7ba6")
                + T(60, 380, "Z-Order 的收益来自 stats：重排后每个文件的 min/max 区间更紧，查询裁剪更狠", 12, "#93a5c0")
            ))),
        ]),
        ("Vacuum", [
            "<code>VacuumCommand</code> 列出表目录中所有物理文件，凡不在当前（及保留期内）日志引用且早于 <code>retentionDuration</code>（默认 7 天）的都删除。dry-run 先列出待删清单；保留窗口是 Time Travel 安全边界的另一面。",
        ]),
    ],
    cards=[
        ("#4f8cff", "Optimize", ["bin-pack 小文件合并", "按分区/谓词圈定范围", "dataChange=false 不影响增量"]),
        ("#a78bfa", "Z-Order", ["多维聚类改善局部性", "stats 聚集 → 更强裁剪", "与liquid clustering 演进"]),
        ("#fb7185", "Vacuum", ["删日志未引用的物理文件", "retention 是 TT 安全窗", "dry-run 先看清单"]),
    ],
))

# ---------------- 08 内核与生态 ----------------
CHAPTERS.append(dict(
    file="08-kernel-ecosystem.html", title="通用内核与生态：Kernel、UniForm 与 Catalog",
    kicker="DELTA LAKE SOURCE STUDY · CH 08",
    sub="Delta 正在把「读表」能力下沉到 <strong>Delta Kernel</strong>（Rust/Java 独立库），把「表格式」通过 <strong>UniForm</strong> 同时暴露为 Iceberg/Hudi，让任意引擎零绑定接入——这是理解 Delta 生态演进的两把钥匙。",
    stats=[("Kernel", "Rust 独立读内核"), ("UniForm", "同时是 Iceberg/Hudi"), ("Catalog", "UC/Hive/Glue 绑定"), ("Streaming", "Structured Streaming 深度集成")],
    sections=[
        ("Delta Kernel", [
            ("fig", FIG("delta-kernel", "图 8-1 · Kernel 与 UniForm：把表格式开放给任意引擎", 1040, 400, (
                T(30, 38, "KERNEL & UNIFORM · 开放的表格式", 13, "#8fa5c8", True)
                + B(40, 90, 250, 110, "#0f2438", CD, "Delta Kernel (Rust)", "读日志 + 扫描 Parquet 的最小库", tcolor=CD)
                + T(60, 158, "引擎只需实现文件读取 SPI", 11, "#8fa5c8")
                + B(40, 240, 250, 90, "#121a30", "#31435f", "Java Kernel", "JVM 引擎的轻量接入")
                + B(400, 90, 250, 110, "#1a1430", CP, "UniForm", "一份 delta 日志 → 同时生成 Iceberg 元数据", tcolor=CP)
                + T(420, 158, "IcebergCompatV1/V2 异步转换", 11, "#8fa5c8")
                + B(400, 240, 250, 90, "#121a30", "#31435f", "Hudi 同步", "DeltaStamp 协同")
                + B(760, 90, 240, 240, "#0f2a1c", CG, "接入的引擎", "Spark / Flink / Presto / Trino", tcolor=CG)
                + T(780, 150, "Unity Catalog / Glue / Hive", 11.5, "#8fa5c8")
                + T(780, 174, "Structured Streaming", 11.5, "#8fa5c8")
                + T(780, 198, "Kafka Connect / Flink CDC", 11.5, "#8fa5c8")
                + T(780, 222, "Databricks Runtime", 11.5, "#8fa5c8")
                + T(780, 258, "写路径仍以 Spark 实现为主", 10.5, "#6b7d99")
                + A(290, 145, 400, 145, "读日志", color="#5f7ba6", dash=True)
                + A(290, 285, 400, 285, "读日志", color="#5f7ba6", dash=True)
                + A(650, 145, 760, 145, "暴露表", color="#5f7ba6")
            ))),
        ]),
        ("UniForm 的意义", [
            "UniForm 让一张 Delta 表在对象存储上同时呈现为 Iceberg 表（元数据异步物化）：Trino/ClickHouse 等只讲 Iceberg 协议的引擎可以零拷贝接入。这与 Hudi 生态的互操作方向一致——<strong>表格式之争正在变成互操作之争</strong>。",
        ]),
    ],
    cards=[
        ("#4f8cff", "Kernel", ["Rust 实现 + Java 封装", "只做读：日志重放 + 扫描", "写仍走 Spark 命令"]),
        ("#a78bfa", "UniForm", ["IcebergCompat 开关", "异步生成 Iceberg 元数据", "Hudi 同步双向互通"]),
        ("#34d399", "流与目录", ["setTransaction 恰好一次", "Catalog 抽象绑定 UC/Glue", "streaming table / CDC 视图"]),
    ],
))
