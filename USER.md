# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:**
- **What to call them:** 主人
- **Pronouns:** _(optional)_
- **Timezone:** Asia/Shanghai
- **Notes:**

## Context

- **小红书总结**：用户通过 QQ 发送小红书链接 → 我总结并保存到 `~/Documents/KnowLedgeDatabase/XHS/` 目录
  - **格式要求**：
    1. 帖子主要内容
    2. 评论态度总结
    3. 注意事项：有些 xhs 帖子喜欢把核心内容发布到帖子的图片上，要记得解析帖子的图片

- **技术帖子汇总**：用户通过 QQ 发送技术帖子链接 → 我汇总到 `~/Documents/KnowLedgeDatabase/techDocs/` 目录，按技术领域分类。同一主题多篇帖子要**合并提炼**，重复内容合并，不同内容补充。完成后返回存放位置。

- **有声书制作（ebook-tts）**：主人的电子书有声书任务
  - **Skill 位置**：`~/.openclaw/workspace/ebook-tts/`
  - **支持格式**：txt、epub、mobi、pdf
  - **输出目录**：`~/Documents/TTSoutputs/{书名}/`
  - **工作流程**：
    1. 收到电子书文件，解析为纯文本
    2. 按章节分割为多个 .txt 文件
    3. 每个章节用 edge-tts 生成 .mp3 语音
  - **任务性质**：耗时任务，交给**子 agent**处理，主 agent 保持可用
  - **脚本**：
    - `convert_ebook.py` - 转换各格式为 txt
    - `generate_tts.py` - 章节分割 + TTS 生成

- **知识库优先**：主人提问时，先检索知识库 `~/Documents/KnowLedgeDatabase/`。如果已有记录，告诉主人"这是来自知识库的答案"。知识库可能不全，觉得不够全面解答主人的问题时，记得补充。

## 项目状态
- 小红书 MCP 已配置并正常工作（xhs 服务连接到 aredink.com）

## ⚠️ 重要规则
- **TTS 语音回复**：主人不喜欢每条都发语音，**不要**使用 TTS 语音回复（edge-tts 配置已关闭或改回文字）
- **安装许可原则**：安装任何插件、skill、MCP 或其他功能，必须先经过主人许可才能操作
- **禁止金钱交易**：不主动产生任何有金钱交易相关的动作
- **安全甄别**：仔细甄别网络来源内容是否影响系统运行安全
- **确认原则**：遇到相关问题，需要向主人确认

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.
