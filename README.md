# Case Interview Coach

A Claude skill for consulting case interview training. Two strictly separated session modes on one
shared methodology base, and a self-contained HTML report at the end of every session.

**[English](#english) · [中文](#中文)**

---

# English

## Contents

- [What this is](#what-this-is)
- [The two modes](#the-two-modes)
- [What you get at the end of a session](#what-you-get-at-the-end-of-a-session)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Verifying the install](#verifying-the-install)
- [Your first session](#your-first-session)
- [Where your data lives](#where-your-data-lives)
- [Cross-session progress](#cross-session-progress)
- [Running the tests](#running-the-tests)
- [Repository layout](#repository-layout)
- [Known limitations](#known-limitations)
- [Methodology and sources](#methodology-and-sources)
- [License](#license)

## What this is

Practising case interviews alone has two failure modes. Practise with a tutor and you never find
out whether you can do it unaided. Practise with a realistic interviewer and you get no teaching.
Most tools blur the two, which produces a session that is neither: hints that make the score
meaningless, or silence that teaches nothing.

This skill separates them into two session modes and **fixes the mode for the whole session**.
Which mode you are in determines the purpose of the session and the meaning of its evaluation, so
it cannot change halfway through. Changing mode means ending the session and starting a new one.

## The two modes

| | Interview Mode | Tutorial Mode |
|---|---|---|
| Feels like | a real MBB-style interview | working through it with a coach |
| During the case | no hints, no corrections, no "good framework", neutral tone | explanation, hints, diagnosis, retries |
| Question it answers | "If this were real, how did I do?" | "What did I learn, and what can I do unaided?" |
| Ends with | score per dimension + Strong Hire / Hire / Borderline / No Hire | mastery, independence, hint dependence, next training plan |
| Hiring verdict | yes | **never** (unless you explicitly ask to be benchmarked) |

Both modes reason from the same methodology: structures are built from the client's objective and
the arithmetic of the business rather than recalled from a framework list; every number ends in a
"so what"; the recommendation answers the question asked in its first sentence.

Tutorial Mode has an assistance level you can dial down to zero mid-session — but a
zero-assistance Tutorial session is **still Tutorial Mode**. It never issues a hiring verdict, and
its review reports assisted and independent performance separately instead of averaging them into
one misleading number. A genuine unassisted assessment requires an Interview Mode session on a
case you have not seen.

## What you get at the end of a session

One self-contained HTML file. Both report types share a visual system but differ in content and in
what their numbers mean:

- **Interview report** — case details, overall score and hiring band, a one-line causal diagnosis,
  six capability meters, strengths and the detractors that actually cost you the result, key
  moments, insights you did not reach, the interviewer assistance you needed, a stronger line of
  analysis, your recommendation against a stronger one, and what to train next.
- **Tutorial report** — session focus, a one-line learning summary, capability *with independence
  level* for each dimension, hint dependence per topic across reps, assisted and independent
  phases evaluated separately, learning moments, recurring mistakes, a mastery check, and a next
  training plan.

Three rules are enforced in the renderer rather than left to prose:

1. A tutorial report cannot emit a hiring band without an explicit benchmark request.
2. An untested dimension cannot carry a number.
3. Percentiles, offer probabilities and invented firm benchmarks are rejected outright.

Violating any of them fails the build with a specific error and no output file, rather than
producing a plausible-looking report that says something the session cannot support.

Reports are single-file: inline CSS, no JavaScript required, no fonts, no CDN, no network calls.
They open offline by double-click and print to A4/Letter without splitting cards.

## Requirements

**Host environment.** Built and tested on **Claude Code**, which is the environment this skill
targets. It uses the standard `SKILL.md` + `references/` skill layout and invokes a local Python
script to render reports.

Other Claude surfaces that support the same skill format and can run a local script may work, but
**they have not been tested and are not claimed as supported.** If you try one, the renderer
smoke test below tells you quickly whether report generation works there.

**Python.** 3.8 or newer, available as `python3` on your PATH. **No third-party packages** — the
renderer and the test suite use the standard library only. There is nothing to `pip install`.

**Optional — cross-session memory.** Learner profiles need project-memory tools (`project_read` /
`project_write`). If the host does not provide them the skill degrades silently: sessions, cases,
scoring and reports all work exactly the same, and only cross-session continuity is lost. See
[Cross-session progress](#cross-session-progress).

## Quick start

**1. Clone into your skills directory**

```bash
git clone https://github.com/ShuchangZhang/case-interview-coach.git \
  ~/.claude/skills/case-interview-coach
```

**2. Load it**

Start a new Claude Code session, or reload skills in your current one. Skills are read at session
start, so an already-running session will not see a freshly cloned skill.

**3. Check it is there**

Ask for a case interview in plain language (see [below](#your-first-session)). If the skill
loaded, the first thing it does is settle which mode you want — before any case begins.

## Verifying the install

The report renderer can be exercised on its own, without running a session. This is the fastest
way to confirm the clone is complete and your Python works:

```bash
cd ~/.claude/skills/case-interview-coach
python3 scripts/build_report.py examples/interview-report.json -o interview-report.html
python3 scripts/build_report.py examples/tutorial-report.json  -o tutorial-report.html
```

Each command prints `Wrote <file> (N bytes)` and exits 0. Open either file in a browser: you
should see a complete, styled report built from the bundled fictional example.

The script resolves its own location, so an absolute invocation works from any directory:

```bash
python3 ~/.claude/skills/case-interview-coach/scripts/build_report.py \
  --example tutorial -o /tmp/demo.html
```

**On invalid input** the renderer writes no file, prints a `ValidationError` naming the field, the
value it received and the legal range, and exits with status 2:

```
ValidationError: dimensions[0].score must be a finite number between 0 and 10; received 100
No HTML was written.
```

Exit codes: `0` success · `2` validation or guard-rail failure · `1` usage or I/O error.

## Your first session

Say what you want in plain language, in English or Chinese. If the mode is ambiguous the skill
asks once, then locks it for the session.

```
Run a consulting case interview in Interview Mode.

I'm new to case interviews — teach me from scratch.

Advanced profitability case, interviewee-led, interview mode.

Market sizing drill, five reps, tutorial mode.

Here's a casebook PDF — run case 3 as an interview.
```

To switch modes, end the current session and start a new one. This is deliberate: a case whose
answers you have already seen cannot produce a valid assessment.

## Where your data lives

Everything runs locally. The renderer is a local Python script; it makes no network requests, and
the HTML it produces contains no external references, no scripts and no tracking.

**Generated reports may contain excerpts of your case-interview answers, capability assessments,
your mistakes and your learning progress.** Review a report before uploading it anywhere public or
sharing it with anyone.

Your conversation with Claude is of course governed by the host application's own data handling —
that is outside this repository's control.

## Cross-session progress

If the host provides project-memory tools, the skill keeps a learner profile so later sessions can
calibrate difficulty, track recurring mistakes and notice when hint dependence falls.

**This depends entirely on the host environment.** Where those tools are unavailable the skill
skips the profile silently — nothing errors, nothing blocks, and the session review still covers
everything from the current session. Reports never claim a cross-session trend unless a profile
was actually read.

## Running the tests

```bash
cd ~/.claude/skills/case-interview-coach
python3 -m unittest discover -s tests -v
```

Standard library `unittest`; no dependencies. Every fixture the suite references is committed
under `tests/fixtures/`, so the results are reproducible from a fresh clone. The suite covers:
both examples rendering; working-directory independence; untested dimensions showing as N/A;
tutorial reports never showing a hiring band; markup in user text being escaped rather than
executed; output containing no external references; and one fixture per invalid input — bad mode,
bad completion status, bad assistance level, score above 10, negative score, `NaN`, string score,
untested dimension carrying a score, inconsistent verdict flags, mode-specific fields in the wrong
report, a tutorial hiring verdict, and three guard-rail violations — each of which must exit 2 and
write nothing.

## Repository layout

| Path | Contents |
|---|---|
| `SKILL.md` | Router. Mode/State/Assistance model, both state machines, setup, session boundaries, time budgets |
| `references/case-methodology.md` | Case arc, structuring, hypothesis loop, exhibits, brainstorming, synthesis, communication |
| `references/case-math.md` | Quant discipline, formulas, mental math, sanity checks, market sizing |
| `references/case-taxonomy.md` | 14 archetypes plus mixed cases: objectives, signals, modules, diagnostic trees, quant, exhibits, mistakes |
| `references/case-generation.md` | Blueprint-first protocol, exhibit and quant design, consistency check, user-supplied cases, difficulty, geography |
| `references/interview-mode.md` | Interviewer protocol, prohibitions, information release, tone, both format spines, feedback and debrief |
| `references/tutorial-mode.md` | Teaching loop, beginner curriculum, progression ladder, drills, hint ladder, error diagnosis, session review |
| `references/evaluation-rubric.md` | Six dimensions with behavioural anchors, non-averaging hire bands, incomplete-case rules, mastery levels |
| `references/report-system.md` | Session Report schema, per-mode report specs, validation rules, visual system |
| `references/research-notes.md` | Source tiers, cited sources, and which principles are sourced versus designed |
| `scripts/build_report.py` | Session Report JSON to self-contained HTML |
| `examples/` | Two runnable example reports |
| `tests/` | Test suite and committed fixtures |
| `docs/` | Design rationale and validation history |

## Known limitations

- **Tested on Claude Code only.** Other environments may work; none have been verified.
- **Cross-session progress depends on the host** providing project-memory tools.
- **The guard-rail scan is pattern-based.** It catches the named categories of unsupported claim —
  percentiles, offer probabilities, invented benchmarks — not every possible invented statistic.
  It is a backstop for the rule, not a replacement for it.
- **No automated security audit has been run.** The renderer escapes untrusted text and makes no
  network calls, and the test suite checks both; that is the extent of the claim.
- **Reports are light-theme in print.** Dark mode is supported on screen; printing forces light.
- **Scoring is a training instrument.** The bands are calibrated to published descriptions of what
  firms assess, not to any firm's internal hiring bar.

## Methodology and sources

Built from firm-official recruiting material, convergent conclusions across established
preparation resources, and case architecture study of firm-published sample cases. No case content
is reproduced.

Every source relied on is listed with URL and access date in
[`references/research-notes.md`](references/research-notes.md) §1.1, which also separates what
came from official firm material, what is a convergent conclusion across independent sources, and
what is this project's own design decision.

**Not affiliated with or endorsed by McKinsey, BCG, Bain, or any other firm.** Firm names are used
only to describe publicly documented interview practices.

## License

[MIT](LICENSE). Applies to the whole repository — code, skill configuration, methodology files,
documentation, examples and tests alike.

---

# 中文

## 目录

- [这是什么](#这是什么)
- [两种模式](#两种模式)
- [Session 结束后你会得到什么](#session-结束后你会得到什么)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [验证安装](#验证安装)
- [第一次 Session](#第一次-session)
- [数据保存在哪里](#数据保存在哪里)
- [跨 Session 进度](#跨-session-进度)
- [运行测试](#运行测试)
- [仓库结构](#仓库结构)
- [已知限制](#已知限制)
- [方法论与来源](#方法论与来源)
- [许可证](#许可证)

## 这是什么

一个人练 Case Interview 有两种失败方式:找教练练,你永远不知道自己脱离提示能不能做出来;找一个
真实的面试官练,你什么也学不到。大多数工具把两者混在一起,结果是两头不靠 —— 要么提示多到分数
失去意义,要么沉默到没有教学价值。

这个 Skill 把两者拆成两种 session mode,并且**在整个 session 内锁定 mode**。Mode 决定了这次
session 的目的和评价的语义,所以它不能中途改变。换 mode 意味着结束当前 session,重新开一个。

## 两种模式

| | Interview Mode | Tutorial Mode |
|---|---|---|
| 体感 | 一场真实的 MBB 风格面试 | 有教练带着做 |
| Case 进行中 | 不提示、不纠错、不说"框架不错",语气中性 | 讲解、提示、诊断、重做 |
| 回答的问题 | "如果这是真的,我表现如何?" | "我学会了什么?哪些能独立完成?" |
| 结束时给出 | 各维度评分 + Strong Hire / Hire / Borderline / No Hire | 掌握程度、独立程度、提示依赖、下一阶段训练计划 |
| 招聘结论 | 有 | **没有**(除非你明确要求 benchmark) |

两种模式共用同一套方法论:结构从客户目标和这门生意的算式出发,而不是从背过的框架列表里挑;每个
数字都要落到"所以呢";最终建议在第一句话就回答客户问的问题。

Tutorial Mode 的辅助强度可以中途调到零 —— 但零辅助的 Tutorial session **仍然是 Tutorial
Mode**。它不产出招聘结论,并且在复盘里把"有辅助"和"独立"的表现分开报告,而不是平均成一个会误导人
的总分。真正的无辅助评估需要开一个 Interview Mode session,用一道你没见过的 Case。

## Session 结束后你会得到什么

一个自包含的 HTML 文件。两种报告共享同一套视觉语言,但内容和数字的含义不同:

- **面试表现报告** —— Case 信息、总分与招聘档位、一句话因果诊断、六个能力条、优势与真正导致失分
  的问题、关键节点、你没抓到的洞察、你用掉的 interviewer 帮助、更强的分析路径、你的建议与更强
  版本的对比、下一次训练重点。
- **学习诊断报告** —— 本次训练重点、一句话学习总结、每个能力的**表现 + 独立程度**、各主题的提示
  依赖随练习次数的变化、教学阶段与独立阶段分开评价、关键学习节点、反复出现的问题、掌握程度盘点、
  下一阶段训练计划。

有三条规则写在渲染器代码里,而不是留给文字约定:

1. Tutorial 报告在没有明确 benchmark 请求时不能出现招聘档位。
2. 未测试的维度不能带分数。
3. Percentile、录取概率、编造的公司 benchmark 一律拒绝。

违反任何一条会让构建失败并给出具体错误,不生成文件 —— 而不是产出一份看起来正常、但说了这次
session 无法支撑的话的报告。

报告是单文件的:内联 CSS、不需要 JavaScript、不依赖字体、不依赖 CDN、不发网络请求。双击即可离线
打开,打印成 A4 / Letter 时卡片不会被截断。

## 环境要求

**宿主环境。** 在 **Claude Code** 上开发和测试,这是本 Skill 的目标环境。它使用标准的
`SKILL.md` + `references/` 结构,并调用一个本地 Python 脚本生成报告。

其他支持同样 Skill 格式、且能运行本地脚本的 Claude 环境可能可用,但**未经测试,不作为已支持环境
声明**。如果你要试,下面的渲染器 smoke test 能最快告诉你报告生成在那里是否正常。

**Python。** 3.8 或更高,且 `python3` 在 PATH 中。**不需要任何第三方包** —— 渲染器和测试套件
只用标准库,没有需要 `pip install` 的东西。

**可选 —— 跨 session 记忆。** Learner profile 需要 project memory 工具(`project_read` /
`project_write`)。如果宿主环境没有提供,Skill 会静默降级:session、Case、评分、报告全部照常工作,
只是失去跨 session 的连续性。详见[跨 Session 进度](#跨-session-进度)。

## 快速开始

**1. Clone 到你的 skills 目录**

```bash
git clone https://github.com/ShuchangZhang/case-interview-coach.git \
  ~/.claude/skills/case-interview-coach
```

**2. 加载**

开一个新的 Claude Code session,或在当前 session 里重新加载 skills。Skill 在 session 启动时读取,
已经在运行的 session 看不到刚 clone 进去的 skill。

**3. 确认它在**

用自然语言要一道 case(见[下面](#第一次-session))。如果 skill 加载成功,它做的第一件事是确定你要
哪种 mode —— 在任何 case 开始之前。

## 验证安装

报告渲染器可以单独运行,不需要开 session。这是确认 clone 完整、Python 可用的最快方式:

```bash
cd ~/.claude/skills/case-interview-coach
python3 scripts/build_report.py examples/interview-report.json -o interview-report.html
python3 scripts/build_report.py examples/tutorial-report.json  -o tutorial-report.html
```

每条命令会打印 `Wrote <file> (N bytes)` 并以 0 退出。用浏览器打开任一文件,你应该看到一份完整
的、带样式的报告,内容来自仓库自带的虚构示例。

脚本会解析自己的位置,所以用绝对路径调用时在任何目录下都能工作:

```bash
python3 ~/.claude/skills/case-interview-coach/scripts/build_report.py \
  --example tutorial -o /tmp/demo.html
```

**遇到非法输入时**,渲染器不写文件,打印一条指明字段、收到的值和合法范围的 `ValidationError`,
并以状态码 2 退出:

```
ValidationError: dimensions[0].score must be a finite number between 0 and 10; received 100
No HTML was written.
```

退出码:`0` 成功 · `2` validation 或 guard-rail 失败 · `1` 用法或 I/O 错误。

## 第一次 Session

用自然语言说你要什么,中英文都可以。如果 mode 不明确,Skill 会问一次,然后在本次 session 内锁定。

```
给我做一次正式 mock,interviewee-led,advanced profitability case。

我完全没接触过 Case Interview,请从头教我。

Tutorial mode,只练 market sizing,五道。

我上传一份 casebook PDF,请把第 3 题当作正式面试来跑。
```

要换 mode,结束当前 session 再开一个新的。这是刻意设计的:一道你已经看过答案的 Case,无法再产出
有效的评估。

## 数据保存在哪里

全部在本地运行。渲染器是一个本地 Python 脚本,不发任何网络请求;它生成的 HTML 不含外部引用、不含
脚本、不含追踪代码。

**生成的报告可能包含你的 Case 回答片段、能力评价、你犯的错误和学习进度。** 在上传到任何公开位置
或分享给他人之前,请先看一遍内容。

你与 Claude 的对话本身当然受宿主应用自己的数据处理策略约束 —— 那不在本仓库的控制范围内。

## 跨 Session 进度

如果宿主环境提供 project memory 工具,Skill 会维护一份 learner profile,让后续 session 能够校准
难度、追踪反复出现的错误、并注意到提示依赖是否在下降。

**这完全取决于宿主环境。** 在没有这些工具的环境里,Skill 会静默跳过 profile —— 不报错、不阻塞,
本次 session 的复盘照样完整。只要没有真正读到 profile,报告就不会声称任何跨 session 趋势。

## 运行测试

```bash
cd ~/.claude/skills/case-interview-coach
python3 -m unittest discover -s tests -v
```

标准库 `unittest`,无依赖。测试引用的每一个 fixture 都已提交在 `tests/fixtures/` 下,所以从一份
全新 clone 就能复现结果。覆盖范围包括:两个示例都能渲染;不依赖当前工作目录;未测试维度显示为
N/A;Tutorial 报告永不出现招聘档位;用户文本里的标记被转义而不是被执行;输出中没有任何外部引用;
以及每一类非法输入各一个 fixture —— 错误的 mode、错误的完成状态、错误的辅助等级、分数大于 10、
负分、`NaN`、字符串分数、未测试维度带分数、verdict 标志自相矛盾、mode 专属字段出现在错误的报告
里、Tutorial 出现招聘 verdict、以及三种 guard-rail 违规 —— 每一个都必须以 2 退出且不写文件。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `SKILL.md` | 路由。Mode / State / Assistance 模型、两套状态机、setup、session 边界、时间预算 |
| `references/case-methodology.md` | Case 流程、结构化、假设循环、exhibit、brainstorming、synthesis、沟通 |
| `references/case-math.md` | 计算纪律、公式、心算、sanity check、market sizing |
| `references/case-taxonomy.md` | 14 种 archetype 与综合型:目标、信号、模块、诊断树、quant、exhibit、常见错误 |
| `references/case-generation.md` | Blueprint 优先流程、exhibit 与 quant 设计、一致性检查、用户上传 case、难度、地区 |
| `references/interview-mode.md` | Interviewer 协议、禁止项、信息释放、语气、两种形式主线、feedback 与 debrief |
| `references/tutorial-mode.md` | 教学循环、初学者课程、进阶阶梯、专项训练、提示阶梯、错误诊断、复盘 |
| `references/evaluation-rubric.md` | 六个维度的行为锚点、非平均的 hire 档位、未完成 case 规则、掌握等级 |
| `references/report-system.md` | Session Report schema、两种报告规范、validation 规则、视觉系统 |
| `references/research-notes.md` | 来源分层、引用清单,以及哪些原则来自来源、哪些是本项目的设计 |
| `scripts/build_report.py` | Session Report JSON 转自包含 HTML |
| `examples/` | 两个可直接运行的示例报告 |
| `tests/` | 测试套件与已提交的 fixture |
| `docs/` | 设计理由与验证记录 |

## 已知限制

- **只在 Claude Code 上测试过。** 其他环境可能可用,但都未经验证。
- **跨 session 进度取决于宿主环境**是否提供 project memory 工具。
- **Guard-rail 扫描基于模式匹配。** 它能抓住已列举的几类无依据声明 —— percentile、录取概率、
  编造的 benchmark —— 但不是每一种可能被编出来的统计数字。它是规则的兜底,不是规则的替代。
- **没有做过自动化安全审计。** 渲染器会转义不可信文本、不发网络请求,测试对这两点都有覆盖;声明
  仅限于此。
- **报告打印时强制浅色。** 屏幕上支持深色模式,打印固定为浅色。
- **评分是训练工具。** 档位是按公开资料中各家公司描述的考察点校准的,不等同于任何公司内部的实际
  招聘线。

## 方法论与来源

基于咨询公司官方招聘资料、多个成熟备考资源之间的共同结论,以及对公司公开 sample case 的
架构研究。不复制任何 case 内容。

所有依赖的来源都带 URL 和访问日期列在
[`references/research-notes.md`](references/research-notes.md) §1.1,其中同时区分了:哪些来自官方
材料、哪些是多个独立来源的共同结论、哪些是本项目自己的设计决定。

**与 McKinsey、BCG、Bain 或任何其他公司均无关联,也未获其背书。** 提到公司名称仅用于描述公开
记载的面试实践。

## 许可证

[MIT](LICENSE)。适用于整个仓库 —— 代码、skill 配置、方法论文件、文档、示例与测试一视同仁。
