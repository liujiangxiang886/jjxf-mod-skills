# 08 · 版本维护者手册（线的维护，不是写 MOD）

> 出处：对外知识库《06-经验沉淀/版本维护者手册.md》（156 行）。面向接手 4.6/4.7 线、
> 做新基线、换剧情层的人。MOD 作者看 `02-mod-toolchain.md`，本篇讲"线本身怎么维护"。

## 你会接手什么

| 对象 | 位置（`<启动器目录>` 为根） | 说明 |
|---|---|---|
| 本体与引擎 | `game/`、`runtime/`、`engines/` | 4.7 本体 = pck + exe；4.6 = 内嵌 pck 的 exe |
| 基线身份 | `baseline/identity-<线>.json` | 整包哈希 + 代码层逐文件哈希 |
| 随包源码 | `baseline/sources-<线>.zip` + `.json` | 补丁与钩子的"原文"来源 |
| 基线配置 | `config/launcher.json` | `baselines.<id>` 的路径/大小/条目数/指纹 |
| 扩展注册表 | `config/extensions.json` | 按线记录覆盖层、启用位、状态 |

**一句话记住**：一条线由**本体 pck + 引擎版本 + 代码层**共同定义，三者任一变化，
原身份与所有验证记录都应视为失效。

## 四条不变量（改之前必读）

1. **一条线一份源码包**。4.6 与 4.7 的 `.gd` 不通用，别用 4.7 源码核对 4.6 补丁。
2. `sources-<线>.json` 的 `sha256` 是 **zip 文件本身的哈希**，不是 pck 指纹。
3. **随包源码必须与本体逐字节一致**。改本体没换源码（或反之）→ 整条线扩展集体报 `SRC-05`。
4. **非标准本体的门不要撬**。指纹闸门拦下意味着"源码不再可信"，放宽等于让锚点盲打。

## 换剧情层（4.7）——最容易出事

剧情层是 4.7 的"第一原文"，排在 mod 之前：
`baseline → story → mod overlay × N → sources 兜底 → merged → instrumented`

1. 先备份旧剧情 `.pck`（命名带日期）；
2. 启动器「游戏库 → 4.7」把剧情覆盖层路径指向新文件；
3. 启动一次确认能进游戏；
4. **通知所有依赖剧情层的作者**：锚点按新源码重算、重新 `seal`；
5. 旧扩展不要直接留用。

> 为什么严重：剧情层里的同名脚本会**整体覆盖**随包源码，旧文本算的锚点一律对不上——这是必然，不是可能。

## 本体升级（官方发新 pck）

1. 新本体放 `game/`，记 `pck_size`、`entry_count`；
2. `freeze_baseline.py` 重建身份；
3. 更新 `config/launcher.json` 的 `baselines.<id>`（path/size/entry_count/pck_size/sha256）；
4. 更新随包源码；
5. **通知作者**：所有 `text_patches` 按新源码重算，旧验证记录全部 `stale`。

## 重建身份指纹

```bash
python tools/freeze_baseline.py --line 4.7 --body <本体>/jjxf47.pck --exe <本体>/jjxf47.exe
python tools/freeze_baseline.py --line 4.6 --body <本体>/mchGame.exe --kind exe   # 4.6 内嵌 pck
python tools/freeze_baseline.py --line 4.7 --body … --exe … --dry-run            # 先看会写什么
```

产物含 `layers`（整包 sha256）与 `code_layer`（逐文件 sha256 + 汇总 digest）。
**旧身份签发的所有 `verification.json` 会立刻失效——预期行为，不是 bug。**

## 更新随包源码（最容易出事的一步）

1. 从新本体反解脚本（GDRE / gdsdecomp），只取 `.gd`；
2. 打成 zip；
3. 算 **zip 文件本身**的 sha256 写进 `sources-<线>.json`；
4. 同步 `pck_size`/`entry_count`/`exe_sha256`；
5. 启动器实测：挑一个用 `text_patches` 的包跑 `check`，应 0 error；
6. **别只换 zip 不换 json，也别只改 json 不换 zip**——两边必须同时。

> 真实事故（2026-11-14）：只把 `texture_cache.gd` 换成改过的 64 MiB 版本、没同步改本体 pck，
> 4.7 合集 21 个扩展**全部**被判源码不符；恢复 zip 后 21/21 通过。

## 登记自定义线

1. 准备改版本体 + 反解源码；2. 启动器登记拿 `identity_hash`；
3. 改版本体同目录放 `line.json`（schema 1，含 name/version/publisher/network=false、
   identity{identity_hash, engine_line, baseline}、source_index、capabilities）；
4. 分档：`launch-only`（没过闸门，只能启动）→ `probe-only`（过闸门但无合格 line.json，启动+只读探测，**不挂扩展**）→ `full`（line.json 通过，可协商挂扩展）。

**当前版本**：自定义线的插桩层生成器**尚未接入**。即使到 `full`，依赖 `method_hooks` 的扩展也会被**明确跳过**（非静默失败）；纯资源/数据覆盖类扩展可用。

## 发布前检查清单

- [ ] `identity-<线>.json` 与当前本体一致（`freeze_baseline.py --dry-run` 比对）
- [ ] `sources-<线>.zip` 与本体逐字节一致，`sources-<线>.json` 的 `sha256` 是 zip 哈希
- [ ] 抽 3 个存量包 `check --line <线>` 0 error
- [ ] 抽一个合集 `verify --with` 结论 ADMITTED
- [ ] 启动器能进游戏、扩展页状态正常（待插桩 → 已就绪）
- [ ] 换过剧情层的，已通知受影响作者并给新源码版本号

## 常见事故速查

| 现象 | 根因 | 处置 |
|---|---|---|
| 全线 `SRC-05` | 源码 zip 与本体不一致 / json sha256 写错 | 恢复匹配源码包；sha256 改回 zip 哈希 |
| 4.6 包在 4.7「命中 0 处」 | 用 4.7 反解工程核对 4.6 源码 | 按线匹配 `source_root`，读 `project.godot` 的 `features` 首项 |
| 换剧情层后黑屏 | 旧补丁打在错误位置 | 先停用该线扩展再换层；让作者按新源码重算 |
| 新本体装完全 `stale` | 代码层变了，旧验证失效 | 预期行为；让作者重新 `seal` |
| 自定义线不挂扩展 | 分档是 `probe-only` | 补合格 `line.json`；注意插桩层仍未接入 |

## 常用命令

```bash
python tools/freeze_baseline.py --line 4.7 --body <pck> --exe <exe>        # 重建身份
python tools/jjm_pack.py check <包>.zip --line 4.7                        # 抽查存量包
python tools/jjm_pack.py verify <包>.zip --with <依赖>.zip --line 4.7     # 组合准入
python tools/merge_story_into_baseline.py --help                          # 合剧情（仅合并包时）
```
