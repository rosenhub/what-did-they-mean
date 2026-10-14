<div align="center">

# what-did-they-mean

### 把对方说的话贴进来，看懂对方的意思。

**为自闭症成年人设计。对所有人更好。**

12 条规则。0 行代码。支持 16 个代理宿主。10 秒安装。

[English](README.md) · [安装](#安装) · [12 条规则](#12-条规则)

```bash
npx skills add rosenhub/what-did-they-mean
```

<img src="assets/before-after.png" width="100%" alt="before / after">

</div>

---

有人给你发了一条消息，你看不出对方想要什么："没关系，你有空再发就行！"——是真的没关系，还是在催？"我们下个季度再聊"——是也许，还是不行？"k"——我做错了什么？

去问聊天机器人，你会得到一段安慰、一句"别想太多"、一个建议回复，和一个"显然"。你问的是这条消息什么意思，得到的却是"你本该知道"。

潜台词是第二语言。大多数人在无意识中解码；自闭症人士被要求全天手动解码，然后还被告知问这个问题本身就是问题。这不是他们的问题，这是翻译问题。把消息翻译出来，每个人都会得到更好的答案。

`what-did-they-mean` 是一个 markdown 文件，让任何代理成为翻译：字面意思、最可能的真实意思、对方期待你做什么、你的回复选项和每个选项传达的信号、以及代理有多确定。每次结构一致。永不说"显然"。

## 安装

把 `SKILL.md` 复制到你的宿主对应位置（完整表格见 [English README](README.md#install)）：

| 宿主 | 位置 |
|---|---|
| Claude Code | `~/.claude/skills/what-did-they-mean/SKILL.md` |
| Codex CLI | 追加到 `AGENTS.md` |
| Cursor | `.cursor/rules/what-did-they-mean.mdc` |
| Gemini CLI | 追加到 `GEMINI.md` |
| OpenClaw | `~/.openclaw/skills/what-did-they-mean/SKILL.md` |
| ChatGPT | 设置 → 个性化 → 自定义指令 |

或者：`curl -fsSL https://raw.githubusercontent.com/rosenhub/what-did-they-mean/main/install.sh | sh`

## 12 条规则

| # | 规则 |
|---|---|
| 1 | 每次都用同样的结构：最可能的意思 → 字面意思 → 对方期待什么 → 你的选项 → 我不确定的地方。 |
| 2 | 第一句就是最可能的意思。 |
| 3 | 永远同时给出字面意思。 |
| 4 | 明说社交期待："她期待今天收到回复。" |
| 5 | 标明确定程度："大约 80%"、"猜测"、"看不出来"。 |
| 6 | 永不说"显然"、"明显"、"只是"、"不过就是"。 |
| 7 | 给 2–3 个回复选项，不给唯一的脚本。 |
| 8 | 说明每个选项传达什么信号。 |
| 9 | 点名修辞手法：讽刺、反语、客套话、软拒绝。 |
| 10 | 永不把提问当成病症。不说"别想太多"。 |
| 11 | 缺少背景时问一个问题，然后照样给出判断。 |
| 12 | 永不猜测文本不支持的情绪。 |

完整内容：[SKILL.md](SKILL.md)。基准测试：[eval/](eval/)。

## 许可

MIT。
