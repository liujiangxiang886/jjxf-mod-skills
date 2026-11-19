# 13 · 共存与冲突实战（真实 `check --pair` 输出）

> 出处：交付包《06-经验沉淀/共存与冲突实战.md》（181 行，2026-11-17 实测，终端原文未改写）。
> 补充 `07-tool-usage.md` 的判定规则，加了方向性、非直觉细节与真实输出。

## 先分清两种"冲突"

| 类型 | 何时查 | 用什么 | 判什么 |
|---|---|---|---|
| **位置冲突**（文件/数据键/文本锚点） | 打包期，无需安装 | `jjm_pack.py check --pair A B` | 两包是否抢同一位置 |
| **钩子键冲突**（同一点改同一 key） | **装完之后** | `cli ext-audit <线>` / 扩展页体检条 | 回调之间是否互相覆盖 |

**`check --pair` 不判钩子**。"pair 过了就没事"是常见误判。

## 真实输出：`check a.zip --pair b.zip --line 4.7`

两包都改 `scripts/interactable.gd` 同一句对话。输出（原文节选）：
```
[提示] PAIR-04 me.rival_a 的 files[0] 与 me.rival_b 的 files[0] 撞在同一处：
       mods/me.guide_demo/main.gd 整份文件。玩家侧默认后者生效…
[提示] PAIR-01 … data_patches[0].operations[0] 撞在同一处：data/start_page.json /mods_guide_demo …
[提示] PAIR-01 … text_patches[0] 撞在同一处：scripts/interactable.gd @export var dialogue … 
结果：错误 0，提示 3，通过
```
**退出码仍是 0**（PAIR-* 全是 warn）。只看退出码等于没看。
`PAIR-04 整份文件`最易忽略——扩展 id 不同、目标路径却撞了。

## 化解：`overrides` + `expect` + `requires`

在**接管方**那条改动上写：
```jsonc
{ "target":"scripts/interactable.gd", "find":"…原句…", "replace":"…新句…",
  "expect_count":1,
  "overrides":["me.rival_b"],                        // 点名被接管的包
  "expect":{"eq":"@export var dialogue: String = \"…\""} }
```
顶层补 `"requires":["me.rival_b"]`（启动器据此排序：先装被接管方）。
改后重跑 pair，第三条从 `PAIR-01` 变 `PAIR-02`（已处置）：
`PAIR-02 … 显式接管了 me.rival_b（带 expect 断言）…装的时候要先装 me.rival_b`。

### 三个非直觉细节（实测踩出来的，务必记住）

1. **`overrides` 必须写在 `--pair` 的第一个参数那一侧**。判定代码
   `authorized = right_id in a["overrides"] and a["expect"] is not None`，`a` 来自**第一个包**。
   写在第二个包上、却按 `check A --pair B` 跑 → **仍是 `PAIR-01`**。
   要么写在 A 上，要么换成 `check B --pair A`。
2. **只对 text_patches 写 `overrides`+`expect`，打包检查不校验这对字段**。
   `MAN-22/23/25` 只挂在 `data_patches.operations` 和 `files` 上；text_patches 层没接。
   文本补丁写错 `overrides` 不报错——只有 `check --pair` 会用。
3. **文本补丁的 `expect` 只是"宣告"，不是运行期断言**。运行期真正断言的是
   `data_patches.operations[*].expect`（`patcher.assert_expect`：eq/ne/exists/type/sha256/size）。
   文本补丁只校验 `expect_count` 命中数。**别指望 expect 在玩家机器上挡住版本漂移。**

## `requires` 为什么必须写

不写 `requires` 不报错，但**加载顺序没人保证**：玩家先装接管方，
接管方断言的"现在是什么"当时不成立，改动可能整条被拒。
`MAN-25`（只对 data_patches/files 触发）：`接管了 {id}，但 requires 里没写…先装被接管方`。

## 判定顺序（照走不会乱）

1. `check` 单包 → 0 错误；
2. `check --pair` 逐个比对已发布最小组合 → 记住每处 `PAIR-01/04`；
3. **能改路径/键的先改**（`PAIR-04` 正解是改路径，如 `mods/me.rival_a/main.gd` 各用各的），
   改完重跑到 `PAIR-OK`；
4. 改不动的才写 `overrides`+`expect`+`requires`，重跑应见 `PAIR-02`；
5. 安装（严格档）→ 看状态列与 `mod_report.json`；
6. `cli ext-audit 4.7` 看钩子三档；
7. 真启动一次，进游戏验证功能。

**先改路径/键，改不动才用接管**——接管要玩家按顺序装，成本更高。
第 2 步最容易被跳过，而它是唯一能在玩家之前发现"两个热门包互相盖"的环节。

## 钩子三档处置（`ext-audit`）

| 档 | 处置 |
|---|---|
| `safe` | 不管，叠加生效 |
| `unknown` | 人工比对两包脚本是不是改同一个键 |
| `clash`（直接赋值/整份替换）| 一方改成读—改—写，或二选一 |
| `clash`（`skip_original`）| 先核对触发条件（通常只在特定场景），再决定是否并存 |
