# intake-schema · 输入资料与清单字段约定

## 一、可接收的资料类型

| source_type | 典型形态 | 提炼重点 |
|---|---|---|
| `doc` | 文档、手册、Wiki、PDF 摘抄 | 结论、命令/路径、口径、版本号 |
| `case` | 真实案例、复盘、事故记录 | 现象→根因→修法→防范 |
| `note` | 个人笔记、随手记、聊天整理 | 先补全六段，缺失处标"待确认" |
| `rule` | 规则、规范、checklist、约定 | 条目化、标注适用范围（哪条线/哪层） |

## 二、intake manifest（JSON）字段

### 顶层

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `intake_id` | string | 建议 | 本次导入批次标识，如 `2026-11-19-community-xxx` |
| `intake_date` | string | 建议 | YYYY-MM-DD |
| `contributor` | string | 建议 | 来源作者/社区，须脱敏 |
| `source_type` | string | 建议 | doc/case/note/rule |
| `items` | array | 必须 | 经验条目数组，见下 |

### items[] 单条

| 字段 | 类型 | 必填 | 合法值/说明 |
|---|---|---|---|
| `date` | string | ✅ | YYYY-MM-DD |
| `title` | string | ✅ | 一句话标题，结论式 |
| `source` | string | ✅ | 来源溯源；外部资料脱敏 |
| `layer` | string | ✅ | `通用` / `项目` |
| `category` | string | ✅ | 版本变化/新坑/新工具用法/作者问题/口径更新/性能/其它 |
| `lines` | array | ✅ | 项目层填 `4.6`/`4.7`；通用层填 `["通用"]` 或具体游戏名 |
| `severity` | string | ✅ | `info`/`warn`/`error` |
| `supersedes` | string | 否 | 推翻旧结论时填被替换的 `references/xx.md §章节` |
| `phenomenon` | string | 建议 | 现象/触发；错误贴日志原文，变量用 `{…}` |
| `conclusion` | string | 建议 | 一句话答案，结论先行 |
| `evidence` | string | 建议 | 出处 + 可复核数字；多行用 `\n` |
| `fix` | string | 建议 | 可直接复制的步骤/命令 |
| `prevention` | string | 建议 | 防复发措施 |
| `related` | string | 建议 | 关联的 references 章节/错误码 |

## 三、脱敏规则（铁律 1）

导入前必须替换以下信息，变量统一用花括号：

| 敏感项 | 替换为 |
|---|---|
| 本机绝对路径 `C:\Users\xxx\...` | `{项目目录}` / `{启动器目录}` |
| 账号、昵称、邮箱 | `{作者}` / `{用户}` |
| 真实角色名、存档名 | `{角色}` / `{存档}` |
| 联机凭据、token、IP | 整段删除，不留 |
| 具体日期时间（非必要） | 保留日期、可模糊时间 |

## 四、可信度分级（决定措辞，不决定真伪）

| 级别 | 依据 | 入库措辞 |
|---|---|---|
| A · 实测 | 命令输出/日志原文/前后数字 | 直接陈述，照抄关键数字 |
| B · 权威文档 | 官方手册/权威 reference | 标注出处章节 |
| C · 经验判断 | 社区笔记/个人观点 | 标注"据社区经验，待版本作者确认" |

本技能不伪造级别；原始资料没给出的依据，`evidence` 就写"来源未提供可复核依据（C 级）"。
