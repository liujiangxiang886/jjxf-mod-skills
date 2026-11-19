# 02 · MOD 开发最小工具链

> 出处：内部完整版 §5.2 最小工具链、§5.4 启动器对作者的支持、§7.3 常用命令。

## 一句话结论

**普通扩展作者不需要 Godot 编辑器、不需要反解、不需要编译引擎**——只要标准本体 + Python 3.9+ +
`jjm_pack.py` 就能做出一个可发布的数据补丁包。

## 工具清单（三档）

| 类别 | 清单 | 说明 |
|---|---|---|
| **必需** | 该线标准本体 | 4.7 必须 380,259 条目那份；非标准会被指纹拦 |
| | Python 3.9+ | jjm_pack.py 单文件、只用标准库，无需 pip 装任何东西 |
| | `tools/jjm_pack.py` | check / verify / pack / manifest / seal / fix + check --pair |
| | 该线 `baseline/sources-<line>.zip` | 算 sources.sha256 用；发布版启动器自带 |
| **可选** | 反解工程（GDRE / gdsdecomp） | 想读原版 .gd/.gdc 时用；普通作者**不需要** |
| | Godot 4.6 / 4.7.2 编辑器 | 只有自己做 .tscn/.tres/自定义脚本时才需要 |
| | dump_pck.py / patch_fix.py 等 | 排障与批量改造脚本，在 扩展开发文档/tools/ |
| **无需** | 编译引擎、C#/.NET、管理员权限 | 全程不碰引擎源码，不写注册表 |
| | 把原版脚本打进包 | 启动器自动用随包源码兜底，作者只需**声明**用哪份 |
| | 改启动器源码 | 扩展是数据 + 覆盖层，不改 exe |

## 最小可用产物

```
me.my_ext-1.0.0.zip
├─ extension.json          ← 必须在根目录，schema 4
└─ payload/
    └─ data/items.json     ← 你自己的文件
```

清单至少写 `schema` / `id` / `name` / `version`；用了 `text_patches` 或 `method_hooks`
就**必须**写 `sources` 三字段（name / sha256 / line），其中 sha256 与随包源码不一致、
或 line 与 engine.line 不一致，都是拒装。

## jjm_pack.py 常用命令

```bash
python tools/jjm_pack.py check   "4.7 mod.zip"              # 基础检查
python tools/jjm_pack.py verify  "4.7 mod.zip"              # strict 准入，发之前必跑
python tools/jjm_pack.py pack    ./my_mod -o my_mod.zip     # 打包
python tools/jjm_pack.py manifest ./my_mod --line 4.7       # 自动生成 sources.sha256
python tools/jjm_pack.py seal    ./my_mod                   # 写 verification.json
python tools/jjm_pack.py check A.zip --pair B.zip           # 两包冲突判定
```

## 从 check 到生效：四道关卡

作者最常见的误解是"`check` 全过了就能装"。实际要过四关：

1. `check` — 基础检查
2. `seal` — 写 `verification.json`（没签封 → `verify.absent`，会被剔除）
3. 安装闸门 — schema / 位置冲突（`conflict.location`）
4. 挂载冒烟 — 启动一次游戏验证真的装上（`install.smoke`）

## 安装与状态

- 装合集用 `cli ext --install`（合包用这个）；`cli mods install` 是逐文件直装，喂合包会报
  "扩展包的信息不完整"。
- 状态机：`needs_hooks`（待插桩）→ `ready`（已就绪）。插桩发生在启动时，进游戏稳定 5 秒才翻。
  一直不翻才看日志里哪些脚本没 apply。
- 导入期间启动按钮置灰——运行中的进程握着 `overlay-*.pck` 句柄，此时改写不生效。

## 签封（seal）要点

- 需该线的代码层指纹 `identity-<线>.json`，找不到报 `SEAL-03`。
- `seal` 前必须先 `check` 通过，否则 `SEAL-04` 拒绝写记录。
- `verification.json` 与当前代码层指纹不符 → `verify.stale`，让作者按当前版本重新 seal。
