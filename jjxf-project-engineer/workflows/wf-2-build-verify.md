# WF-2 · 标准线打包与验证（4.6 / 4.7）

> 目标：把内容目录变成一份**可发布、装得上**的签封包。
> 适用：**标准线** 4.6 / 4.7。自定义/改版本体走 WF-3，不要混用。
> 核心心法：**完整顺序** —— `check` → `verify` → `compat` → `seal`（**对目录**）→ `pack` → 安装 → 冒烟。
> 出处：`references/11-command-reference.md`、`references/07-tool-usage.md`

---

## 第 1 步 · 明确完整关卡（先纠正"check 过了就能装"的误解）

**【目标】** 让用户理解发布前的完整链路，避免后面反复困惑。

**【你要做的】** 讲清六段（出处：`11-command-reference.md`；`02-mod-toolchain.md` §从 check 到生效）：

| 段 | 命令/动作 | 没过的典型表现 |
|---|---|---|
| ① 基础检查 | `check`（目录即可，不必先 pack） | 结构/清单/锚点/源码不合错误码 |
| ② 准入预检 | `verify` | 非 ADMITTED |
| ③ **真实命中预检** | `cli compat <包> --line <线>` | 补丁命中数 < 预期（**安装前唯一能回答"补丁在这条线命不命中"的工具**，无 GUI） |
| ④ 签封 | `seal` **对目录** → `verification.json` | 没签封 → `verify.absent`，导入被剔除 |
| ⑤ 出包 + 安装闸门 | `pack` → 安装器判 schema / 位置冲突 | `conflict.location` |
| ⑥ 挂载冒烟 | 启动一次游戏 | `install.smoke` / 状态不翻 `ready` |

**【怎么算过了】** 用户确认"check 全过只是第一步"，且知道 `compat` 要在安装前跑。
**【下一步】** 第 2 步，跑 verify。
**【出处】** `references/11-command-reference.md` §一/§二；`references/02-mod-toolchain.md`

---

## 第 2 步 · 跑 verify（发布前准入）

**【目标】** 确认这包"一导入就过"：schema 升格、接管三条件、位置重叠、依赖闭环。

**【你要做的】**

```bash
python tools/jjm_pack.py verify ./my_mod --line 4.7
```

若依赖其它包，加 `--with`：

```bash
python tools/jjm_pack.py verify ./my_mod.zip --with 依赖A.zip --line 4.7
```

**【怎么算过了】** 退出码 `0`，结论 `ADMITTED`。
**已知误报**：schema 4 的包也会输出 `ADM-01 schema=4...`，**不影响结论**（仍 ADMITTED），**忽略即可**。
**⚠️ 不要为了消这条警告把 schema 改回 3**——schema 4 才强制写 `sources` 三字段（声明锚点按哪份源码算的），
降回 3 等于把这件事丢掉（出处：`11-command-reference.md` §四误用 5；`07-tool-usage.md` §已知误报）。

**【下一步】** ADMITTED → 第 3 步 compat 真实命中预检。
**【卡住了】** 看错误码 → WF-5；依赖闭环问题回 WF-1 第 3 步补依赖声明。
**【出处】** `references/07-tool-usage.md` §六个子命令分工/§已知误报

---

## 第 3 步 · compat 真实命中预检（安装前最有价值的一步）

**【目标】** 在真实本体上试算补丁命中数——**唯一能在安装前回答"补丁在这条线到底命不命中"的工具**。

**【你要做的】**

```bash
"<启动器目录>/New state launcher.exe" cli compat <包.zip> --line 4.7
```

它是启动器内核 CLI（不是 jjm_pack），**不安装**，只按真实基线 pck 试算。
**没有 GUI 入口**——新手想看命中数只能走这条命令。

**【怎么算过了】** 看输出行，例如：
```
[OK  ] me.guide_demo  v1.0.0  补丁 2/2  覆盖 0 命中 / 1 新增
```
`补丁 2/2` = 声明的补丁都在真实本体命中；`覆盖 N 命中 / M 新增` = files 的情况。
**这一行比"装完看有没有效果"可靠得多**，也比装完再排障快。

**【下一步】** 命中数符合预期 → 第 4 步签封。
**【卡住了】** 命中数 < 预期（如 `补丁 1/2`）→ 锚点按错线算了 / 换行符 CRLF vs LF /
剧情层换了没重算 → 回 WF-1 第 3 步与 WF-5（锚点 0 命中），按真实源码重算后再 compat。
**【出处】** `references/11-command-reference.md` §二（compat）+ §三（无 GUI）；完整样例见 `examples/me.guide_demo-1.0.0.zip`（解压）

---

## 第 4 步 · seal 签封（**对目录做**，绑定代码层指纹）

**【目标】** 写 `verification.json`，让包与当前线代码层指纹绑定——这是很多"装了被剔除"的根因。

**【你要做的】**

```bash
python tools/jjm_pack.py seal ./my_mod --line 4.7     # 对目录签封 → 写 <目录>/verification.json
```

**⚠️ seal 必须对目录做，不要对 zip 做**（出处：`11-command-reference.md` §1.2）：
`check`/`verify`/`seal` 三者都同时接受目录与 zip，但**两种 seal 不等价**：

| 你对谁 seal | 产物 | `content_scope` | 装完还能否判"内容被改过" |
|---|---|---|---|
| **目录** | `<目录>/verification.json` | `dir` | **能**（推荐） |
| zip | `<原名>.sealed.zip`（不动原 zip） | `package` | **不能**——装完只比代码层，改了包内容也照样显示"已验证" |

所以统一流程是：**在目录上 seal，再 pack**（此时 zip 里已带 verification.json）。

**签封三个要点**（出处：`02-mod-toolchain.md` §签封要点）：
1. 需该线代码层指纹 `identity-<线>.json`，找不到报 `SEAL-03`。
2. `seal` 前必须 `check` 通过，否则 `SEAL-04` 拒绝写记录。
3. **`seal` 之后再改文件，记录立刻变 `stale`**——所以签封必须是改文件的最后一步。

**【怎么算过了】** 退出码 `0` 且目录里生成了 `verification.json`。
（`seal` 特殊：检查通过**且**记录写成功才返回 0；检查不过不出记录、返回 1。）

**【下一步】** 签封完成 → 第 5 步打包。
**【卡住了】** `SEAL-03/04` 或 `verify.stale` → WF-5 对应码；stale 就按当前版本重新 seal。
**【出处】** `references/11-command-reference.md` §1.2；`references/02-mod-toolchain.md` §签封要点

---

## 第 5 步 · pack 出包

**【目标】** 把已签封目录打成可发布的 zip。

**【你要做的】**

```bash
python tools/jjm_pack.py pack ./my_mod -o my_mod-1.0.0.zip
```

`pack` 只接受目录、打包前自检；此时 zip 里已带上 `verification.json`。

**【怎么算过了】** 生成 `my_mod-1.0.0.zip`，内含根目录 `extension.json` + `payload/` + `verification.json`。
**【下一步】** 第 6 步做共存判定（若玩家会同时装其它包）。
**【卡住了】** 打包自检报错 → WF-5。
**【出处】** `references/11-command-reference.md` §一；`references/02-mod-toolchain.md`

---

## 第 6 步 · 共存判定（多包场景，别跳过）

**【目标】** 避免与其它已发布包撞位置/撞钩子——玩家侧默认后者生效，先装的改动会被盖。

**【你要做的】** 与每个可能共存的包做 pair 检查：

```bash
python tools/jjm_pack.py check my_mod.zip --pair 已发布.zip --line 4.7
```

**读结果**（都是 warn，退出码仍为 0，**必须看输出里的码**，出处：`07-tool-usage.md` §check --pair）：
- `PAIR-OK`：无重叠，可同时启用。
- `PAIR-01`：同文件同锚点/同数据键撞车 → 收窄锚点 / 一方 `overrides`+`expect` / 二选一。
- `PAIR-02`：一方显式接管另一方（带 expect），可控，安装顺序要求：先装被接管方。
- `PAIR-04`：整文件或父子位置重叠 → 改补丁方式或二选一。

**⚠️ `overrides` 有方向性，别写反**（出处：`references/13-coexistence.md`；对照表 §3.5）：
- 判定是 `right_id in a["overrides"]`，`a` 来自 **`--pair` 的第一个包**；
- 所以 **`overrides` 必须写在第一个参数那一侧**，写在第二个包上仍报 `PAIR-01`；
- `MAN-22/23/25` 只校验 `data_patches.operations` 与 `files`，`text_patches` 上的 `overrides`/`expect`
  **打包检查不校验**，只有 `--pair` 会用；文本补丁的 `expect` 是"宣告接管"，**运行期不校验**
  （真正断言的是 `data_patches.operations[*].expect`）。

钩子共存另看三档（`safe` 叠加无顺序 / `unknown` 需人工比对改的是不是同一个键 /
`clash` 真重叠；`skip_original` 最严重，触发时后续回调整个不执行）。

**【怎么算过了】** 无 `PAIR-01`/`PAIR-04`（或已按处置方案化解），钩子共存档为 `safe` 或已人工确认。
**【下一步】** 全部通过 → 交接 **WF-4** 安装与冒烟跑通。
**【卡住了】** `PAIR-01/04` 或钩子 `clash` → WF-5 对应处置，或回 WF-1 第 3 步改补丁方式；
真实终端输出样例与三个非直觉细节见 `references/13-coexistence.md`。
**【出处】** `references/13-coexistence.md`；`references/07-tool-usage.md` §check --pair/§钩子共存三档

---

## 本流完成标准

一份 `check` 0 error、`verify` ADMITTED、已 `seal`、共存无硬冲突的 zip。
→ 交接 **WF-4** 做安装与冒烟跑通。
