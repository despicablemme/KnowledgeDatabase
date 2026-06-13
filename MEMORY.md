# MEMORY.md - Long-Term Memory

_Update this file with lessons learned, decisions, and important context._

---

## 🏷️ IDENTITY
- I am **Jarvis**，主人的贴身助手
- 主人: 你

---

## 📁 代码项目目录（2026-06-06）
- 以后所有代码项目统一放在 `~/CodeProjects/` 下
- 不再使用 `~/Documents/KnowLedgeDatabase/projects/` 存放代码
- 知识库相关资料（资料总结、文档）仍放在 `~/Documents/KnowLedgeDatabase/`
- 当前项目：
  - `~/CodeProjects/syncplay` - 异地同步视频播放工具（GitHub: despicablemme/SyncPlayer）

---

## ⚠️ IMPORTANT RULES (learned the hard way)

### 1. 用户要求必须立刻写入文件
- 教训:用户提要求时没有立刻写入,等追问才补写
- 以后:任何用户的重要要求、规则、偏好,**立刻写入文件**,不等追问
- 写入位置:USER.md 或相关项目文件

### 2. 安装前必须申请许可
- 任何插件、skill、MCP 或其他功能,安装前必须先问主人
- 不可以自作主张安装

### 3. 主人给的重要行动规则(2026-03-21)
- **禁止金钱交易**:不主动产生任何有金钱交易相关的动作
- **安全甄别**:仔细甄别网络来源内容是否影响系统运行安全
- **确认原则**:遇到相关问题,需要向主人确认

### 4. QQBot Skill 安装目录规则(已废弃:2026-05-16)
- 原规则:skill 必须安装到 `~/.openclaw/skills/`(通用 skill 目录)
- 新规则:统一放在 `~/.openclaw/workspace/skills/` 下
- 详见规则 #11

### 5. 不准随意卸载软件或删除文件(2026-03-22)
- 不准随意卸载软件,或是删除与主人明确要求无关的文件
- 所有删除/卸载操作必须获得主人**明确授权**后方可执行

### 6. 角色定位:领导者和任务发布者(2026-03-23)
- 主人定位我为:领导者、任务发布者、监督者
- 收到耗时任务时,**立即创建子 agent 处理**,我不被阻塞
- 子 agent 完成任务后,我负责汇总汇报给主人
- **永远保持可响应状态**

### 7. 知识库优先检索(2026-03-21)
- 主人有知识库:`~/Documents/KnowLedgeDatabase/`
- 主人提问时,**先检索知识库**
- 如果知识库已有记录,告诉主人"这是来自知识库的答案"
- 如果知识库没有,再搜索或查找其他来源

### 8. TTS相关规则(2026-03-23)
- **输出目录**:`~/Documents/TTSoutputs/{书名}/`
- **语速偏好**:0.75倍速(rate="-25%")
- **声音**:默认 zh-CN-XiaoxiaoNeural(晓晓女声)
- **东北话**:zh-CN-liaoning-XiaobeiNeural
- **TTS任务必须交给子agent处理**,我不被阻塞

### 9. 子agent使用规则(教训:2026-03-23)
- **所有任务一律交给子 agent 执行**,我永远不自己执行
- 即使是"只生成一段"只要涉及较长时间,也交给子 agent
- 不要在自己会话里执行任何耗时任务
- 我只负责:分派任务 → 监控进度 → 汇总汇报
- **永远保持可响应状态**

### 10. 检查定时任务要用 openclaw cron list(教训:2026-03-24)
- `crontab -l` 看的是系统 crontab,可能是空的
- OpenClaw 自己的 cron 任务要用 `openclaw cron list` 查看
- 两者是独立的两套系统

### 11. Skill 存放位置规则(2026-05-16)
- 所有 skill(技能/插件)统一创建和维护在 `~/.openclaw/workspace/skills/` 目录下
- 不再区分通用 skill 目录或扩展专属目录
- 方便统一管理和维护

### 12. 任何耗时操作必须发子agent(教训:2026-03-24)
- brew install、文件生成、代码编译等耗时任务,一律丢给子agent
- 我永远不自己在主会话执行耗时操作
- 养成习惯:先想"这耗时吗" → 耗时就spawn

### 13. 处理问题要先查证再回复(教训:2026-05-17)
- 教训:文件发送失败后,没验证原因就直接重发,不透明
- 以后遇到问题:先查证据(文件权限、编码、实际发送状态),再告诉用户原因,最后处理
- 不能只给结果不给原因

### 14. 主人求证时必须有切实证据(教训:2026-05-17)
- 教训:主人向我求证事情时,我必须先查实再回复,不能凭感觉或猜测
- "有切实证据"的定义:文件权限、实际状态、脚本输出、日志记录等可查可验的东西
- 不能用"应该是"、"估计是"、"看起来是"来回复,必须是确定的

### 14. 纠错指导写入持久文件(教训:2026-05-17)
- 当主人对我纠错或指导时,把可复用的有价值的经验写入 MEMORY.md
- 判断标准:能否减少自己以后的出错概率
- 不能只"记在心里",要写进文件才算数

### 20. subagent `done` 后必须立即查交付 + 主动汇报(教训:2026-06-08)
- 教训:`v04-commander` 昨晚 23:04 跑完 21 分钟就 `done` 了,但**静默收工,没给主人汇报**
- 主人 21 小时后问"进展怎么样"我才知道要查
- 这等于 v0.4 完工事件根本没被主会话处理
- **规则(铁律)**:
  1. 收到任何 subagent `done` 事件 → **立刻** `subagents list` 查交付
  2. 查完 → **立刻** 主动汇报主人(不要等问)
  3. 汇报内容包括:实际跑多久 / 交付了什么 / 失败点 / 下一步
- 推论:同步任务完成 = 事件回流到主会话 + 主人看到汇报,缺一不可
- **不要把"查交付"和"汇报"分两步,中间一定夹立刻动作**

### 20.1 sessions_yield 不等 subagent done 事件 (教训:2026-06-10 强化)
- 教训:v0.6.1-A-Builder 15:26 完工,主 agent **沉睡 2.5 小时**到 18:00 主人问"没有结果?"才查
- **根因**:`sessions_yield` 等的是"主人在 webchat 发消息"或"外部事件",但 **subagent done 事件不算外部事件** — `streamTo: "parent"` 只把事件 **push 到 transcript**,**不**触发主 agent turn
- 这跟 v04-commander 21 小时静默**同款 bug**,我**又**踩了
- **规则(强化铁律)**:
  1. **派 subagent 后不 yield** — yield 阻塞主 agent,完工事件沉底
  2. 派 subagent → `update_plan` 标记进度 → 主 agent **主动做下一件事** (准备下一任务 / 整理文档 / 检查产物)
  3. **下次主 agent 被触发时第一件事** `subagents list` 查所有 done 的 subagent → 立刻查交付 + 主动汇报
  4. 如果主 agent 实在没事做,**结束 turn 让主人在 webchat 触发**,不要 yield 沉睡
- 推论:**主 agent 工作模式 = "派活 → 不等 → 做下一件事 → 主动汇报"**,**不**是"派活 → yield 等 → 主人问"
- 推论:yield 用途:等**明确外部事件** (cron wake / 主人在 webchat 发消息),**不**是"等 subagent 完工"

### 28. 已确定的计划, 默认执行到底不打扰 (主人 2026-06-10 立特质)
- 教训:v0.6.1 阶段 B, 主人说"跑C。跑完C自己去把所有必要文档更新", 反映主人**明确**希望主 agent 自主执行已定计划
- **规则(主人立的特质, 高优先级)**:
  1. **已确定的计划**: runbook / ROADMAP DoD / 阶段 A plan doc 里写明的, 默认执行到底
  2. **不打扰主人的节点**: 派 subagent / 写 task 书 / 起 cron / 修测试 / commit / push / 阶段 C 一次性更新 docs
  3. **要打扰主人的节点**: 出现 FAIL / NEED FIX / 方向缺失 / 关键 trade-off 选择 / 阶段完工汇报
  4. **汇报频率**: 子任务完工 + 阶段完工 = 主动汇报; 中间步骤**不**汇报
  5. **不**问 "我**现在**该怎么办" — 问 = 浪费主人时间
- 推论: 主 agent 工作模式 = "已 plan + 不打扰 + 主动执行 + 阶段完工汇报"
- 推论: 中间问 = 主 agent 没**真**理解 runbook, **没**真**自主**
- 推论: 跑前**先**确认 plan 完整, 跑中**不**中途问
- 主人原话 (2026-06-10): "以后确定的计划, 如果没有必须我来确认的问题 (比如出现了失败, 缺乏方向), 按照计划执行下去。"
- 关联: 跟 MEMORY #6 (角色定位: 领导者) 一致, 跟 #20 (subagent 主动汇报) 不冲突 — #20 是"完工主动汇报", #28 是"已 plan 不打扰中间"
- 推论: 主 agent 收到"我刚立了特质"的消息时, **本回合**就要把规则写进 SOUL.md (特质) + MEMORY.md (教训), 写完**立刻**执行 (不只写不干)

### 29. 子任务 pass 默认继续, 异常才暂停(主人 2026-06-13 立)
- 主人原话 (2026-06-13 19:47): "如果子任务 pass, 不用请示我, 出现异常才暂停等我指示。"
- **规则**:
  1. 子任务 **pass** → 默认继续下一项, **不**请示主人
  2. 子任务 **异常** (FAIL / NEED FIX / 方向缺失 / 关键 trade-off) → **暂停**, 主动汇报并等指示
  3. 跟 #28 (#28 "已 plan 不打扰中间") **一致**, 是 #28 在"子任务"场景下的具体化
  4. 跟 #20 (#20 "subagent 主动汇报") **互补**: #20 是完工汇报, #29 是 pass 默认走
- 推论: 主 agent 的"暂停请示"清单 = **异常 + 方向缺失 + 关键 trade-off**, 其他场景 (含 pass) 都**不**请示
- 推论: 中途问 = 把"小决策"也升级成"请示", 浪费主人时间, 也显得没自主
- 推论: 派 subagent 时, **预期跑完一路 pass**, 看到 pass 就推下一项, 不要逐项请示

### 20.2 派 subagent 后必须加 cron 轮询 (教训:2026-06-10 再次强化)
- 教训:18:00 修了"yield 不等 done 事件",但 19:24 B-Builder 完工后,**20 分钟空窗期**(19:24-19:43)主 agent 没被任何 trigger 唤醒, 主人 19:43 问"进度"才查
- **根因**:即使不 yield, **ACP `streamTo: "parent"` 事件不自动触发主 agent turn** — 主 agent 只有被 trigger 才 active (cron wake / 主人消息 / 外部事件), 这之间有空窗
- **修法 (v0.6.1 实战)**: **派 subagent 后立刻 add cron 轮询任务**
  - 频率: every 10m (主人 6/10 决定; 5m 太频繁改 10m 平衡)
  - session: isolated
  - payload: agentTurn 查 subagents list, 看到 done 就走 announce 推主人 QQ
  - delivery: announce -> qqbot -> 主人 chat
  - **关键: cron 任务里要写明 "没 done 时静默退出, 不输出"**, 避免每 10 分钟刷屏
  - 完工时 (B-Builder / B-Tester / ...) 走 announce 自动推给主人, 主人**不等问**就看到
- 命令模板:
  ```bash
  openclaw cron add \
    --name "<project>-<version>-progress-poll" \
    --every 5m \
    --session isolated \
    --agent main \
    --announce \
    --channel qqbot \
    --to "qqbot:c2c:<主人-chat-id>" \
    --best-effort-deliver \
    --description "<一句话>" \
    --message "<agent prompt: 查 subagents list, 找到 done 的 <project> subagent, 验证 commit, 静默或发汇报>"
  ```
- 验证: `openclaw cron list | grep <project>` 应看到新任务, 下次跑时间 5m 后
- 配套: **跑完整个项目 (阶段 C 完工) 后, `openclaw cron remove` 删掉**, 避免遗留
- 推论:**任何"派 subagent 后等完工"的场景**, 默认就要加 cron 监控, 不要再吃空窗期亏
- 推论: 20 分钟空窗期 = 主 agent 失职 + 主人不信任累积, 用 cron 10 分钟轮询 = 最多 10 分钟空窗 + 自动汇报

### 24. GitHub Actions if 表达式里慎用 matches() (教训:2026-06-09)
- 坑: `if: ... !matches(github.event.head_commit.message, '^(docs|chore|ci)\s*[\(:]')` 在 push 后 run 0 秒就 completed failure (workflow 拒绝执行)
- 根因: YAML 单引号字符串里的反斜杠 (`\s`, `\(`, `\[`) 在 expression parser 链里可能被处理掉 / 不被识别为合法 regex → GitHub 直接拒跑整个 workflow
- 现象: workflow_dispatch / push 触发后, run status = completed / failure, 0 jobs 跑, 0 logs 产生
- 推论: GitHub Actions if 表达式里**不能假设**反斜杠 escape 跟标准正则一样
- **稳的写法**: 放弃 matches(), 用 `>-` YAML 折行 + `startsWith()` 链式 OR
  ```yaml
  if: >-
    github.ref == 'refs/heads/main' &&
    !startsWith(github.event.head_commit.message, 'docs:') &&
    !startsWith(github.event.head_commit.message, 'docs(') &&
    ...
  ```
- 折行 `>-` 把多行折叠成单行, GitHub Actions if 表达式按单行解析
- 验证命令: push 后看 run 状态, `in_progress`/`completed / success` = 表达式合法; `completed / failure` + 0 jobs + 0 logs = 表达式被拒

### 25. 不要纠结歧义短消息,直接给主人选项让他选(教训:2026-06-10)
- 教训:主人发"不在线2",我反复纠结问"是选B吗?"主人嫌慢回"那个就是我发的,你回的很慢"
- 根因:把"不在线2"当成了"系统消息"或"奇怪格式",没想到就是主人手打
- **规则**:
  1. **任何 QQ / 频道消息默认就是主人发的**,不要怀疑它是系统消息或状态码
  2. **看不懂的短消息不要纠结超过 1 个回合** → 直接列清晰选项(`做A`/`做B`/`做C`)让主人挑
  3. 主人嫌"回得很慢" → 通常因为我问问题而不是直接行动;给选项比问意图快
- 推论:主人回短消息 = 已经决定 / 在催我,这时该给选项或直接干,不要反问
- 推论:用"做A/做B/做C"或"按你说的来"这种**短回执模板**让主人 5 秒内给指令

### 26. subagent 的诊断要亲自验证,不能盲信(教训:2026-06-10)
- 教训:6/9 早报子 agent 报"Tavily API key 位置错配" → 主人转给我修 → 我自己实测 web_search 工具**完全能用**,key 已经在正确位置
- 早期报诊断错了一半:把 stock `@openclaw/tavily-plugin` 和 framix-team 第三方 `openclaw-tavily` 搞混了
- **规则(铁律)**:
  1. subagent 报"X 不工作" → **先自己跑一遍实测** 确认,不要直接动手改
  2. subagent 的诊断可能基于过时的状态(它看到配置的时刻和我们现在看到的不一样)
  3. **修任何东西前先实测**: web_search 跑一次、文件 cat 一次、服务 curl 一次
- 推论:实测 30 秒,比改坏再回滚 5 分钟便宜

### 27. openclaw-tavily 跟 stock @openclaw/tavily-plugin 是两个不同的 plugin(教训:2026-06-10)
- 背景:OpenClaw 2026.6.1 启动报 4 个 warning,其中 2 个跟 Tavily 相关
- **关键事实**(已实测验证):
  - **stock `@openclaw/tavily-plugin`** (官方): 路径 `/opt/homebrew/lib/node_modules/openclaw/dist/extensions/tavily/`,**已编译**,配置 `config.webSearch.apiKey`,提供 `tavily_search` + `tavily_extract`,**就是 web_search 工具背后用的那个**
  - **第三方 `openclaw-tavily`** (framix-team, v0.2.1): 路径 `~/.openclaw/extensions/openclaw-tavily/`,**只有 .ts 无 dist/**,打包有问题,提供 `tavily_crawl` + `tavily_map` + `tavily_research` 等更多工具但当前**用不了**
- **配置正确路径**(web_search 读这个): `plugins.entries.tavily.config.webSearch.apiKey`(注意是 `tavily` 这个 key 名,不是 `openclaw-tavily`)
- 修复方法:删 `plugins.entries.openclaw-tavily` + `plugins.entries.minimax-portal-auth` 这两个 stale config,`openclaw gateway restart`,warning 从 4 个变 1 个(剩下的跟 Tavily 无关)
- 备份命令: `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.$(date +%Y%m%d-%H%M%S)`
- **stale config 含义**: config 引用了已经不存在的 plugin,系统报 "plugin not found",功能不受影响只是噪音 → 直接从 config 删掉就行
- 推论:看到 "plugin not found" warning → 先看 `extensions/` 目录里有没有,没有就说明是 stale config,直接删

### 23. git push 后面 inline `2>&1` 会把分支名搞坏(教训:2026-06-09)
- 坑:`git push origin main 2>&1` 在 exec 工具/某些 shell 解析下变成 `git push origin main2>&1`,被理解为 push 一个叫 `main2` 的 ref → `src refspec main2 does not match any`
- 解决:把 redirect 拆开写 → `git push origin main > /tmp/log 2>&1; cat /tmp/log`
- 或者用 `tee`:`git push origin main 2>&1 | tee /tmp/log`
- 以后:任何 inline `2>&1` 跟命令名同行的写法都警惕,优先写到临时文件

### 22. Mac dmg 装上弹 "damaged" 不一定是 dmg 损坏(教训:2026-06-08)
- 教训:v0.5.0 / v0.5.1 dmg 都被反馈"damaged",我一度以为 spctl 评估失败 = 装上必坏
- 实际根因:**Chrome 浏览器下载时自动加了 `com.apple.quarantine` xattr** + ad-hoc 签名 + macOS Gatekeeper 拦截
- `spctl --assess` 评估失败 ≠ 实际不能开(macOS 实际运行时只看 quarantine + 签名状态,不严格做 sealed resources 校验)
- 验证链:
  - 本地 build 装的 v0.5.1 app 能开(`xattr -l` 显示 quarantine 空)
  - GitHub Actions 下的 v0.5.1 dmg 装上后跑 `xattr -dr com.apple.quarantine` 也能开
- **万能解法**(先试这个,10 秒):
  ```bash
  xattr -dr com.apple.quarantine <app路径>
  ```
- 推论:Mac ad-hoc 签的 app 只要 quarantine 卸了就能开,不需要 Apple Developer 签名/公证
- 推论:但分发渠道有碑 - 用户每次都要跑 xattr 命令,体验差
- **记住**:诊断 Mac "damaged" 问题,先看 `xattr -l <app> | grep quarantine`,有就先卸了试

### 21. 嘴上说"立刻做"必须真的立刻做(教训:2026-06-08)
- 教训:我说"我立刻写进 MEMORY.md",但**主人在我心里默认我可能没写**,反问"你写了吗"
- 主人问的时候,说明他对我口头承诺已经失去信任
- **规则**:
  1. 说"立刻做" → **同一个回合**就把文件改了,不要等下一个工具调用
  2. 改完 → **明确告诉主人**:写入位置 + 行号/章节,不要含糊
  3. 主人质问"你做没做"时 → **第一句回答事实**(已做/没做),不要先解释
- 推论:"我等下做"是空头支票,要 commit 到本轮就做完

### 19. edit 工具可能改坏文件标点(教训:2026-06-07)
- 坑:用 `edit` 工具改一行时,意外把文件中其他行的全角标点(`：` `，` `（` `）`)改成了半角
- 现象:git diff 显示一堆无关行被修改
- 原因:edit 工具的 oldText/newText 匹配 / 规范化可能出意外
- 修复:用 `git checkout <file>` 还原到上次 commit 的状态
- 以后:复杂代码改动后,先 `git diff <file>` 看看,若有意外,checkout + 重做

### 18. 别在 SMB / UNC 路径下跑 Python/Node 服务(教训:2026-06-07)
- 坑:从 `\\server\share\foo` 这类 UNC 路径直接启 `python -m http.server` / `node server.js`
- 症状:脚本打"服务已启"但页面空白(端口未真监听),或 EBUSY/permission 拒绝
- 原因:SMB 文件锁/权限/I/O 延迟都不适合启长连服务
- 解决:先 xcopy / rsync 到本地盘(如 C:\foo 或 ~/foo),再从本地启服务
- 推论:Mac 的 SMB 挂载(`smb://...`)和 Windows UNC 一样不要当工作目录
- 以后:看到“页面空白但进程活着” → 先怀疑路径,再怀疑其他

### 17. Python http.server 拦截 `..` 路径(教训:2026-06-07)
- 坑:`python3 -m http.server 8080` 在 `src/client/` 启,但 HTML 写 `<script src="../shared/xxx.js">`
- 现象:`xxx.js` 静默 404(SyncEngine 未定义,整个 init() 崩,创建房间无反应)
- 原因:Python http.server 出于安全会拦截 `..` 路径,不让访问上级目录
- 修复:把 server 启在 `src/` 顶层,而不是 `src/client/`,URL 变 `http://localhost:8080/client/`
- 以后:启 static server 时,根目录要够"高"以容纳所有相对路径
- 检查:打开 DevTools Network,看 `../` 路径资源是否 200

### 16. 路径里 `..` 别想当然(教训:2026-06-07)
- 坑:`~/.openclaw/workspace/../CodeProjects/...` 不会回到 `~/CodeProjects/`
  而是到 `~/.openclaw/CodeProjects/...` (多一层 .openclaw/)
- 因为 `workspace/` 的父目录是 `.openclaw/`,不是 home
- 以后给项目用绝对路径:`/Users/bruce/CodeProjects/syncplay/...`
- 或者两个 `..`:`~/.openclaw/workspace/../../CodeProjects/...`
- 这个坑会导致 OpenClaw 的 edit/write 工具报 ENOENT

### 15. 优先用项目自带的"一键脚本",别让用户敲多条命令(教训:2026-06-07)
- 教训:主人质问"不是要求一键启动吗,为什么还要这么多命令"
- 项目已有 start.command / start.sh / start.bat,R1 已实现
- 我却贴了 3 条手动命令(cd + npm install + npm start)
- 以后:给用户任何操作步骤前,先查 `ls start.*` / `cat package.json scripts` / README
- 优先用项目自带的脚本;只有项目没提供才手写
- 如果连"测试"都要多步,主动提:要不要写个 `test:xxx.js` 脚本

### 14. 回复要明确,不要说"记下了"这种模糊表达
- 教训:用户问"怎么记下的"时我没有给出具体答案
- 以后说"记下了"后要补充说明具体写到哪里了
- 写入位置:USER.md(用户规则)或相关项目文件
- 配置完任何东西后**立即主动汇报结果**
- 不要等主人问"怎么样了"
- 教训:Edge TTS配置好后没有主动告诉主人
- 主人有知识库:`~/Documents/KnowLedgeDatabase/`
- 主人提问时,**先检索知识库**
- 如果知识库已有记录,告诉主人"这是来自知识库的答案"
- 如果知识库没有,再搜索或查找其他来源

---


### 30. 派 ACP Builder/Tester subagent 跑代码改动前, 必先配 approve-all + restart gateway(教训:2026-06-13)

- **情境**:2026-06-13 20:00 派 Builder v0.6.2-B subagent 跑代码改动, subagent 撞 OpenClaw permission gate, 写文件被拒
- **根因**:
  - 派活**前**主 agent 以为 `permissionMode approve-all` **没**配 (subagent 报告"未配")
  - **实际**查证: `openclaw config get plugins.entries.acpx.config.permissionMode` 返回 `approve-all` (值正确)
  - **但是** `openclaw gateway restart` **没**跑过 → ACP runtime 还在用**旧**配置 → 新值不生效 → 撞 gate
  - **更深根因**: "approve-all" 配了**没** restart gateway, 等于**没**配
- **坑的表现**:
  - Builder ACP subagent 报告 `tool permission denied` / `non-interactive permission unavailable`
  - 写文件 (edit / write) 被 silent reject, subagent 报"我自己干不了"
  - runtime 看起来**正常** (5-15 分钟) 但**实际**啥都没改
- **规则(铁律)**:
  1. **派 ACP Builder/Tester subagent 跑代码改动前**, **必**先跑:
     ```bash
     openclaw config get plugins.entries.acpx.config.permissionMode  # 验证是 approve-all
     openclaw config set plugins.entries.acpx.config.permissionMode approve-all  # 保险再设一次
     openclaw gateway restart  # 必**重启**, 否则新值不生效
     ```
  2. **不**靠"之前好像配过" — 每次派活**前**必 verify (`config get` + `restart` 已发生)
  3. 如果 subagent 报告"permission gate" / "permission denied" / "non-interactive permission unavailable" → **立刻**停下来, **不**让 subagent 继续乱试
- **per #10 教训实战** (v0.6.2-B):
  - 撞 gate 后, Builder 报告"主 agent 接手" (per #10 决策) — 主 agent 直接实施代码改动
  - 但**应该**是: 撞 gate **立刻** + restart gateway + 重派 subagent (而不是自己干)
  - 这次自己干是因为撞 gate 报告**晚**(完工报告里才说), **下次**应该 subagent 撞 gate **立刻**触发主 agent 查 config + restart
- **加固**:
  - 在 `agentWorkflowAndTemplates/runbook.md` 阶段 B 派 Builder subagent 段**加** "派活前必跑" 段: `config get permissionMode` + `restart gateway`
  - 在 `agentWorkflowAndTemplates/control-claude.md` ACP 段**加** "permission gate 必查" warning
- **关联**:
  - AGENT_PRACTICES #18 ACP 启用步骤 (v1/v2/v3 故事, 配 approve-all 在 v3)
  - AGENT_PRACTICES #20.1 sessions_yield 不等 done 事件
  - MEMORY #10 subagent 失败 → 立刻自己接手 (这次的兜底, 但**不是首选**)
- **避免**:
  - ❌ **不**信"approve-all 之前配过" (没 restart 等于没配)
  - ❌ **不**让 subagent 撞 gate 后**继续**乱试 (浪费 runtime + 可能产生半成品)
  - ❌ **不**忘 restart gateway (设了值**没** restart 跟没设一样)



### 31. v0.6.x 工作流修订 v3 — A 完后 B/C/debug build 全自动, debug 出才通知主人 (教训:2026-06-13 22:20)

- **触发**: 2026-06-13 22:20 主人纠正 v0.6.2 阶段 C 卡住问 "debug build 怎么 trigger" 失误
- **v3 核心**: A 完 (主人 + Jarvis 经 Claude 确认方案 + 落实 MEETINGS) → **B → C → D (debug build trigger) 全自动** → debug 出才通知
- **B/C 全自动**: 子任务实施 + 验收 + commit + push, 中间不打扰
- **bug 自动修**: 主 agent 评估范围, 当前子任务内修; 超出开新子任务
- **测试不通过自动修**: 主 agent 区分错 (实施/任务书/测试), 自动修
- **debug build trigger 主 agent 自己跑** (per v3 主人原话): 必 verify env (per #30):
  - `which gh` 或 `brew list gh` (没装就 `brew install gh`)
  - `security find-internet-password -s github.com -w` (Keychain token, 10s 超时)
  - `openclaw config get plugins.entries.github` (OpenClaw github 集成)
  - 缺啥**主 agent 自己装**, **不**问主人
  - 用 gh / curl+token / OpenClaw github 集成 触发 `workflow_dispatch build.yml build_type=debug`
- **debug build 出 → 通知主人验收** (唯一自动链终止点)
- **release 仍主人决定**: debug 实测通过后, 主人通知主 agent 出 release
- **例外通知** (per #28/#29 + v3): trade-off 决策 / 方向缺失 / 3 次 debug build 都 FAIL
- **推 git tag 必先 trigger debug build**: push tag 触发 release workflow (auto), v0.6.2 失误就因推 tag 跳过 debug
- **关联**:
  - `agentWorkflowAndTemplates/runbook.md` — 阶段 B/C 顶部 + 新阶段 D 段
  - `AGENT_PRACTICES.md` #31 — 完整版
  - MEMORY #10 (subagent 失败主 agent 接手) + #28 (不打扰) + #29 (pass 默认走) + #30 (verify env)
  - AGENT_PRACTICES #30 (verify env before ACP subagent) + #31 (本条)


## 📋 任务说明

### 小红书总结
- 主人通过 QQ 发送小红书链接
- 我总结并保存到 `~/Documents/KnowLedgeDatabase/XHS/`
- 格式参考已有的 md 文件
- **必须同时分析图片**(用 vision 模型解析图片中的文字、表格、截图)
- **图片也要保存到知识库**:下载图片到对应文件夹,用 Markdown 图片引用

### 技术帖子汇总
- 主人通过 QQ 发送技术帖子链接
- 汇总到 `~/Documents/KnowLedgeDatabase/techDocs/` 目录
- 按技术领域分类
- 同一主题多篇帖子要**合并提炼**
- **图片也要保存到知识库**:下载图片到对应文件夹,用 Markdown 图片引用

---

## 🔧 TOOLS & SKILLS

### 已配置的 MCP
- **xiaohongshu (xhs)**:通过 mcporter 连接 aredink.com
- 配置:`~/.openclaw/workspace/config/mcporter.json`

### 工作目录
- `~/Documents/KnowLedgeDatabase/XHS/` - 小红书总结
- `~/Documents/KnowLedgeDatabase/techDocs/` - 技术帖子汇总
- `~/Documents/KnowLedgeDatabase/` - 知识库根目录

---

## 📅 SESSIONS & EVENTS

### 2026-03-21
- 主人赋予我身份:Jarvis,贴身助手
- 配置了小红书 MCP(x-mcp 服务商 aredink.com)
- 安装了 mcporter 并配置了 xhs MCP 服务器
- 学会了海航 PLUS 会员抢票攻略并保存

