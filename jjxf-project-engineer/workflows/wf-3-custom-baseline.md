# WF-3 · 自定义基线（改版）与改版 MOD

> 目标：用户改了本体 / 用自定义版本时，说清"现在到底能做什么、不能做什么、基线怎么验"。
> 出处：`references/12-custom-baseline.md`（源自交付包《自定义基线与改版 mod.md》，逐条对过代码）。
>
> ⚠️ **本流硬约束（进去前必须讲，不可省略，否则给用户假预期）**：
> 1. **`jjm_pack.py` 的 `--line` 只认 `4.6` / `4.7`**（argparse `choices` 限死）。
>    写 `custom:…` 会以**退出码 2** 被拒，业务逻辑根本不执行。**没有** `--custom` / `--baseline <path>` 参数。
>    所以"用 jjm_pack 给自定义线打包验证"这条链路**不存在**。
> 2. **自定义线现在装不了扩展**：装配层未开放——界面只有 4.6/4.7 两个导入入口，
>    `cli ext --install --line custom:…` 被拒。代码注释原话：`自定义改版没有扩展体系，走不到这里`。
>    手工把 `overlay-custom_*.pck` 铺进去属**未支持、未验证**路径，不要建议。
> 3. **插桩层生成器尚未接入自定义线**：`negotiate.py` 原文
>    `基线已导入且校验有效，但插桩层生成器尚未接入自定义线；为避免静默失效，本次跳过`。
>    被跳过的扩展仍在列表里（`ModDecision skip`），不是装坏了。
>
> **一句话**：自定义线现在只能做三件事——**启动改版、存档隔离、验收基线**；
> 扩展装配是预留能力。不要给自定义线写"打包→安装→生效"的 SOP。

---

## 第 1 步 · 先纠正用户的预期

**【目标】** 让用户明白当前边界，避免按标准线流程白忙一场。

**【你要做的】** 明确告诉他三条硬约束（见上），并给出**现在能做的三件事**：

| 能做 | 不能做 |
|---|---|
| 启动改版本体、存档隔离 | 用 jjm_pack 校验自定义线（工具不认） |
| 用 `cli custom-baseline` 验收/登记基线 | 装扩展（装配层未开放） |
| 先按标准线验结构、把内容当草稿 | 声称"支持某改版"的包发出去（玩家装上只会得到"不在此线"或"插桩被跳过"） |

**【怎么算过了】** 用户理解了"现在验基线、不验扩展装配"，并说明自己的真实目标。
**【下一步】** 第 2 步，验收基线。
**【卡住了】** 用户坚持要"给自定义线做能装的 MOD" → 如实说明当前能力边界，
不承诺、不臆测开放时间；可按 LEARNING.md 记为一条"能力需求"。
**【出处】** `references/12-custom-baseline.md` §一

---

## 第 2 步 · 验收自定义基线（B0–B5）

**【目标】** 把创作者交付的反解源码验过六项判据，拿到有效期内的基线登记。

**【你要做的】** 确认交付物三件套：
```
<基线目录>/  baseline.json（schema:1, identity_hash, engine_line, source_dir?）
            index.json（files / symbols / anchors）
            sources/   （明文 .gd，UTF-8、非空、含 extends/func/var 等特征）
```

六项判据（出处：`12-custom-baseline.md` §4.3）：
- **B0 元数据**：`baseline.json` schema=1；`identity_hash` 与本体闸门一致；`engine_line` 一致。
- **B1 源码**：`sources/` 有明文 `.gd`，UTF-8、非空、命中 `extends/class_name/func/signal/var/const`。
- **B2 索引一致**：`index.json` 的 files 都在 sources；symbols 每个方法能找到 `func/signal`；anchors 每段原文能找到。
- **B3 本体对应**：`.gd ↔ .gdc` 能在本体 pck 索引对上，比例 **≥ 80%**。
- **B4 脚本覆盖**：`line.json` 里 `kind=method/hook` 的 `capabilities.target` 都交了源码。
- **B5 联机禁入**：源码正文命中联机协议（P2P/直连）一律拒绝。

**验收命令**（出处：`12-custom-baseline.md` §4.2）：
```bash
"<启动器目录>/New state launcher.exe" cli custom-baseline verify <基线目录> --line custom:<ID>
"<启动器目录>/New state launcher.exe" cli custom-baseline import <基线目录> --line custom:<ID>   # 过了才登记
"<启动器目录>/New state launcher.exe" cli custom-baseline status  --line custom:<ID>              # 随时查有效期
```

**【怎么算过了】** `verify` 退出码 0；`import` 成功；`status` 返回 `ready: true`。
**【下一步】** 第 3 步，把 mod 内容按"只验结构"处理。
**【卡住了】** 按失败判据定位（B0 拿错源码/本体被换、B1 缺源码、B2 符号或锚点找不到、
B3 本体对应 <80%、B4 能力目标没交源码、B5 含联机协议）。
**注意 status 会自己失效**：本体指纹变了、源码目录没了、源码内容改过 → 都要重走 B0–B5。
**【出处】** `references/12-custom-baseline.md` §四

---

## 第 3 步 · 改版 MOD 内容：只验结构，锚点/钩子当草稿

**【目标】** 让用户在当前能力下把内容准备到"开放即可用"的程度，不发布假预期包。

**【你要做的】** 告诉用户现阶段唯一可行的做法（出处：`12-custom-baseline.md` §三）：
1. 清单按**标准线写法**验结构：`--line 4.7`，`baseline.id` 写 `jjxf.v4.7`，
   把 `engine.line` **临时**写成 `4.7` 跑一遍 `check` / `verify`，确认结构与字段合规。
2. `text_patches` / `method_hooks` 的**锚点和钩子当草稿**——本机没有这条线的源码，验不了；
   等拿到创作者验收过的 `sources/` 再逐条重算。
3. **不要发布**声称"支持某改版"的包。玩家装上只会"不在此线"或"插桩被跳过"。

> 为什么 jjm_pack 必然报错：`--line` 只认 4.6/4.7；且自定义线清单的 `baseline.id=jjxf.v1.45`
> 与 `engine.line=custom:…` 必然触发 `MAN-07`（或改 baseline.id 触发 `MAN-06`）。
> 这是**工具边界**，不是 bug。

**【怎么算过了】** 用户有一份"结构已按标准线验通、锚点/钩子标注为草稿、未对外发布"的内容。
**【下一步】** 停在"草稿待开放"状态；若只是要启动改版+存档隔离，转 WF-4 的启动部分（不涉及扩展装配）。
**【卡住了】** 看到 `MAN-06/07` 或退出码 2 → 这是预期内的边界，不是要修的 error；
解释给用户，不要试图绕过（撬门等于让锚点盲打）。
**【出处】** `references/12-custom-baseline.md` §三；`references/03-error-codes.md`

---

## 附：将来装配层开放后会变成怎样（前瞻，不承诺时间）

- 清单写法：`baseline.id=jjxf.v1.45`，`engine.line=custom:<ID>`，`sources.line=custom:<ID>`。
- go/no-go 六条全绿才发：创作者交付三件套且 `verify` 退 0、`import` 后 `status.ready=true`、
  `line.json` 的 capabilities 覆盖扩展要用的方法/信号/资源、
  **启动器版本说明明确写了"自定义线装配已开放"**（现在没有）、
  包无 `method_hooks` 或已接受被跳过、发布说明写清适配哪个改版与源码摘要。
- **第 4 条不过，前三条做得再对也不该发**（出处：`12-custom-baseline.md` §六）。

## 本流完成标准

自定义基线已通过 B0–B5 并登记有效；用户明确知道扩展装配当前未开放；
改版 MOD 内容处于"结构验通的草稿"状态、未对外发布。
