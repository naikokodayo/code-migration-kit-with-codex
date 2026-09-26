# code-migration-kit-with-codex

这是 [Anthropic 原仓库](https://github.com/anthropics/code-migration-kit-with-claude-code)
的独立 Codex 适配版，保留 Apache-2.0 许可、原作者版权和历史案例。
它用于跨语言迁移整个项目，不是把业务代码接入某个模型 API。

## 来源与致谢

本项目基于 **Anthropic 的
[code-migration-kit-with-claude-code](https://github.com/anthropics/code-migration-kit-with-claude-code)**
改编，上游基准提交为 `cf91c9d5068d9aaf95a36164169f08c3e636c909`。
迁移方法、原始提示词、脚本、模板、测试样例和历史案例均来自该仓库。
本项目的修改集中在 Codex 适配、中文说明与离线检查，不代表上述原始内容由本项目原创。

保留上游 Git 历史、Anthropic 版权声明和 [Apache-2.0 许可证](LICENSE)。
这是独立适配项目，并非 OpenAI 或 Anthropic 官方产品。
当前仓库：[naikokodayo/code-migration-kit-with-codex](https://github.com/naikokodayo/code-migration-kit-with-codex)。

## 已适配

- `CLAUDE.md` 改为 Codex 可读取的 `AGENTS.md`。
- 技能入口放在 `.agents/skills/code-migration/SKILL.md`。
- Claude 权限文件改为 `templates/migration.rules`，使用 Codex 原生执行规则。
- 八份阶段提示词调整为 Codex 工作流，保留独立审查、阶段确认与磁盘队列。
- 依赖分析、任务清单、队列和构建脚本继续使用 Python/Node.js/Bash，无新增依赖。

## 使用

需要 Python 3、Node.js、Bash 和已登录的 Codex。把完整工具包放在目标项目内
或旁边。下面的命令在**待迁移项目根目录**执行，并替换工具包绝对路径：

```sh
KIT=/absolute/path/to/code-migration-kit-with-codex
mkdir -p .agents/skills
ln -s "$KIT/.agents/skills/code-migration" .agents/skills/code-migration
```

已有同名技能时先检查，勿覆盖。工具包需保留在该路径，不能只复制 `SKILL.md`。
如果直接在本工具包根目录打开 Codex，则不需要创建上述链接。

将工具包的 `AGENTS.md` 合并进待迁移项目的同名文件，保留项目原有约定，并调整
其中指向工具包的路径。如果目标项目没有此文件，可以复制后修改路径。

在 Codex 中打开待迁移项目，输入：

```text
使用 $code-migration，评估将这个项目迁移到 Rust 的可行性。
先执行可行性评估，输出证据和建议，在阶段门结束。
```

将 Rust 换成目标语言。如果技能未显示，重新打开 Codex；也可以直接要求它阅读
工具包中的 `prompts/00-feasibility.md`。模型由你在可行性阶段选择，不绑定某个型号。
可行性评估会先核查可复用的目标语言开源项目及组件，并比对许可证、编译器版本、
依赖边界与原项目行为；已有同领域应用不自动等于可直接替换的迁移基础。

六阶段是：建立依赖图与规则 → 压力测试规则 → 批量翻译 → 编译 → 运行 → 行为对齐。
翻译前先验证行为测试工具；每个阶段完成后，由你启动下一阶段。

## 权限与独立审查

在阶段提示词 03 之前，按 [执行规则说明](templates/rules.README.md) 人工适配并安装
规则到待迁移项目的 `.codex/rules/migration.rules`，确认项目配置受信任并重启 Codex。
可行性评估和测试工具准备阶段需要运行构建/测试，因此不要提前安装循环禁令。

Codex 规则主要控制沙箱外命令，不能保证所有工具路径都无法调用编译器。
独立的人工作业进程负责构建和测试，工作代理读取结果；若需要严格隔离，应提供
不含编译器的工作环境。文件存在或离线规则匹配通过，不等于运行时已完全隔离。

多代理能力可用时使用 Codex 子代理；否则使用相互独立的 Codex 会话。
单会话中的多次自查不能当作独立审查，盲测翻译也不能继承规则手册或聊天历史。

## 验证与范围

在工具包根目录执行：

```sh
python3 scripts/check_kit.py
```

检查原始依赖图样例、清单转换、队列、构建进程和 Codex 规则匹配，不调用模型。
本适配版尚未在 Codex 中完成真实项目的端到端跨语言迁移。
`RUN-NOTES.md` 和 `examples/` 是原仓库历史材料，里面保留的 Claude 名称不是运行依赖。

英文完整流程：[README.md](README.md)。
官方文档：[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、
[技能](https://learn.chatgpt.com/docs/build-skills)、
[执行规则](https://learn.chatgpt.com/docs/agent-configuration/rules)。
