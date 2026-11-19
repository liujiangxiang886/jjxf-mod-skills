# 12 · 自定义基线（改版）能力边界与验收

> 出处：交付包《01-引擎线与版本/自定义基线与改版 mod.md》（166 行，逐条对过代码）。
> **权威边界来源**，覆盖 WF-3。与 `08-version-maintainer.md` 冲突时以本篇为准（08 的"登记自定义线"写于插桩接入前）。

## 一、结论先行（逐条对过代码，非推断）

| 问题 | 权威答案 |
|---|---|
| 能用 `jjm_pack.py check/verify/seal --line <自定义线ID>` 吗 | **不能**。`--line` 的 choices 只有 4.6/4.7，写 `custom:…` 退出码 2 拒掉 |
| 有 `--custom` / `--baseline <path>` 吗 | **没有**，六子命令都没有 |
| 自定义线的包怎么验 | 现阶段**只能验结构**：`engine.line` 临时写 4.7、`baseline.id` 写 `jjxf.v4.7` 跑一遍；锚点与钩子**验不了** |
| `sources-<线>.zip` 路径对自定义线适用吗 | **不适用**。自定义线源码由创作者交付，登记在 `config/custom_baselines.json`，不叫 `sources-<线>.zip` |
| 现在能装扩展吗 | **不能**。装配层未开放：界面只有 4.6/4.7 两个入口，`install()` 逐字比对 `engine.line`。代码注释原话：`自定义改版没有扩展体系，走不到这里` |
| 插桩层接入了吗 | **没有**。`negotiate.py:316`：`基线已导入且校验有效，但插桩层生成器尚未接入自定义线；为避免静默失效，本次跳过` |

**一句话**：**不要给自定义线写"打包→安装→生效"的 SOP**，那条链路现在不存在。
现在能做的是：启动改版、存档隔离、验收基线；扩展装配是预留能力。

## 二、四个标识（别混）

| 标识 | 例子 | 用在哪 |
|---|---|---|
| 线 id | `custom:3f2a…` | 配置键、`cli --line`（仅 custom-baseline） |
| 文件名标签 | `custom_3f2a…` | 覆盖层 `overlay-custom_*.pck`（冒号在 Windows 文件名非法，由 `paths.line_tag()` 折叠） |
| 基线 id | `jjxf.v1.45`（固定） | 扩展清单 `baseline.id` |
| 引擎线 | `4.6` / `4.7` | 决定底座引擎与 pack 版本 |

`uuid` 由启动器登记时生成，**作者不要自己编**。

## 三、改版 mod 清单（开放后才生效）与当前报错

```jsonc
{ "schema":4, "id":"me.my_custom_mod", "version":"1.0.0",
  "baseline":{"id":"jjxf.v1.45","engine":{"line":"custom:3f2a…"}},
  "sources":{"name":"my_line_sources.zip","sha256":"<反解源码 sha256>","line":"custom:3f2a…"} }
```

**为什么 jjm_pack 必然报错**：`_resolve_line` 按 `baseline.id=jjxf.v1.45` 命中 4.6，
再比对 `engine.line` 必须是 4.6，而清单写 `custom:…` → `MAN-07`。
改 baseline.id 为 `custom:…` 则触发 `MAN-06`（不认识该基线）。**这是工具边界，不是 bug。**

**现阶段作者该做的**：①用标准线写法验结构（`--line 4.7`）；②`text_patches`/`method_hooks`
的锚点钩子当草稿，等拿到创作者验收过的 `sources/` 再重算；③**不要发布**声称"支持某改版"的包。

## 四、custom-baseline 验收（B0–B5）

交付物三件套：
```
<基线目录>/  baseline.json  # schema:1, identity_hash, engine_line, source_dir?, index?
            index.json     # files / symbols / anchors
            sources/       # 明文 .gd（UTF-8、非空、含 extends/func/var 特征）
```

```bash
"<启动器目录>/New state launcher.exe" cli custom-baseline verify <基线目录> --line custom:<ID>  # 不写登记
"<启动器目录>/New state launcher.exe" cli custom-baseline import <基线目录> --line custom:<ID>   # 过了才登记
"<启动器目录>/New state launcher.exe" cli custom-baseline status  --line custom:<ID>              # 查有效期
```
`--game` 可指定改版本体文件。界面路径：基线导入对话框。

| 项 | 判据 | 不过的原文（节选） |
|---|---|---|
| B0 元数据 | schema=1；identity_hash 与本体闸门一致；engine_line 一致 | `identity_hash 与改版本体不符（拿错源码/本体被换过）` |
| B1 源码 | sources/ 有明文 .gd，UTF-8、非空、命中 extends/class_name/func/signal/var/const | `缺少源码目录：…` |
| B2 索引一致 | files 都在 sources；symbols 每个方法找到 func/signal；anchors 每段原文能找到 | `符号 {脚本}:{方法} 在源码里找不到` |
| B3 本体对应 | `.gd↔.gdc` 在本体 pck 索引对上 **≥80%** | `只有 N% 的源码脚本能在本体里找到对应条目（需 >= 80%）` |
| B4 脚本覆盖 | `line.json` 里 `kind=method/hook` 的 `capabilities.target` 都交了源码 | `能力目标 {脚本} 没有交源码，无法插桩` |
| B5 联机禁入 | 源码正文命中联机协议（P2P/直连）一律拒绝 | `含联机协议（{原因}），不支持联机接入` |

**status 会自己失效**：本体指纹变了 / 源码目录没了 / 源码内容改过 → 都要重走 B0–B5。"验过一次"≠永久有效。

## 五、钩子被跳过的两段真实日志（排障用）

```
基线已导入且校验有效，但插桩层生成器尚未接入自定义线；为避免静默失效，本次跳过
```
```
含方法钩子，自定义线无正典源码、不生成插桩层；请按《自定义基线导入准则》导入反解源码
```
第一条=源码已验收只差生成器；第二条=还没交源码。汇总行：`能力协商：挂载 N 个、跳过 M 个（可用能力 K 项）`。
**被跳过不等于报错**：`ModDecision(ext_id, "skip", reason)`，扩展仍在列表，只是不参与挂载——别让玩家以为装坏了。

## 六、将来装配开放后的 go/no-go（不承诺时间）

六条全绿才发：①三件套交付且 verify 退 0；②import 后 status.ready=true；③`line.json` capabilities
覆盖扩展要用的方法/信号/资源；④**启动器版本说明明确写了"自定义线装配已开放"**（现在没有）；
⑤包无 `method_hooks` 或已接受被跳过；⑥发布说明写清适配哪个改版与源码摘要。
**第 4 条不过，前三条做得再对也不该发。**
