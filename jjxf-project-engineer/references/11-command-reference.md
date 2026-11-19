# 11 · 命令权威手册（jjm_pack 与启动器 CLI）

> 出处：交付包《03-启动器与工具/命令权威手册.md》（204 行，逐条实跑核对）。
> 这份是**唯一正确调用形式**的权威来源，冲突时以本篇为准（覆盖 02/07 的泛化写法）。
> 版本：`jjm_pack 1.6` / 规范 `1.7` / 发布版 **V1.5**。

## 两个入口，别混

| 入口 | 谁用 | 完整形式 | 依赖 |
|---|---|---|---|
| 作者工具 | MOD 作者 | `python jjm_pack.py <子命令> …` | 只需 Python 3.9+，不 import 启动器代码 |
| 启动器内核 CLI | 作者/维护者/排障 | `<启动器目录>/New state launcher.exe cli <子命令> …` | 需启动器本体 + 已配置本体路径 |

CLI 源码形式 `python -m app.main cli …`。
**冻结版坑**：exe `console=False`，stdout 不可用时输出重定向到 `logs/cli-<时间>.log`。
想看输出：`"New state launcher.exe" cli mods list > mods.txt 2>&1`，或看 `logs/` 里 `cli-` 文件。

## 一、jjm_pack 六子命令 × 输入形态

**结论：`check`/`verify`/`seal` 三者都同时接受目录与 zip，没有"必须先 pack"限制。**

| 子命令 | 目录 | zip | 产物 | 备注 |
|---|---|---|---|---|
| `check` | ✅ | ✅ | 无（只出报告） | 目录 check 更快 |
| `verify` | ✅ | ✅ | 无 | 可喂合集包 |
| `seal` | ✅ 写 `<目录>/verification.json` | ✅ 生成 `<原名>.sealed.zip`（不动原 zip） | 两种指纹域不同 |
| `pack` | ✅ 仅目录 | ❌ | `.zip` | 参数是 folder |
| `manifest` | ✅ 仅目录 | ❌ | 改/建 extension.json | `--id` 必填 |
| `fix` | ✅ 包 | ✅ 包 | `-o` 指定新 zip | `--source` 与 `-o` 都必填 |

### 推荐路线（目录开发 → 目录签封 → 目录打包）

```bash
python jjm_pack.py check  ./my_mod --line 4.7     # 开发期随时检查，目录即可
python jjm_pack.py verify ./my_mod --line 4.7     # 发布前准入
python jjm_pack.py seal   ./my_mod --line 4.7     # 对目录签封，写 verification.json
python jjm_pack.py pack   ./my_mod -o my_mod-1.0.0.zip
```

已发过 zip 只想补签封：`python jjm_pack.py seal my_mod-1.0.0.zip --line 4.7`
→ 生成 `.sealed.zip`，原 zip 不变。

### seal 两种指纹域（最容易踩）

| 对谁 seal | 产物 | `content_scope` | 装完还能否判"内容被改过" |
|---|---|---|---|
| **目录** | `<目录>/verification.json` | `dir` | **能**（推荐） |
| zip | `<原名>.sealed.zip` | `package` | **不能**——装完只比代码层，改了包内容也显示"已验证" |

判定端 `app/core/ext/verify_mark.py:358`：`comparable = source == "local" or content_scope == "dir"`。
**所以 seal 统一做在目录上，再 pack。**

### 退出码与 --line 限制

退出码：`0` 无 error（可能 warn）/ `1` 有 error / `2` 参数或子命令不认识。
`seal` 多一个条件：检查通过（或 `--force`）**且**记录写成功才 0。
**`--line` 是 `choices` 限死的 `4.6`/`4.7`**（`LINE_PROFILES`）。写 `custom:…` 直接退出码 2，业务逻辑不执行。

## 二、启动器 CLI 完整语法

**形式：`<启动器目录>/New state launcher.exe cli <子命令> [参数]`**

### 扩展相关（作者最常用）

| 用途 | 完整命令 | 界面可替代 |
|---|---|---|
| 静态检查（含钩子对源码）| `cli ext <包.zip> --check-hooks -v` | ❌ |
| **安装**（单包/合集）| `cli ext <包.zip> --install --line 4.7` | ✅ 扩展页「安装扩展…」 |
| 安装+冒烟 | `cli ext <包.zip> --install --verify --line 4.7` | ✅ 完全校验档默认冒烟 |
| 允许部分补丁 | `cli ext <包.zip> --install --line 4.7 --allow-partial` | ✅ 宽松档 |
| 逐文件直装（旧法）| `cli mods install <包.zip> --line 4.7`（喂合集报"信息不完整"）| ✅ 界面走 ext --install |
| 列出已装 | `cli mods list` | ✅ |
| 启用/停用 | `cli mods disable/enable <id> --line 4.7` | ✅ |
| 重扫覆盖层 | `cli mods rescan` | ✅ |
| **真实本体命中预检** | `cli compat <包.zip> --line 4.7`（不安装，按真实 pck 试算补丁命中数）| ❌ **无（最该补的界面入口）** |
| 共存体检 | `cli ext-audit 4.7`（只扫已装扩展）| ✅ |
| 加载顺序 | `cli lock 4.7 [--write]` | ✅ |

compat 实跑输出：
```
[OK  ] me.guide_demo  v1.0.0  补丁 2/2  覆盖 0 命中 / 1 新增
合计：兼容 1，部分兼容 0，不兼容 0，待查 0
```
`补丁 2/2` = 1 条 text_patches + 1 条 data_patches 都在真实本体命中。**比"装完看效果"可靠得多。**

### 启动与冒烟
- `cli smoke 4.7`（headless，默认主场景 `res://scenes/start_page.tscn`）
- `cli smoke 4.7 --with-mods`（组合级）
- `cli run 4.7 --with-mods`（带窗口，排障用）
- 全局选项写在子命令**之前**：`cli --ext-mode strict smoke 4.7`

### 基线与诊断
- `cli verify <基线 zip 或 pck>`（校验身份）
- `cli drift 4.7 [--samples 24]`（源码/字节码漂移）
- `cli stat`（环境体检）、`cli dump <pck> --search scripts/ --limit 50`（只读）
- `cli custom-baseline verify/import/status --line custom:<ID>`（**唯一认 custom 线的子命令**）

### 两条限制
1. `ext`/`lock`/`ext-audit`/`compat`/`drift`/`smoke`/`run` 的 `--line` 只有 4.6/4.7；自定义线只有 `custom-baseline` 认。
2. **`compat` 没有 GUI**，发包前都该跑一遍。

## 三、界面能替代的动作（给新手）

导入扩展 `cli ext <包> --install --line <线>` / 启停 `enable/disable` / 卸载 `uninstall_line` /
体检 `cli ext-audit` / 启动 `cli run <线> --with-mods` / 自定义基线导入对话框（`custom-baseline import`）。
**无界面**：`cli compat`（补丁命中预检）。

## 四、五个高频误用

1. `check` 前非要 `pack` —— 不需要，目录直接 check。
2. seal 了 zip 又去 pack —— zip 已封好，再 pack 只换名。
3. `mods install` 喂合集 —— 报"信息不完整"，合集用 `ext --install`。
4. 只看退出码 —— `PAIR-01/04/ADM-01` 都是 warn，退出码仍 0，要读报告行。
5. 为消 `ADM-01` 把 schema 改回 3 —— **别做**。schema 4 才强制 `sources`，降回 3 丢掉"锚点按哪份源码算"。误报忽略即可。
