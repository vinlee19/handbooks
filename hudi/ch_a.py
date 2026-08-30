# -*- coding: utf-8 -*-
"""Hudi 手册 01-04 章内容。"""
from site_fw import B, A, T, R, FIG

C = "#00e5cc"   # hudi 主色（青）
CW = "#22d3ee"
CP = "#a78bfa"
CY = "#fbbf24"
CG = "#34d399"
CR = "#fb7185"

CHAPTERS_A = []

# ---------------- 01 总体架构 ----------------
fig_arch = FIG("hudi-arch", "图 1-1 · Hudi 总体架构：写入客户端 → Timeline → 文件布局 → 查询入口（对象存储上同样成立）", 1040, 560, (
    T(30, 38, "HUDI ARCHITECTURE · 架构总览", 13, "#8fa5c8", True)
    # 写入侧
    + R(30, 70, 250, 96, "#121a30", 10, "#31435f")
    + T(48, 96, "写入侧（Write Client）", 12, "#7fc8e8")
    + T(48, 120, "BaseHoodieWriteClient", 13.5, "#dbe6f5", True)
    + T(48, 142, "upsert / insert / delete · Bulk Insert", 11.5, "#6b7d99")
    # 引擎适配
    + R(30, 190, 250, 80, "#16202f", 10, "#3a5a75")
    + T(48, 218, "引擎绑定", 12, "#7fc8e8")
    + T(48, 240, "Spark / Flink / Java 客户端", 12.5, "#c9d9ee")
    # Timeline
    + B(380, 90, 260, 110, "#0f2438", C, "Timeline 时间线", "HoodieActiveTimeline", tcolor=C)
    + T(400, 140, ".commit  .deltacommit  .compaction", 11.5, "#8fa5c8", mono=True)
    + T(400, 160, ".clean  .rollback  .replacecommit", 11.5, "#8fa5c8", mono=True)
    + T(400, 180, "requested → inflight → completed", 11.5, "#fbbf24", mono=True)
    # 文件布局
    + R(380, 240, 260, 130, "#121a30", 10, "#31435f")
    + T(400, 268, "文件布局（表内）", 12, "#7fc8e8")
    + T(400, 292, "FileGroup → FileSlice", 13, "#dbe6f5", True)
    + T(400, 314, "Base File: *.parquet (COW)", 11.5, "#8fa5c8", mono=True)
    + T(400, 334, "Log File: *.log (MOR 追加块)", 11.5, "#8fa5c8", mono=True)
    + T(400, 354, ".hoodie/ 元数据目录", 11.5, "#6b7d99", mono=True)
    # 索引
    + B(380, 410, 260, 100, "#1a1430", CP, "Index 索引", "record key → file group", tcolor=CP)
    + T(400, 470, "BLOOM · BUCKET · HBASE · RECORD_INDEX", 11, "#8fa5c8", mono=True)
    # 查询侧
    + R(760, 90, 250, 110, "#121a30", 10, "#31435f")
    + T(780, 118, "查询侧", 12, "#7fc8e8")
    + T(780, 142, "Snapshot / Read Optimized", 13, "#dbe6f5", True)
    + T(780, 164, "Incremental Query", 13, "#dbe6f5", True)
    + T(780, 186, "Hive/Spark/Presto/Trino InputFormat", 11, "#6b7d99")
    # 表服务
    + R(760, 240, 250, 130, "#16202f", 10, "#3a5a75")
    + T(780, 268, "表服务（Table Services）", 12, "#7fc8e8")
    + T(780, 292, "Compaction（MOR 合并）", 12.5, "#dbe6f5")
    + T(780, 314, "Clustering（小文件整理）", 12.5, "#dbe6f5")
    + T(780, 336, "Clean（清理旧版本）", 12.5, "#dbe6f5")
    + T(780, 358, "由 timeline 驱动 · 可独立部署", 11, "#6b7d99")
    # 并发控制
    + B(760, 410, 250, 100, "#241a12", CY, "并发控制 / ACID", "OCC + Lock Provider", tcolor=CY)
    + T(780, 470, "ConflictChecker · Zookeeper/DDB 锁", 11, "#8fa5c8", mono=True)
    # 箭头
    + A(280, 118, 380, 130, "产生 instant", color="#5f7ba6")
    + A(510, 200, 510, 240, "读取最新 file slice", color="#5f7ba6")
    + A(640, 145, 760, 135, "暴露表视图", color="#5f7ba6")
    + A(280, 230, 380, 440, "查询索引定位", color="#5f7ba6", dash=True)
    + A(640, 460, 760, 450, "写冲突校验", color="#5f7ba6", dash=True)
    + A(510, 410, 510, 370, "compaction 计划/执行", color="#5f7ba6", dash=True, lx=430)
))

CHAPTERS_A.append(dict(
    file="01-overview.html", title="Hudi 总体架构：为湖上增量处理而生",
    kicker="APACHE HUDI SOURCE STUDY · CH 01",
    sub="Hudi 的核心主张是把<strong>数据库的增量语义</strong>带到数据湖上：以 Timeline 为一等公民、以 File Group 组织数据、用 Index 把 record key 绑定到文件组，再由表服务持续整理布局。本手册基于 hudi-client / hudi-common 等模块的逐源码分析，带你看清每一个机制在代码里的位置。",
    stats=[("3 类", "COW/MOR 表 + 元数据表"), ("6 种", "核心 instant action"), ("8+", "索引实现"), ("2 条", "读路径：Ro / Snapshot")],
    sections=[
        ("要解决什么问题", [
            "传统数据湖上只有「整目录扫描」语义：追加一条记录要重写整个分区的 Parquet，更新一条记录更是不可想象。Hudi 用三个机制破解：<strong>Timeline</strong>（把每次变更记录为一条时间线上的 instant）、<strong>File Group + File Slice</strong>（更新只作用于特定文件组，产生新版本切片）、<strong>Index</strong>（把 record key 稳定映射到 file group，更新时才知道该改哪个文件）。",
            "这三个机制分别由 <code>hudi-common/src/main/java/org/apache/hudi/common/table/timeline/</code>、<code>.../common/table/view/</code> 与 <code>org.apache.hudi.index</code> 三个包承载，是读源码的主线索。",
        ]),
        ("总体架构图", [
            ("fig", fig_arch),
            "写入侧只与 Timeline 和 Index 打交道；查询侧通过 FileSystemView 拿到「当前可见的 FileSlice」；表服务（compaction/clustering/clean）作为独立的 timeline 参与者，同样以 instant 的形式留下痕迹——这就是 Hudi 一切组件的统一协作协议。",
        ]),
        ("两种表类型与一条分界", [
            "COW（Copy-On-Write）：每次写都产出新的 Base File（Parquet），读路径纯净但写放大高；MOR（Merge-On-Read）：增量写入 Log File（Avro 追加块），由 compaction 异步合并，写快读慢但可调。<code>HoodieTableType</code> 枚举定义了这两种类型，几乎整个代码库都存在 COW/MOR 的分叉。",
            ("co", "读源码先记住：COW 的提交动作是 .commit，MOR 是 .deltacommit；compaction 只属于 MOR；clustering 两者皆有（.replacecommit）。"),
        ]),
        ("仓库模块地图", [
            "hudi-common 是地基（timeline/文件布局/日志块/文件系统视图）；hudi-client 是写侧引擎（BaseHoodieWriteClient、compactor、clustering）；hudi-spark-datasource / hudi-flink-datasource 是引擎绑定；hudi-hadoop-mr 提供 Hive/Presto 的 InputFormat；hudi-aws / hudi-gcp 是云存储与锁的实现。",
            "另一个容易忽略的模块是 <strong>元数据表（Metadata Table, MDT）</strong>：把文件列表、bloom filter 甚至 record index 挪进一张 Hudi 表，避免对象存储的昂贵 List 与 bloom 读取（<code>org.apache.hudi.metadata.HoodieBackedTableMetadata</code>）。",
        ]),
    ],
    cards=[
        ("#00e5cc", "读源码的三条主线", ["Timeline：common/table/timeline/", "文件视图：common/table/view/", "索引：org.apache.hudi.index"]),
        ("#a78bfa", "两种表类型", ["COW：写放大低延迟读，.commit", "MOR：写快，.deltacommit + compaction", "分叉点几乎遍布所有写入代码"]),
        ("#fbbf24", "统一协作协议", ["一切变更都是 timeline 上的 instant", "表服务也是 instant 参与者", "并发控制围绕 instant 提交展开"]),
    ],
))

# ---------------- 02 Timeline ----------------
fig_tl = FIG("hudi-timeline", "图 2-1 · Timeline 状态机：每个 instant 走完 requested → inflight → completed；崩溃后 inflight 可 rollback 重放", 1040, 460, (
    T(30, 38, "TIMELINE STATE MACHINE · 时间线状态机", 13, "#8fa5c8", True)
    + B(60, 120, 240, 90, "#0f2438", C, "requested", "*.requested 文件", tcolor=C)
    + T(80, 178, "调度阶段：compaction 先写计划", 11, "#6b7d99")
    + B(420, 120, 240, 90, "#2a2010", CY, "inflight", "*.inflight 文件", tcolor=CY)
    + T(440, 178, "执行阶段：崩溃后可回滚", 11, "#6b7d99")
    + B(780, 120, 220, 90, "#0f2a1c", CG, "completed", "直接重命名落地", tcolor=CG)
    + T(800, 178, "对外可见的时间点", 11, "#6b7d99")
    + A(300, 165, 420, 165, "transitionState", color="#5f7ba6")
    + A(660, 165, 780, 165, "transitionState", color="#5f7ba6")
    # 底部：文件形态
    + R(60, 260, 940, 150, "#121a30", 10, "#31435f")
    + T(80, 290, ".hoodie/ 目录（HoodieTableMetaClient 读取）", 12, "#7fc8e8")
    + T(80, 318, "20240115103000000.commit.requested", 12, "#8fa5c8", mono=True)
    + T(80, 342, "20240115103000000.commit.inflight → 20240115103000000.commit（重命名完成）", 12, "#8fa5c8", mono=True)
    + T(80, 366, "文件内容 = HoodieCommitMetadata（avro/json 序列化：分区路径、写统计、fileId 列表）", 11.5, "#6b7d99")
    + T(80, 394, "时间戳即 instant time：HoodieActiveTimeline 按字典序 = 时间序", 11.5, "#93a5c0")
))

CHAPTERS_A.append(dict(
    file="02-timeline.html", title="Timeline：把每一次变更变成时间线上的一个点",
    kicker="APACHE HUDI SOURCE STUDY · CH 02",
    sub="Timeline 是 Hudi 的心跳。所有写入、compaction、clean、rollback 都是时间线上的一个 <strong>instant</strong>（动作 + 状态 + 时间戳）。理解 Timeline 的状态机与文件形态，就理解了 Hudi 的 ACID、崩溃恢复与表服务调度。",
    stats=[("3", "instant 状态"), ("6+", "核心 action 类型"), ("O(1)", "按时间戳定位"), ("1", ".hoodie 元数据目录")],
    sections=[
        ("Instant 的三要素", [
            "<code>HoodieInstant</code> = <strong>action</strong>（做什么：commit/deltacommit/compaction/clean/rollback/replacecommit/savepoint）+ <strong>state</strong>（做到哪：requested/inflight/completed）+ <strong>timestamp</strong>（何时：形如 20240115103000000 的字符串）。三者的组合唯一确定一次表变更。",
            "<code>HoodieTimeline</code> 接口提供过滤与遍历：<code>filterCompletedInstants()</code>、<code>filterInflights()</code>、<code>lastInstant()</code>、<code>nthInstant(n)</code>、<code>findInstantsBeforeOrEquals(ts)</code> 等。查询路径几乎总是先取 <code>metaClient.getActiveTimeline</code> 再过滤 completed。",
        ]),
        ("状态机与崩溃恢复", [
            ("fig", fig_tl),
            "关键设计：completed 文件由 inflight <strong>原子重命名</strong>而来。因此「存在 completed 即成功、只有 inflight 即未完成」，崩溃恢复时 Hudi 对 inflight 走 rollback（写 rollback instant）或按配置重放。<code>HoodieActiveTimeline</code> 的 <code>transitionState()</code> 与 <code>saveAsComplete()</code> 是状态迁移的仅有入口。",
        ]),
        ("元数据内容与 Schema", [
            "commit 文件的内容是 <code>HoodieCommitMetadata</code>（avro 序列化，json 兼容）：按分区汇总写入统计、每个 fileGroup 的变更、compaction/cluster 的输入输出。replacecommit 额外携带被替换删除的文件（clustering 与 partition 迁移都用它）。",
            "时间线增长由 <strong>archival</strong> 控制：<code>HoodieArchivedTimeline</code> 把老 instant 打包进元数据表的归档分区，active timeline 只保留最近窗口。",
        ]),
        ("源码坐标", [
            "核心类：<code>common/table/timeline/HoodieInstant.java</code>、<code>HoodieTimeline.java</code>（接口 + 默认实现 <code>HoodieDefaultTimeline</code>）、<code>HoodieActiveTimeline.java</code>（存储 IO）。表配置：<code>HoodieTableConfig</code>；入口：<code>HoodieTableMetaClient</code>。",
        ]),
    ],
    cards=[
        ("#00e5cc", "为什么用重命名", ["重命名在对象存储上近似原子", "completed 存在 = 提交成功", "inflight 残留 = 可判定崩溃"]),
        ("#fbbf24", "常见 action", ["commit / deltacommit：数据写入", "compaction / log compaction", "clean / rollback / savepoint / replacecommit"]),
        ("#a78bfa", "时间线与查询", ["查询只认 completed instant", "Time Travel = 指定 instant time", "Incremental = 起止 instant 区间"]),
    ],
))

# ---------------- 03 文件布局 ----------------
fig_layout = FIG("hudi-layout", "图 3-1 · 文件布局：FileGroup 是身份，FileSlice 是版本；MOR 在切片内追加 log", 1040, 500, (
    T(30, 38, "FILE LAYOUT · 分区 / 文件组 / 文件切片", 13, "#8fa5c8", True)
    # 分区
    + B(40, 90, 220, 300, "#121a30", "#31435f", "partition=2024-01-15/", "物理目录（对象存储=前缀）")
    + T(60, 130, "filegroup-1", 12, "#7fc8e8")
    + T(60, 152, "filegroup-2", 12, "#7fc8e8")
    + T(60, 174, "filegroup-3", 12, "#7fc8e8")
    + T(60, 210, "fileId 一旦生成永不改变，", 10.5, "#6b7d99")
    + T(60, 228, "更新永远落在同一 fileGroup", 10.5, "#6b7d99")
    + T(60, 264, ".hoodie/ 与分区同级", 10.5, "#6b7d99", mono=True)
    + T(60, 282, "_metadata 表另立门户", 10.5, "#6b7d99", mono=True)
    # filegroup-1 的切片
    + R(320, 90, 320, 300, "#0f2438", 10, "#31435f")
    + T(340, 118, "fileGroup-1 的切片演进", 12, "#7fc8e8")
    + B(340, 136, 130, 52, "#0e2a20", CG, "slice v1", "base v1.parquet", tcolor=CG)
    + T(340, 212, "COW：v2 是全新 parquet", 11, "#8fa5c8")
    + B(340, 226, 130, 52, "#0e2a20", CG, "slice v2", "base v2.parquet", tcolor=CG)
    + T(340, 302, "base 不可变 · 切片切换靠 commit", 10.5, "#6b7d99")
    # MOR 追加
    + R(700, 90, 300, 300, "#121a30", 10, "#31435f")
    + T(720, 118, "MOR：slice v3 追加中", 12, "#7fc8e8")
    + B(720, 136, 130, 52, "#0e2a20", CG, "base v3", "parquet", tcolor=CG)
    + B(720, 200, 240, 46, "#241a12", CY, ".log_1 队列块", "AVRO_DATA_BLOCK", tcolor=CY, mono=True)
    + B(720, 254, 240, 46, "#241a12", CY, ".log_2 删除块", "DELETE_BLOCK", tcolor=CY, mono=True)
    + T(720, 330, "compaction 把 base+log 合成新 base", 10.5, "#6b7d99")
    + T(720, 350, "FileSlice = base + 其后全部 log", 10.5, "#93a5c0")
    # 箭头
    + A(260, 140, 320, 140, "", color="#5f7ba6")
    + A(470, 188, 470, 226, "新 commit", color="#5f7ba6", lx=520)
    + A(640, 240, 700, 240, "MOR 写入", color="#5f7ba6")
))

CHAPTERS_A.append(dict(
    file="03-file-layout.html", title="文件布局：FileGroup、FileSlice 与 Log File",
    kicker="APACHE HUDI SOURCE STUDY · CH 03",
    sub="Hudi 的目录布局刻意保持「分区/文件组/切片」三层：fileId 是记录的身份，commit 是切片的版本。COW 用整文件替换表达更新，MOR 用追加日志表达增量——两者共享同一套视图抽象。",
    stats=[("3 层", "partition → filegroup → slice"), ("不可变", "base file 一旦写出不再修改"), ("5 种", "log block 类型"), ("1", "FileSystemView 缓存视图")],
    sections=[
        ("FileGroup：身份绑定", [
            "一个 <strong>FileGroup</strong> 由唯一 fileId 标识，生命周期内不换名。索引层（CH06）把 record key 映射到 fileId，从而保证「同 key 更新永远落在同一文件组」——这是 Hudi 避免全表扫描做更新的根本。",
            "<strong>FileSlice</strong> 是 fileGroup 在某个 instant 的版本：= 一个 base file（COW 必有）+ 其后追加的所有 log file（MOR）。新 commit 产生新 slice，旧 slice 在 clean 之前仍可被 Time Travel / 增量查询引用。",
        ]),
        ("布局图解", [
            ("fig", fig_layout),
            "Base File 是不可变 Parquet；Log File（<code>.log_N</code>）由 <code>HoodieLogFormatWriter</code> 顺序追加，每个 block 自带头部（含 instantTime、schema、block 类型）。读取时 <code>HoodieLogFormatReader</code> 逐块反序列化。",
        ]),
        ("Log Block 类型", [
            "<code>HoodieLogBlock</code> 家族：AVRO_DATA_BLOCK（数据）、DELETE_BLOCK（整行删除）、COMMAND_BLOCK（rollback 指令）、CORRUPT_BLOCK（损坏占位）、HFILE_DATA_BLOCK。block 头部带 magic 六字节（<code>HOODIE_MAGIC</code>）用于扫描定位与损坏跳过。",
            "视图层 <code>common/table/view/</code> 把这些物理事实组装成逻辑视图：<code>HoodieTableFileSystemView</code> 按 (partition, fileId) 缓存 <code>FileSlice</code>，提供 <code>getLatestFileSlice()</code>、<code>getLatestBaseFile()</code> 等 API——查询与 compaction 调度都建立在它之上。",
        ]),
    ],
    cards=[
        ("#00e5cc", "不变量", ["fileId 永不变名", "base file 不可变", "新版本 = 新文件"]),
        ("#fbbf24", "MOR 的追加", ["block 头带 HOODIE_MAGIC", "数据/删除/命令分块", "compaction 消费 base+log"]),
        ("#a78bfa", "视图层", ["FileSystemView 缓存切片", "查询只看最新 completed 视图", "增量查询按 instant 区间取切片"]),
    ],
))

# ---------------- 04 写路径 COW ----------------
fig_cow = FIG("hudi-cow", "图 4-1 · COW 写入流水线：index 打标 → 分区分组 → 执行替换 → 提交", 1040, 520, (
    T(30, 38, "COW WRITE PIPELINE · 以 upsert 为例", 13, "#8fa5c8", True)
    + B(40, 90, 190, 80, "#121a30", "#31435f", "HoodieRecord 流", "HoodieKey + payload")
    + B(280, 90, 200, 80, "#0f2438", C, "① Index.lookup", "key → fileId 位置", tcolor=C)
    + B(540, 90, 200, 80, "#121a30", "#31435f", "② WorkloadProfile", "update/insert 分组统计")
    + B(40, 220, 200, 80, "#121a30", "#31435f", "③ 分区执行器", "UpsertPartitioner")
    + B(280, 220, 200, 80, "#0f2438", C, "④ 写新 base", "HoodieCreateHandle", tcolor=C)
    + B(540, 220, 200, 80, "#2a2010", CY, "⑤ Marker", "防部分写：先立 marker", tcolor=CY)
    + B(40, 350, 200, 80, "#121a30", "#31435f", "⑥ WriteStatus", "统计 + 错误收集")
    + B(280, 350, 200, 80, "#0f2438", C, "⑦ commit", "HoodieCommitMetadata", tcolor=C)
    + B(540, 350, 200, 80, "#2a2010", CY, "⑧ 冲突校验", "ConflictChecker + 锁", tcolor=CY)
    + B(40, 450, 200, 50, "#0f2a1c", CG, "completed instant", "表对外可见", tcolor=CG)
    + A(230, 130, 280, 130, "", color="#5f7ba6")
    + A(480, 130, 540, 130, "", color="#5f7ba6")
    + A(640, 170, 640, 220, "驱动", color="#5f7ba6", dash=True, lx=700)
    + A(240, 130, 40, 220, "tagLocation", color="#5f7ba6", dash=True, lx=100)
    + A(240, 260, 280, 260, "", color="#5f7ba6")
    + A(480, 260, 540, 260, "", color="#5f7ba6")
    + A(140, 300, 140, 350, "", color="#5f7ba6")
    + A(240, 390, 280, 390, "", color="#5f7ba6")
    + A(480, 390, 540, 390, "", color="#5f7ba6")
    + A(240, 430, 40, 470, "发布", color="#5f7ba6", dash=True)
))

CHAPTERS_A.append(dict(
    file="04-cow-write.html", title="COW 写路径：从 upsert 到一次原子提交",
    kicker="APACHE HUDI SOURCE STUDY · CH 04",
    sub="COW 的写路径是一条经典的「索引打标 → 工作负载画像 → 分区器派发 → 写新文件 → 打点防泄漏 → 提交」流水线。<code>BaseHoodieTableServiceClient</code> 是它的骨架，理解这条链就理解了 Hudi 写侧 80% 的代码。",
    stats=[("8 步", "upsert 主流程"), ("2 类", "insert 与 update 分组"), ("原子", "marker + commit 双保险"), ("OCC", "提交时冲突校验")],
    sections=[
        ("主流程", [
            ("fig", fig_cow),
            "<code>BaseHoodieTableServiceClient.upsert()</code> 首先调 <code>index.tagLocation()</code>：对每条 HoodieRecord 查它属于哪个 fileId（不存在则标为 insert）。随后 <code>WorkloadProfile</code> 按「是否命中已有 fileGroup」把工作分成 update 与 insert 两组，交给 <code>UpsertPartitioner</code> 生成 Spark 任务。",
        ]),
        ("写文件与防部分写", [
            "<strong>COW 的更新 = 重写整个 base file</strong>：<code>HoodieMergeHandle</code> 读旧 slice、与新记录合并、由 <code>HoodieCreateHandle</code> 写出新 parquet。insert 走 <code>HoodieCreateHandle</code> 直接新建 fileGroup（受小文件策略 <code>SmallFileAssignPolicy</code> 影响可能填进旧组）。",
            "对象存储没有原子重命名，Hudi 用 <strong>marker 机制</strong>防部分写：写每个文件前先落 marker（<code>marker/marker-type/</code>），提交前 <code>MarkerFiles</code> 校验「所有 marker 都有对应数据文件」，否则判定失败并清理，杜绝读到半成品。",
        ]),
        ("提交与冲突", [
            "全部 WriteStatus 汇总成 <code>HoodieCommitMetadata</code>；提交前经 <code>TransactionManager</code> 取锁、<code>ConflictChecker</code> 与并发 instant 比对（CH08），通过后 transitionState 到 completed。",
            "Bulk Insert 与 Delete 复用同一骨架，只是 partitioner 与 handle 不同；<code>replacecommit</code> 用于 clustering 与整分区替换（<code>HoodieReplaceCommitMetadata</code>）。",
        ]),
    ],
    cards=[
        ("#00e5cc", "骨架类", ["BaseHoodieTableServiceClient", "SparkRDDWriteClient 引擎绑定", "HoodieWriteConfig 全参数"]),
        ("#fbbf24", "两个保护", ["Marker：防部分写泄漏", "ConflictChecker：提交时 OCC", "锁提供者可插拔"]),
        ("#a78bfa", "调优入口", ["小文件：SmallFileAssignPolicy", "并行度：insert/upsert shuffle", "写放大：compaction 触发参数"]),
    ],
))
