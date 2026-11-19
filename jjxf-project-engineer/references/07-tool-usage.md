# 07 · jjm_pack.py 使用细则（怎么读结果）

> 出处：对外知识库《03-启动器与工具/工具使用细则.md》（157 行）。命令清单见 `02-mod-toolchain.md`，
> 本篇专讲**怎么读结果**——退出码、报告字段、配对判定、共存判定、已知误报。

## 退出码（只有 3 种）

| 码 | 含义 | 典型场景 |
|---|---|---|
| `0` | 本次检查**没有 error**（可能有 warn） | check 全过；verify 是 ADMITTED |
| `1` | 有 error，检查未通过 | 锚点失配、缺字段、包读不了 |
| `2` | 命令或参数不认识 | 子命令拼错、缺必填参数 |

三个特殊点（作者最容易误判）：
1. **warn 不影响退出码**。`check --pair` 发现两包撞车也只给 warn，退出码仍 `0`。**必须看输出里有没有 `PAIR-01`/`PAIR-04`**。
2. **`seal` 多一个条件**：检查通过（或 `--force`）**且**记录写成功才返回 `0`；检查不过时不出记录，退出码 `1`。
3. **`--json` 不改变退出码**，只改输出格式。

## 报告怎么读

文本模式行首 `[错误]`/`[提示]`/`[通过]` = `error`/`warn`/`ok`；错误码是搜 `03-error-codes.md` 的入口；
`@ 位置`定位到第几条补丁/文件/行。最后一行「结果」是汇总，**只有错误数 0 才算通过**。

JSON 模式（`--json`）字段：`ok`（唯一判据，等价 errors==0）、`errors`/`warnings`（计数，便于 CI 卡阈值）、
`findings[]`（每条含 `level`/`code`/`where`/`message`）、`tool_version`/`spec_version`（归档回溯用）。

批量检查：
```bash
for f in *.zip; do python jjm_pack.py check "$f" --line 4.7 --json > "${f%.zip}.report.json"; done
```

## 六个子命令分工

| 命令 | 判什么 | 何时跑 |
|---|---|---|
| `check` | 包本身合不合规：结构/清单/锚点/钩子/源码/联机 | 每次改完 |
| `verify` | 能否一导入就过：schema 升格、接管三条件、位置重叠、依赖闭环 | 发布前 |
| `seal` | 跑完整 verify 后写 `verification.json`，绑定代码层指纹 | 发布前最后 |
| `pack` | 目录打 zip，打包前先自检 | 出包时 |
| `manifest` | 生成清单骨架，自动写 `sources.sha256` | 新建包 |
| `fix` | 从反解工程补自带基底 | 老包报 `SELF-01` |

**顺序不能反**：`check` → 修 → `verify` → `seal` → `pack`（或 pack 后再 seal）。先 seal 再改文件，记录立刻变 `stale`。

## `check --pair`：四种结果（都是 warn，退出码 0）

| 结果 | 含义 | 风险 | 怎么办 |
|---|---|---|---|
| `PAIR-OK` | 无位置重叠 | 无 | 可同时启用 |
| `PAIR-01` | 同文件同锚点/同数据键撞车 | **玩家侧默认后者生效**，先装改动被盖 | 收窄锚点 / 一方 `overrides`+`expect` / 二选一 |
| `PAIR-02` | 一方显式接管另一方（带 expect） | 可控，但有安装顺序要求 | 先装被接管方 |
| `PAIR-04` | 整文件或父子位置重叠 | 整份文件只能留一个，另一改动可能整体失效 | 改补丁方式或二选一 |

`PAIR-02` 不是"更严重的冲突"，是"已处置过的冲突"；真正担心 `PAIR-01`/`PAIR-04`。

## 钩子共存三档（`cli compat`，check --pair 只看静态位置）

| 档 | 含义 | 风险 |
|---|---|---|
| `safe` | 键不重叠，或双方都是"读—改—写" | 叠加生效，顺序无关 |
| `unknown` | 有一方写入没解析出来 | **需人工确认**：打开两包脚本比对改的是不是同一个键 |
| `clash` | 键真重叠（直接赋值）/一方整份替换 result/`before` 相位有人设 `skip_original` | 互相覆盖；`skip_original` 更严重——触发时后面的回调**整个不执行** |

`skip_original` 判定是静态的，看不出运行期条件，常是"可能冲突"。看到先核对是不是只在特定分支触发。

## 已知误报

`verify` 对 **schema 4** 的包也输出 `ADM-01 schema=4；启动器会自动升格…但 1/2 没有位置级 overrides…`。
这是工具判断条件还停留在"schema 必须是 3"，schema 4 也命中。**不影响结论（仍 ADMITTED）**，可忽略；
介意则把 schema 写成 3 再验一次。

## 最省事的自检组合

```bash
python jjm_pack.py check  pkg.zip --line 4.7          # 合规 + 准入
python jjm_pack.py verify pkg.zip --line 4.7          # 发布前
python jjm_pack.py check pkg.zip --pair 已发布.zip --line 4.7   # 共存
python jjm_pack.py seal  pkg.zip --line 4.7           # 签封 → pkg.sealed.zip
python jjm_pack.py verify pkg.zip --with 依赖A.zip --with 依赖B.zip --line 4.7  # 组合准入
```
