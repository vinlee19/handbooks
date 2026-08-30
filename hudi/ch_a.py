# -*- coding: utf-8 -*-
"""Hudi 手册 01-04 章内容（深度版）。"""
from site_fw import B, A, T, R, FIG

C = "#00e5cc"
CP = "#a78bfa"
CY = "#fbbf24"
CG = "#34d399"
CR = "#fb7185"
CB = "#38bdf8"

CHAPTERS_A = []

# ================ 01 总体架构 ================
fig_overview = FIG("hudi-arch", "图 1-1 · Hudi 总体架构：五个参与方围绕 Timeline 协作（所有交互都以 instant 为协议单位）", 1040, 620, (
    # 顶部标题
    T(30, 40, "HUDI ARCHITECTURE · 五个参与方 · 一条时间线", 13, "#8fa5c8", True)
    # 左上：写入客户端
    + R(30, 70, 280, 130, "#121a30", 10, "#31435f")
    + T(50, 98, "① 写入客户端", 12, "#7fc8e8", True)
    + T(50, 124, "BaseHoodieWriteClient", 13, "#dbe6f5", True, mono=True)
    + T(50, 148, "upsert / insert / delete / bulk_insert", 11, "#8fa5c8", mono=True)
    + T(50, 172, "调用 index.tagLocation 打位置标", 11, "#6b7d99")
    # 中上：Timeline（核心，放大）
    + R(380, 60, 300, 150, "#0f2438", 10, C)
    + T(400, 88, "② Timeline 时间线（核心）", 12.5, C, True)
    + T(400, 112, "HoodieActiveTimeline / HoodieInstant", 11.5, "#dbe6f5", mono=True)
    + T(400, 136, "action: commit · deltacommit", 11, "#8fa5c8", mono=True)
    + T(400, 156, "         compaction · clean · rollback", 11, "#8fa5c8", mono=True)
    + T(400, 180, "state: requested → inflight → completed", 11, CY, mono=True)
    + T(400, 198, ".hoodie/ 元数据目录（avro/json）", 10.5, "#6b7d99", mono=True)
    # 右上：查询
    + R(750, 70, 260, 130, "#121a30", 10, "#31435f")
    + T(770, 98, "③ 查询引擎", 12, "#7fc8e8", True)
    + T(770, 124, "Snapshot / ReadOptimized / Incremental", 11.5, "#dbe6f5", mono=True)
    + T(770, 148, "经 FileSystemView 选文件", 11, "#6b7d99")
    + T(770, 172, "Hive/Presto/Trino/Spark/Flink", 11, "#6b7d99", mono=True)
    # 左下：索引
    + R(30, 260, 280, 120, "#1a1430", 10, CP)
    + T(50, 288, "④ Index 索引", 12, CP, True)
    + T(50, 312, "record key → fileGroup 映射", 12, "#dbe6f5")
    + T(50, 336, "BLOOM · BUCKET · HBASE · RECORD_INDEX", 10.5, "#8fa5c8", mono=True)
    + T(50, 360, "canIndexLogFiles / isGlobal 开关", 10.5, "#6b7d99", mono=True)
    # 中下：文件布局
    + R(380, 260, 300, 120, "#121a30", 10, "#31435f")
    + T(400, 288, "⑤ 文件布局", 12, "#7fc8e8", True)
    + T(400, 312, "FileGroup → FileSlice → Base/Log", 12.5, "#dbe6f5", mono=True)
    + T(400, 336, "base 不可变；MOR 追加 .log 块", 11, "#6b7d99")
    + T(400, 360, "FileSystemView 组装可见视图", 11, "#6b7d99")
    # 右下：表服务
    + R(750, 260, 260, 120, "#121a30", 10, "#31435f")
    + T(770, 288, "⑥ 表服务 Table Services", 12, "#7fc8e8", True)
    + T(770, 312, "Compaction · Clustering · Clean", 11.5, "#dbe6f5", mono=True)
    + T(770, 336, "同样以 instant 留痕", 11, "#6b7d99")
    + T(770, 360, "可 inline 也可独立部署", 11, "#6b7d99")
    # 底部横条：并发控制
    + R(30, 430, 980, 110, "#241a12", 10, CY)
    + T(50, 458, "⑦ 并发控制（贯穿所有参与方）", 12, CY, True)
    + T(50, 484, "提交前：TransactionManager 取锁（Zookeeper / DynamoDB / FileSystem 可插拔）", 11.5, "#dbe6f5")
    + T(50, 508, "提交时：ConflictChecker 与并发 instant 比对文件集 → 相交失败 / 不相交提交", 11.5, "#dbe6f5")
    + T(50, 530, "原子性：completed instant 的原子重命名 —— 锁只保护临界区，真相在 timeline", 11.5, "#8fa5c8")
    # 箭头（全部走空白走廊）
    + A(310, 120, 380, 120, "产生 instant", color="#5f7ba6", lx=345, ly=112)
    + A(680, 120, 750, 120, "暴露视图", color="#5f7ba6", lx=715, ly=112)
    + A(170, 200, 170, 260, "查询索引", color="#5f7ba6", dash=True, lx=170, ly=235)
    + A(310, 300, 380, 300, "定位 fileGroup", color="#5f7ba6", dash=True, lx=345, ly=292)
    + A(530, 210, 530, 260, "版本演进", color="#5f7ba6", lx=600, ly=240)
    + A(680, 320, 750, 320, "整理布局", color="#5f7ba6", dash=True, lx=715, ly=312)
))

CHAPTERS_A.append(dict(
    file="01-overview.html", title="Hudi 总体架构：为湖上增量处理而生",
    kicker="APACHE HUDI SOURCE STUDY · CH 01",
    sub="传统数据湖的目录里只有一堆不可变的 Parquet：追加一条记录要重写整个分区，更新一条记录无从谈起，并发写互相覆盖。Hudi（Hadoop Upserts Deletes and Incrementals）用三个正交机制破解这三个问题，并把它们统一在一条时间线协议之下。本章先建立全局心智模型，后续章节再逐层深入源码。",
    stats=[("3 层", "Timeline/布局/索引 核心抽象"), ("2 类", "COW / MOR 表类型"), ("6+", "instant action 类型"), ("19.7k+", "hudi-common 核心行数")],
    sections=[
        ("三个问题与三个机制", [
            "<strong>问题一：更新与删除。</strong>对象存储上的 Parquet 文件不可变，改一条记录唯一的办法是重写整个文件。Hudi 的答案是 <strong>FileGroup + FileSlice</strong>：把「记录住在哪里」稳定下来（fileId 永不变名），更新时只重写该文件组对应的文件，其他文件毫发无损。",
            "<strong>问题二：更新的定位。</strong>要改一条记录，得先知道它在哪个文件里。全表扫描定位太贵，Hudi 引入 <strong>Index</strong>：把 record key 映射到 fileGroup 的映射关系持久化下来（bloom filter / bucket 哈希 / 外部 KV / 元数据表），写入前用 <code>index.tagLocation()</code> 一次性打标。",
            "<strong>问题三：并发与一致性。</strong>多个写客户端同时提交，谁赢？Hudi 引入 <strong>Timeline</strong>：每次提交是时间线上的一个 instant，文件以「重命名」原子可见，提交前用 OCC 冲突校验——文件集不相交即可并行。时间线还顺带解决了崩溃恢复（inflight 残留可判定）与增量消费（instant 区间即变更集）。",
            ("co", "一句话心智模型：Timeline 记录「何时发生了什么」，FileGroup 回答「数据住在哪里」，Index 回答「怎么找到它」。三者正交，其余一切都是实现细节。"),
        ]),
        ("总体架构图", [
            ("fig", fig_overview),
            "图中七个参与方的每一次交互，最终都会落到 timeline 上的某个 instant：写入客户端产生 commit/deltacommit；表服务产生 compaction/clustering/clean；rollback 产生回滚 instant。查询引擎是唯一的「只读者」，它通过 FileSystemView 消费 completed instant 之后的稳定视图。",
        ]),
        ("COW 与 MOR：一条分界线贯穿全库", [
            "Hudi 支持两种表类型，由 <code>HoodieTableType</code> 枚举定义：<strong>COW（Copy-On-Write）</strong> 每次 upsert 重写受影响 fileGroup 的整个 base file，读路径只有 Parquet、纯净高效，但写放大高；<strong>MOR（Merge-On-Read）</strong> 把增量追加为 log file（Avro 块），由 compaction 服务异步合并成新 base，写入秒级返回，代价是读时需要合并。",
            "这条分界线在源码里随处可见：COW 的提交动作是 <code>.commit</code>，MOR 是 <code>.deltacommit</code>；<code>HoodieTable</code> 的实现类分叉为 <code>HoodieSparkCopyOnWriteTable</code> / <code>HoodieSparkMergeOnReadTable</code>；甚至查询侧也有专门的 Read Optimized 视图（只看完成 compaction 的纯 base）。",
            "选型经验：高频小批量更新（CDC 秒级同步）选 MOR；批处理为主、下游是 OLAP 直查选 COW。两者可以在同一张表上通过复制转换。",
        ]),
        ("仓库模块地图（逐目录）", [
            "<code>hudi-common</code> 是地基：timeline/（instant 与存储 IO）、table/（MetaClient、TableConfig）、table/view/（FileSystemView）、log/（日志块读写）、metadata/（元数据表 MDT）。它不依赖任何计算引擎。",
            "<code>hudi-client</code> 是写侧：BaseHoodieWriteClient / BaseHoodieTableServiceClient 骨架、index/ 各索引实现、transaction/（锁与冲突校验）、marker/（防部分写）、action 具体执行器（compactor、clustering）。<code>hudi-spark-datasource</code> / <code>hudi-flink-datasource</code> 是引擎绑定层；<code>hudi-hadoop-mr</code> 提供 Hive/Presto 的 InputFormat；<code>hudi-aws</code>、<code>hudi-gcp</code> 提供云上锁与存储实现；<code>hudi-cli</code> 是运维工具。",
            "还有一个横切模块值得单独记住：<strong>Metadata Table（MDT）</strong>（<code>org.apache.hudi.metadata.HoodieBackedTableMetadata</code>）。它本身是一张小 Hudi 表，托管三类信息：文件列表（免对象存储 List）、bloom filter（免读文件 footer）、record index（key→位置）。对象存储时代它几乎是必开项。",
        ]),
        ("贯穿全库的四个设计决策", [
            "<strong>① 一切皆 instant。</strong>数据写入与表服务共用一套提交协议，这让 compaction 可以独立部署在异构引擎上，也让运维操作（clean/rollback）天然可审计可重放。",
            "<strong>② 物理不可变。</strong>base file 写出后不再修改，更新 = 新文件 + timeline 记录。这把一致性难题转化为「重命名 + 引用切换」，完美适配对象存储。",
            "<strong>③ 视图层解耦。</strong>查询和表服务都不直接碰文件系统，而是问 FileSystemView 要「某个 fileGroup 在某个 instant 的切片」。物理布局因此可以自由演进（v6 format 的 timed layout 等）。",
            "<strong>④ 增量一等公民。</strong>任何消费者都可以按 instant 区间拉取变更（incremental query / CDC），不需要额外构建变更管道——写入时留下的元数据已经足够。",
        ]),
    ],
    cards=[
        ("#00e5cc", "三条读码主线", ["timeline/：instant 状态机", "table/view/：文件视图组装", "index/：key→fileGroup 映射"]),
        ("#a78bfa", "COW vs MOR", ["COW：重写 base、读纯、写放大", "MOR：追加 log、写快、读需合并", "compaction 是两者的桥"]),
        ("#fbbf24", "易忘但重要", ["Metadata Table 免 List/bloom", "archival 控制时间线长度", "rollback 也是 instant"]),
    ],
))

# ================ 02 Timeline ================
fig_tl_states = FIG("hudi-tl1", "图 2-1 · instant 三要素与状态机：文件名 = 时间戳 + action + 状态后缀", 1040, 560, (
    T(30, 40, "HOODIE INSTANT · 三要素与状态迁移", 13, "#8fa5c8", True)
    # 三要素拆解
    + R(30, 70, 980, 120, "#121a30", 10, "#31435f")
    + T(50, 98, "HoodieInstant 的三要素（一个唯一的表变更）", 12, "#7fc8e8", True)
    + B(50, 116, 280, 56, "#0f2438", C, "timestamp", "20240115103000000", tcolor=C, mono=True)
    + B(360, 116, 280, 56, "#0f2438", C, "action", "commit / deltacommit / …", tcolor=C, mono=True)
    + B(670, 116, 300, 56, "#0f2438", C, "state", "requested / inflight / completed", tcolor=C, mono=True)
    # 状态机：三个状态一行排开，间距足够
    + B(80, 250, 240, 84, "#0f2438", C, "requested", "文件: {ts}.{action}.requested", tcolor=C)
    + B(430, 250, 240, 84, "#2a2010", CY, "inflight", "文件: {ts}.{action}.inflight", tcolor=CY)
    + B(780, 250, 220, 84, "#0f2a1c", CG, "completed", "文件: {ts}.{action}", tcolor=CG)
    + A(320, 292, 430, 292, "transitionState()", color="#5f7ba6", lx=375, ly=280)
    + A(670, 292, 780, 292, "saveAsComplete()", color="#5f7ba6", lx=725, ly=280)
    # 底部：崩溃恢复语义条
    + R(30, 390, 980, 130, "#121a30", 10, "#31435f")
    + T(50, 418, "崩溃恢复的判定规则（不需要分布式协调）", 12, "#7fc8e8", True)
    + T(50, 444, "① 存在 completed 文件 → 提交成功（重命名即原子边界）", 12, "#dbe6f5")
    + T(50, 470, "② 只有 inflight 文件 → 执行中断：按 action 语义 rollback 或删除重放", 12, "#dbe6f5")
    + T(50, 496, "③ rollback 自身也是 instant：先 requested 再 completed，留下审计痕迹", 12, "#8fa5c0")
))

CHAPTERS_A.append(dict(
    file="02-timeline.html", title="Timeline：把每一次变更变成时间线上的一个点",
    kicker="APACHE HUDI SOURCE STUDY · CH 02",
    sub="Timeline 是 Hudi 的心跳：所有写入、表服务、运维操作都表现为时间线上的一个 <strong>instant</strong>（HoodieInstant）。它的文件形态简单到极致——.hoodie/ 目录下的一批小文件——却支撑起了 ACID、崩溃恢复、增量消费与表服务调度。本章从三要素、状态机、文件形态到源码走读完整拆解。",
    stats=[("3", "instant 状态"), ("7+", "action 类型"), ("原子", "重命名即提交边界"), ("2 个", "IO 入口方法")],
    sections=[
        ("Instant 的三要素", [
            "<code>HoodieInstant</code> 由三部分组成：<strong>timestamp</strong>（形如 <code>20240115103000000</code> 的字符串，由 <code>HoodieActiveTimeline.createNewInstantTime()</code> 生成，保证单调）、<strong>action</strong>（做什么）、<strong>state</strong>（做到哪）。三者的组合唯一确定一次表变更，也是文件命名的全部依据。",
            ("fig", fig_tl_states),
            "注意文件命名细节：completed 状态的文件没有状态后缀（<code>{ts}.{action}</code>），requested/inflight 有显式后缀。文件按文件名排序即时间序——Hudi 从不依赖文件 mtime（对象存储 mtime 不可靠）。",
        ]),
        ("状态机：两个迁移方法就是全部", [
            "状态迁移只有两个入口：<code>HoodieActiveTimeline.transitionState(instant, newState)</code>（重命名）与 <code>saveAsComplete(metadata)</code>（写内容 + 重命名）。所有 action 执行器都遵守「先 requested（需要计划时）→ 再 inflight → 最后 completed」的纪律。",
            "requested 阶段对数据写入是可选的（直接 inflight），但对 <strong>compaction / clustering</strong> 是必须的：计划（哪些 fileGroup、怎么合并）先持久化为 requested instant，执行器崩溃后计划不丢，任何引擎都能接手执行——这是「表服务可独立部署」的基石。",
        ]),
        ("commit 文件里有什么", [
            "completed 的 commit 文件内容是 <code>HoodieCommitMetadata</code>（avro 序列化，兼容 json 视图）：顶层是 <code>partitionToWriteStats</code>——每个分区下每个 fileGroup 的写入统计（文件路径、新增行数、更新行数、总行数、文件大小）；replacecommit 额外带 <code>partitionToReplaceFileIds</code>（被整组替换的文件）。",
            "查询路径几乎不读 commit 的业务内容，只读它的 <strong>文件清单</strong> 部分（经由 FileSystemView 缓存）；而 <strong>Incremental Query</strong> 与 <strong>CDC</strong> 则会深入解析它，输出 instant 区间内的变更。",
        ]),
        ("HoodieActiveTimeline 源码走读", [
            "<code>getActiveTimeline()</code> 时 MetaClient 会扫描 .hoodie/ 目录，把文件名解析成 instant 列表缓存。<code>filterCompletedInstants()</code> / <code>filterInflights()</code> / <code>filter(f)</code> 是流式过滤器；<code>lastInstant()</code>、<code>nthInstant(n)</code>、<code>findInstantsBeforeOrEquals(ts)</code>、<code>findInstantsAfter(ts,n)</code> 服务于增量查询与 Time Travel 定位。",
            "写入 IO 只有两条：<code>saveToPending(action, content)</code> 写 requested/inflight 内容，<code>saveAsComplete(action, content)</code> 完成提交。二者都以 <code>HoodieActiveTimeline</code> 持有的 <code>HoodieStorage</code>（封装 FileSystem / object store）为底座——这也是云存储适配的单一收口点。",
        ]),
        ("Archival：时间线的垃圾回收", [
            "高频写入会让 active timeline 无限增长，扫描变慢。<code>HoodieArchivedTimeline</code>（配合元数据表）把老 instant 归档到 <code>.hoodie/archived/</code> 的列存文件里。归档按「保留窗口 + 最老活跃 instant」划线，归档后 active timeline 恢复小文件状态。",
            "读源码注意：<code>HoodieTableMetaClient.reloadActiveTimeline()</code> 在任何可能的外部变更（多写者场景）之后必须显式调用，否则拿到的是缓存的旧时间线——这是并发调试时最常见的坑。",
        ]),
        ("崩溃恢复的完整语义", [
            "结合状态机与文件形态，崩溃恢复不需要任何分布式协调：<strong>残留 inflight</strong> 说明执行中断——数据写入类 action（commit/deltacommit）由 rollback instant 撤销（删除半成品文件、回写索引撤销记录）；表服务类（compaction）则可以直接删除 requested/inflight 重试，因为计划是幂等的。",
            "rollback 本身也是 instant（action=rollback），其元数据记录被回滚的目标 instant 及删除的文件清单——所以回滚同样可审计、可追溯。",
        ]),
    ],
    cards=[
        ("#00e5cc", "状态机不变量", ["completed = 原子重命名边界", "inflight 残留 = 可判定崩溃", "requested = 计划先行"]),
        ("#fbbf24", "常见坑", ["多写者后要 reloadActiveTimeline", "对象存储 mtime 不可信", "archival 后增量查询要看归档"]),
        ("#a78bfa", "源码坐标", ["timeline/HoodieInstant.java", "timeline/HoodieActiveTimeline.java", "table/HoodieTableMetaClient.java"]),
    ],
))

# ================ 03 文件布局 ================
fig_layout = FIG("hudi-fl1", "图 3-1 · 三层布局全景：分区目录 → FileGroup → FileSlice → Base/Log", 1040, 620, (
    T(30, 40, "FILE LAYOUT · partition / fileGroup / fileSlice / base+log", 13, "#8fa5c8", True)
    # 左列：分区目录树
    + R(30, 70, 300, 420, "#121a30", 10, "#31435f")
    + T(50, 98, "表目录树（对象存储=前缀）", 12, "#7fc8e8", True)
    + T(50, 130, "my_table/", 12, "#dbe6f5", mono=True)
    + T(66, 154, ".hoodie/", 11.5, CY, mono=True)
    + T(82, 176, "20240115….commit", 10.5, "#8fa5c8", mono=True)
    + T(82, 196, "archived/  .schema/", 10.5, "#6b7d99", mono=True)
    + T(66, 222, "partition=2024-01-15/", 11.5, "#dbe6f5", mono=True)
    + T(82, 244, "fg-1/", 11.5, C, mono=True)
    + T(98, 266, "v1.parquet  v2.parquet", 10.5, "#8fa5c8", mono=True)
    + T(98, 286, ".log_1  .log_2", 10.5, CY, mono=True)
    + T(82, 310, "fg-2/", 11.5, C, mono=True)
    + T(66, 336, "partition=2024-01-16/", 11.5, "#dbe6f5", mono=True)
    + T(66, 362, "_metadata/（MDT）", 11.5, CP, mono=True)
    + T(50, 400, "fileId 是文件组身份：", 11, "#6b7d99")
    + T(50, 420, "fg-1 的所有版本同住一个子目录", 11, "#6b7d99")
    + T(50, 440, "（v6 format 可扁平化，见后文）", 10.5, "#6b7d99")
    # 中列：FileGroup 时间线
    + R(360, 70, 320, 420, "#0f2438", 10, "#31435f")
    + T(380, 98, "FileGroup fg-1 的切片时间线", 12, "#7fc8e8", True)
    # slice v1
    + B(380, 118, 280, 70, "#0e2a20", CG, "FileSlice @ t1", "base: fg-1-v1.parquet", tcolor=CG)
    # slice v2
    + B(380, 204, 280, 70, "#0e2a20", CG, "FileSlice @ t3", "base: fg-1-v2.parquet", tcolor=CG)
    + A(520, 188, 520, 204, "commit t3 重写", color="#5f7ba6", lx=600)
    # slice v3 (MOR)
    + R(380, 306, 280, 106, "#241a12", 10, CY)
    + T(398, 330, "FileSlice @ t6 (MOR)", 12, CY, True)
    + T(398, 352, "base: fg-1-v3.parquet", 10.5, "#dbe6f5", mono=True)
    + T(398, 374, "+ .log_1  + .log_2（追加中）", 10.5, CY, mono=True)
    + T(398, 396, "log 不改变 base，读时合并", 10.5, "#8fa5c8")
    + T(380, 436, "每个切片 = 一个 completed instant", 10.5, "#6b7d99")
    + T(380, 456, "旧切片保留到 clean / Time Travel 窗口外", 10.5, "#6b7d99")
    # 右列：一个切片内部
    + R(720, 70, 290, 420, "#121a30", 10, "#31435f")
    + T(740, 98, "MOR 切片内部：base + log 合成", 12, "#7fc8e8", True)
    + B(740, 118, 250, 60, "#0e2a20", CG, "base（v3.parquet）", "10:00 时的完整快照", tcolor=CG)
    + B(740, 196, 250, 56, "#241a12", CY, "log_1 · DATA 块", "11:00 的 upsert", tcolor=CY, mono=True)
    + B(740, 268, 250, 56, "#241a12", CY, "log_2 · DELETE 块", "11:05 的删除", tcolor=CY, mono=True)
    + B(740, 340, 250, 56, "#1a1430", CP, "读时合并", "base × logs → 当前视图", tcolor=CP)
    + A(865, 178, 865, 196, "", color="#5f7ba6")
    + A(865, 252, 865, 268, "", color="#5f7ba6")
    + A(865, 324, 865, 340, "", color="#5f7ba6")
    + T(740, 428, "log 块按 8-32MB 滚动新文件", 10.5, "#6b7d99")
    + T(740, 448, "compaction 消费后整组作废", 10.5, "#6b7d99")
    # 底部横条
    + R(30, 510, 980, 80, "#121a30", 10, "#31435f")
    + T(50, 538, "源码实体对应：HoodieFileGroup（fileId + slices）→ HoodieFileSlice（baseFile + logFiles + instantTime）→ HoodieBaseFile / HoodieLogFile", 11.5, "#93a5c0")
    + T(50, 566, "全部位于 common/table/view/ 包；FileSystemView 负责把它们组装并缓存成「某 instant 下的可见视图」", 11.5, "#6b7d99")
))

CHAPTERS_A.append(dict(
    file="03-file-layout.html", title="文件布局：FileGroup、FileSlice 与 Log File 的字节级细节",
    kicker="APACHE HUDI SOURCE STUDY · CH 03",
    sub="Hudi 的目录布局刻意保持「分区 / 文件组 / 切片」三层结构：fileId 是记录的身份（永不变名），commit 是切片的版本（时间线驱动），base 不可变、MOR 追加日志。本章从目录树一路讲到 log block 的字节级格式。",
    stats=[("3 层", "partition → filegroup → slice"), ("不可变", "base file 写出即冻结"), ("6 字节", "HOODIE_MAGIC 块头"), ("1 个", "视图缓存层 FileSystemView")],
    sections=[
        ("三层布局全景", [
            ("fig", fig_layout),
            "与 Parquet 目录的最大差异在于：Hudi 的文件名携带 <strong>fileId + 写入时间</strong>（如 <code>fg-id-v1.parquet</code>），从而「文件的身份」与「文件的版本」都可从文件名推断——文件系统视图的重建因此不需要任何额外元数据。",
        ]),
        ("Base File：比 Parquet 多一个 footer", [
            "base file 是标准 Parquet，外加 Hudi 自己的 <strong>footer 块</strong>（<code>HoodieFooter</code>）：写入 commit instant、schema、以及 bloom filter（若启用）。bloom filter 按 <code>hoodie.bloom.index.filter.type</code> 选择 DYNAMIC/SIZED，写入时 <code>HoodieCreateHandle</code> 按 key 构造。",
            "记录级元数据还有 <strong>record key 与分区路径列</strong>（MetaColumns）：_hoodie_commit_time、_hoodie_commit_seqno、_hoodie_record_key、_hoodie_partition_path、_hoodie_file_name 五列前缀由 <code>HoodieRecordPayload</code> 写入，是 merge 与审计的物理依据。",
        ]),
        ("Log File：字节级格式", [
            "log file 由 <code>HoodieLogFormatWriter</code> 追加，结构为「块序列」：每块以 <strong>6 字节 HOODIE_MAGIC</strong>（<code>#HUDF#</code>）开头，随后是块长度、<code>HoodieLogBlockHeader</code>（instantTime、blockType、schema、owner class）、块体、以及 <code>HoodieLogBlockFooter</code>（总长度用于完整性校验）。",
            "五种块类型：<strong>AVRO_DATA_BLOCK</strong>（upsert/insert 的记录序列）、<strong>DELETE_BLOCK</strong>（整行删除的 keys）、<strong>COMMAND_BLOCK</strong>（rollback 命令，让 reader 跳过被回滚块）、<strong>CORRUPT_BLOCK</strong>（写坏后的占位，reader 跳到下一 MAGIC）、<strong>HFILE_DATA_BLOCK</strong>（HFile 格式变体）。块达到 <code>hoodie.logfile.data.block.max.size</code>（默认 256MB，常调小）就滚动新文件。",
            "读取端 <code>HoodieLogFormatReader</code> 逐块读：校验 MAGIC → 读 header → 按 schema 反序列化 → footer 校验长度。CORRUPT_BLOCK 的存在使「写一半崩溃」的日志仍可安全地读到已完整写入的块。",
        ]),
        ("v6 格式与布局演进", [
            "传统布局把同一 fileGroup 的版本放子目录；<strong>table format v6</strong>（<code>HoodieTableVersion.SIX</code>）起支持扁平化（timed layout）：文件名携带版本时间戳，直接放分区前缀下。这减少了小目录数量，对对象存储的 List/事务更友好。视图层通过 <code>HoodieTableMetaClient.getTableFormatVersion()</code> 分叉处理。",
        ]),
        ("FileSystemView：把物理组装成逻辑", [
            "<code>FileSystemViewManager</code> 按表创建 <code>HoodieTableFileSystemView</code>：扫描分区 → 按 fileId 聚成 FileGroup → 每个 group 内按 instant 排出 FileSlice → 缓存。提供 <code>getLatestFileSlice(partition)</code>、<code>getLatestBaseFile()</code>、<code>getAllFileSlices()</code>、<code>getLatestMergedFileSliceBeforeOrOn()</code>（Read Optimized 用）等 API。",
            "多写者场景下视图可能过期，<code>sync()</code> 增量刷新；服务端化形态（Timeline Server）把视图集中缓存，避免每个 executor 重复扫描——这是 0.13+ 的默认推荐架构。",
        ]),
    ],
    cards=[
        ("#00e5cc", "不变量", ["fileId 永不变名", "base file 不可变", "新版本 = 新文件 + 新 instant"]),
        ("#fbbf24", "log 字节级", ["6 字节 HOODIE_MAGIC", "header(instant/schema/type)", "footer 总长校验 + CORRUPT 块"]),
        ("#a78bfa", "易忽略的点", ["MetaColumns 五列前缀", "v6 扁平化布局", "Timeline Server 集中视图"]),
    ],
))

# ================ 04 COW 写路径 ================
fig_cow = FIG("hudi-cow", "图 4-1 · COW upsert 全流程：八个阶段与两处保护（marker + OCC）", 1040, 620, (
    T(30, 40, "COW WRITE PIPELINE · BaseHoodieTableServiceClient.upsert()", 13, "#8fa5c8", True)
    # 阶段条
    + B(40, 70, 220, 74, "#0f2438", C, "① tagLocation", "Index：key → fileId 打标", tcolor=C)
    + B(300, 70, 220, 74, "#121a30", "#31435f", "② WorkloadProfile", "update / insert 分组统计")
    + B(560, 70, 220, 74, "#121a30", "#31435f", "③ Partitioner", "UpertPartitioner 派发任务")
    + B(820, 70, 180, 74, "#121a30", "#31435f", "④ 执行写入", "各 task 写文件")
    + A(260, 107, 300, 107, "", color="#5f7ba6")
    + A(520, 107, 560, 107, "", color="#5f7ba6")
    + A(780, 107, 820, 107, "", color="#5f7ba6")
    # 第二行
    + B(820, 180, 180, 74, "#2a2010", CY, "⑤ Marker", "每个待写文件先立标", tcolor=CY)
    + B(560, 180, 220, 74, "#121a30", "#31435f", "⑥ HoodieMergeHandle", "读旧 slice + 新记录合并")
    + B(300, 180, 220, 74, "#121a30", "#31435f", "⑥b CreateHandle", "insert 新建 fileGroup")
    + B(40, 180, 220, 74, "#121a30", "#31435f", "⑦ WriteStatus", "统计 / 错误收集")
    + A(820, 144, 910, 180, "", color="#5f7ba6")
    + A(820, 217, 780, 217, "", color="#5f7ba6")
    + A(560, 217, 520, 217, "", color="#5f7ba6")
    + A(300, 217, 260, 217, "", color="#5f7ba6")
    # 第三行：提交
    + B(300, 300, 220, 74, "#241a12", CY, "⑧ ConflictChecker", "与并发 instant 比文件集", tcolor=CY)
    + B(560, 300, 220, 74, "#0f2438", C, "⑨ 提交", "commitMetadata → timeline", tcolor=C)
    + B(40, 300, 220, 74, "#121a30", "#31435f", "索引回写", "updateLocation 新 key")
    + A(260, 337, 300, 337, "", color="#5f7ba6")
    + A(520, 337, 560, 337, "", color="#5f7ba6")
    # 底部：marker 与小文件策略详解
    + R(40, 420, 960, 170, "#121a30", 10, "#31435f")
    + T(60, 448, "Marker 机制（防对象存储部分写）", 12, "#7fc8e8", True)
    + T(60, 474, "写每个数据文件前先创建 marker 文件：{ts}/{partition}/{fileId}{markerExt}；Direct 模式逐个写，Timeline-Server 模式批量由服务端代写", 11.5, "#93a5c0")
    + T(60, 500, "提交前校验：所有 marker 必须有对应成功写出的数据文件；发现孤儿 marker → 判定本次写失败并清理，杜绝半成品文件被读到", 11.5, "#93a5c0")
    + T(60, 528, "小文件策略：SmallFileAssignPolicy 把小 base（< hoodie.parquet.small.file.limit）标记为可追加，insert 优先填充它们而不是开新 fileGroup", 11.5, "#93a5c0")
    + T(60, 556, "失败清理：rollback instant + MarkerFiles.deleteMarkerFiles；对象存储上由 orphan-file 清理兜底", 11.5, "#6b7d99")
    + A(140, 374, 140, 420, "详情", color="#5f7ba6", dash=True, lx=140)
))

CHAPTERS_A.append(dict(
    file="04-cow-write.html", title="COW 写路径：从 upsert 到一次原子提交的八步",
    kicker="APACHE HUDI SOURCE STUDY · CH 04",
    sub="<code>BaseHoodieTableServiceClient.upsert()</code> 是 Hudi 写侧的主干道：索引打标 → 工作负载画像 → 分区器派发 → 写新 base → marker 防泄漏 → 冲突校验 → 提交。本章沿这条链逐站拆解，每一站的类名、决策点与调优参数都标出来。",
    stats=[("8 步", "upsert 主流程"), ("2 处", "Marker + OCC 双保护"), ("3 种", "写 handle 分工"), ("1 条", "小文件填充策略")],
    sections=[
        ("主流程总览", [
            ("fig", fig_cow),
            "入口 <code>upsert(javadDRecordRDD, instantTime)</code>：先 <code>index.tagLocation()</code>，把每条记录标注为「update（已有 fileId）」或「insert（新 key）」；随后构造 <code>WorkloadProfile</code>（按分区的 update/insert 工作量画像），交给 <code>UpsertPartitioner</code> 生成 Spark 任务；执行后汇总 <code>WriteStatus</code>，最后走提交协议。",
        ]),
        ("Index 阶段：决定记录去哪", [
            "tagLocation 输出带 <code>HoodieRecordLocation</code>（instantTime + fileId）的记录流：命中旧 fileGroup 的标 update（位置 = 该组当前 slice），未命中的标 insert。这一步的代价就是索引实现的代价（CH06）：Bloom 索引要读候选文件的 bloom，Bucket 索引是纯计算，Record Index 查 MDT。",
            "索引还有第二个职责：提交成功后 <code>updateLocation()</code> 把新 key 的位置回写进索引（Bloom 无需回写——它随 base file 自带；Record Index/HBase 需要）。",
        ]),
        ("Partitioner：update 与 insert 的不同命运", [
            "<strong>update 记录</strong>：按 fileId 分组——同组记录合并为一个任务，交给 <code>HoodieMergeHandle</code>：读旧 slice 的 parquet 逐行与更新记录按 key 合并（payload.merge），写出全新 base file。<strong>insert 记录</strong>：先尝试填充小文件（SmallFileAssignPolicy），填不下的开新 fileGroup 交给 <code>HoodieCreateHandle</code>。",
            "任务并行度由 <code>hoodie.upsert.shuffle.parallelism</code> 控制；<code>WorkloadProfile</code> 还会为每个分区的写入量估算，用于全局小文件平衡（<code>SmallFileCompare</code>）。",
        ]),
        ("Marker：对象存储上的防部分写", [
            "S3/OSS 没有原子重命名，「写一半的文件」会被 List 看到。Hudi 的解法：写数据文件之前先写一个 <strong>marker 文件</strong>，提交前由 <code>MarkerFiles</code>（<code>MarkerType.DIRECT</code> 或 timeline-server 聚合模式）核对「marker 数 = 成功数据文件数」。不等则本次写失败：触发 rollback 清理半成品。频繁失败的场景可开 <code>hoodie.write.markers.timeline_server_based.enabled</code> 把 marker 写放大降一个量级。",
        ]),
        ("提交：OCC 与索引回写", [
            "WriteStatus 汇总为 <code>HoodieCommitMetadata</code> 后进入 CH08 的提交协议：取锁 → 冲突校验 → 写 timeline。成功后回调 <code>index.updateLocation()</code> 维护外部索引，并触发 inline 表服务（compaction/clustering/clean 的调度钩子）。",
            "Bulk Insert 是同一骨架的轻量分支：跳过 index（不查旧位置，直接新建），适合首次装载。<code>HoodieBulkInsertDataInternalWriter</code> 在 Spark 3 上走 vectorized 路径。",
        ]),
    ],
    cards=[
        ("#00e5cc", "骨架类", ["BaseHoodieTableServiceClient", "UpsertPartitioner / SmallFilePolicy", "HoodieMergeHandle / CreateHandle"]),
        ("#fbbf24", "两个保护", ["Marker：部分写泄漏防护", "OCC：提交临界区冲突校验", "rollback 兜底清理"]),
        ("#a78bfa", "调优入口", ["upsert.shuffle.parallelism", "small.file.limit 阈值", "markers.timeline_server_based"]),
    ],
))
