---
name: mod-experience-ingest
version: "1.0.0"
display_name: MOD 经验资料导入
display_name_en: MOD Experience Ingest
description: |
  把他人的 MOD 开发经验资料（文档/案例/笔记/规则）规范化导入我们的知识库并可用于检索。
  ①接收任意来源资料→按统一清单约定提炼为结构化条目；②校验分层/引擎线/必填项、去重、冲突检测；
  ③dry-run 预览确认后落库到 jjxf-project-engineer/experiences/，更新 README 索引；
  ④输出验证报告，确认新经验可被检索路由命中、可用于后续辅助开发。默认只读不写，需显式确认。
description_zh: |
  把他人的 MOD 开发经验资料（文档/案例/笔记/规则）规范化导入我们的知识库并可用于检索。
  ①接收任意来源资料→按统一清单约定提炼为结构化条目；②校验分层/引擎线/必填项、去重、冲突检测；
  ③dry-run 预览确认后落库到 jjxf-project-engineer/experiences/，更新 README 索引；
  ④输出验证报告，确认新经验可被检索路由命中、可用于后续辅助开发。默认只读不写，需显式确认。
description_en: |
  Ingest other people's MOD development experience material (docs/cases/notes/rules) into our
  knowledge base in a normalized, retrievable form. (1) Turn arbitrary source material into a
  structured intake manifest; (2) validate layer/line/required fields, de-duplicate, detect conflicts;
  (3) after a dry-run preview is confirmed, write entries into jjxf-project-engineer/experiences/
  and update the README index; (4) emit a verification report proving the new material is reachable
  by the retrieval router and usable for future assistance. Read-only by default; writes need explicit consent.
---

# MOD 经验资料导入（Skill）

把一个外部作者的经验资料，变成**我们知识库里可检索、可被引用的经验条目**。
它补足了主技能 jjxf-project-engineer 的《LEARNING.md》三条通道（作者反馈 / 知识库回流 / 知识升级）
里缺失的一环：**面向"他人资料批量导入"的确定性流程**。

## 何时触发

- 用户提供一份/一批 MOD 经验资料：文档、案例、笔记、规则、聊天记录整理、他人 FAQ。
- 用户说"把这个作者的经验加进知识库""导入这份踩坑笔记""别人的规则收进来"。
- 需要把散落的外部资料沉淀为可被专家后续检索、教学、排障引用的知识。

不触发：只是问一个知识点 → 走 `jjxf-project-engineer` 的正常检索；用户要改稳定核心 `references/` → 走 LEARNING.md 通道 C。

## 铁律（每次遵守）

1. **先脱敏**：外部资料含个人路径、账号、真实存档名、联机凭据 → 一律脱敏后再入库（变量用 `{…}`）。
2. **默认只读**：落库必须经用户明确确认；先用 dry-run 预览，绝不"边看边写"。
3. **不臆测真伪**：本技能做结构化搬运与校验，**不判断内容事实是否正确**；项目层经验的可信度由"出处 + 可复核数字"承载，拿不准的标注"待版本作者确认"。
4. **分层标注**：每条经验标 `layer`（通用/项目）与 `lines`（4.6/4.7/通用）；通用 Godot 经验与机甲旋风项目经验分开。
5. **去重与冲突**：与已有条目重复则跳过（除非 `--force`）；推翻旧结论的走 `supersedes` + LEARNING.md 通道 C，不静默覆盖。

## 关键流程（四步）

### 第 1 步 · 接收与提炼（资料 → 清单）

读取用户给的原始资料，按 `references/intake-schema.md` 的字段约定，提炼成一份
**intake manifest（JSON）**。模板见 `templates/intake-manifest.md`。
先只做"提炼"，不写库。提炼时执行铁律 1（脱敏）和铁律 4（分层）。

### 第 2 步 · 校验与去重

运行导入器做结构校验（dry-run）：

```bash
python3 scripts/ingest_experience.py <manifest.json> --report report.json
```

校验内容：必填字段、layer/category/severity/lines 合法值、日期格式、正文六段完整性、
清单内重复、以及与目标 `experiences/` 已有条目的重复。详见 `references/normalize-rules.md`。

### 第 3 步 · 用户确认后落库

把第 2 步报告给用户看（计划写入哪些文件、有无冲突）。用户确认后：

```bash
python3 scripts/ingest_experience.py <manifest.json> --commit
```

脚本写入 `<date>-<主题>.md` 到目标 experiences 目录，并在《README.md》的"已有条目"追加链接。

### 第 4 步 · 验证可检索

按 `references/verification.md` 逐项验证：文件存在、frontmatter 合法、README 已登记、
检索路由能命中（`SKILL.md` 的"真实案例/新经验 → experiences/ 目录"路由本就存在）、
新经验关键词可被后续问答引用。输出验证结论给用户。

## 数据格式与接口约定

- **输入**：intake manifest（JSON），字段定义见 `references/intake-schema.md`。
- **输出**：经验条目 Markdown，格式对齐 `templates/experience-entry.md` 的六段结构 + 扩展 frontmatter（`ingest_by`/`intake_id`）。
- **落库目标**：默认 `../jjxf-project-engineer/experiences/`（同级技能），可用 `--target` 覆盖。
- **索引**：`experiences/README.md` 的"已有条目"段。
- **报告**：`--report` 输出 JSON，含 errors/warnings/planned_files/conflicts/written。

## 模块清单

| 模块 | 路径 | 职责 |
|---|---|---|
| 技能入口 | `SKILL.md` | 触发条件、铁律、四步流程 |
| 输入约定 | `references/intake-schema.md` | 资料类型、字段定义、脱敏规则、可信度分级 |
| 规范化规则 | `references/normalize-rules.md` | 分层判定、去重、冲突、质量门槛 |
| 验证清单 | `references/verification.md` | 落库后可检索验证步骤 |
| 清单模板 | `templates/intake-manifest.md` | 可直接填写的 manifest 样例 |
| 条目模板 | `templates/experience-entry.md` | 经验条目六段格式 |
| 导入器 | `scripts/ingest_experience.py` | 校验/去重/落库/报告（标准库，dry-run 默认） |

## 与其它技能的关系

- 落库目标是 `jjxf-project-engineer/experiences/`——该 Skill 的 `SKILL.md` 检索路由已含
  "真实案例、新作者贡献的经验 → experiences/ 目录（按日期倒序）"，因此本技能导入的条目
  **自动进入专家的检索范围**，无需改主 Skill 路由。
- 若新经验推翻旧结论（重大变化），落库后仍按《LEARNING.md》通道 C 更新 references 与口径，
  并由主流程重新打包专家包。
