# 15 · 各类 MOD 最小做法 + 钩子正反例 + 新手十问

> 出处：交付包《02-MOD开发/各类MOD最小做法.md》（188 行）、《钩子写法与坑.md》（234 行）、
> 《04-常见问题FAQ/新手十问标准答法.md》（150 行）。源自现网 28 个已装扩展的真实清单统计 + 代码判据。
> 用途：用户说"我想做某类内容"时，**先定机制再动手**——选错机制是新手最贵的一次返工。

## 一、一张表定机制（改数据用 data，改文字/逻辑用 text，换文件用 files，加行为用 hooks）

| 你要做的东西 | 用什么 | 需要源码 | 现网代表（改动方式 files/data/text/hooks） |
|---|---|---|---|
| 改数值、改描述、加道具/装备/掉落 | `data_patches` | 否 | `qt6663.exp_equipment`（0/2/0/0） |
| 改界面文案、改显示逻辑 | `text_patches` | **是** | `qt6663.exp_dungeon_difficulty`（0/0/2/0） |
| 换贴图/立绘/模型/图标 | `files`（+导入产物） | 否 | `jjxf.dark_weapon.black`（562/0/0/0） |
| 加按钮/面板/交互流程 | `method_hooks`+`files` | **是** | `mch.ai_teammate`（11/0/0/12） |
| 综合大型内容 | 四样一起 | 是 | `mch.treasure_dup`（360/1/5/6） |

**口诀**：改"数据"用 data，改"文字/逻辑"用 text，换"文件"用 files，加"行为"用 hooks。
四样都不需要、只想整包替换资源 → 覆盖层直铺。

### 1. 数值/道具/掉落（data_patches）
找对 JSON 与 Pointer，`op: replace/add`。真实 Pointer：
- 改装备属性 `data/equipment.json` → `/catalog/300001/attributes`
- 加新装备 同文件 `/catalog/396001`（整对象 add）
- 加图标/外观 同文件 `/catalog/301037/visual_key` + `/icon_path`
- 加掉落池 `data/dungeon_loot.json` → `/pools/legendary_20`、`/profiles/boss`
- 改道具描述 `data/items.json` → `/100000/description`

写完先 `cli compat <包> --line 4.7` 看"补丁 N/N"是否全命中（现网 `exp_equipment` 有 5,130 条 replace）。
**坑**：`add` 到已存在的 key 会失败——加新条目用 add，改已有用 replace。

### 2. 文案/显示逻辑（text_patches）
一条 `find`+`replace`，`expect_count:1`，改 `.gd` 必须声明 `sources`。四条铁律（顺序不能换）：
①`find` 唯一（不唯一加 `scope:"function:函数名"`）；②缩进逐字符照抄（Tab 别写空格）；
③find 与 replace 一起改；④按**目标线**源码算锚点，4.6 锚点别搬 4.7。
改 `hud.gd` 这类多扩展争抢脚本先 `check --pair`（见 `13-coexistence.md`）。

### 3. 图片/立绘/模型（files + 导入产物）——最容易漏
**只放一张 `.png` 不生效**！pck 里是导入后产物，运行期不重新导入。新增一张图是**三件套**：
```
mods/<id>/assets/xxx.png
mods/<id>/assets/xxx.png.import
.godot/imported/xxx.png-<hash>.ctex
```
三件套必须同一次导出生成（Godot 编辑器导入一次），手写 path 与 ctex 名对不上就是"图裂"。
4.7 本体 pck 里 **188,424 个 `.ctex`、只有 1 个 `.png`**——改图只能改 `.ctex`，
先 `cli dump <pck> --search <关键字>` 确认目标存在。整包铺 overlay 体积大、易互盖，不建议。

### 4. 新增玩法/UI（method_hooks + files）
`extends Node` 入口脚本，`install(api)` 里注册钩子。三个硬约束：
①`phase` 只能用 `before`/`after`（写 `replace` **不报错但永不触发**）；
②`after` 改返回值必须写回 `ctx["result"]`（`return` 新值无效）；
③目标方法必须真实存在（`HOOK-02` 拦）。

### 5. 剧情内容
走**剧情覆盖层** `story.pck`，不进 `packs/<id>/`：
声明 `line:"4.7"`（别把 4.6 剧情挂 4.7）；覆盖 `.gd` 必须**保留同名 `.remap`**（否则本体 `.gdc` 盖住你的）；
只放改过的脚本/场景/数据；**换层即失效**，发布说明写清适配哪个剧情版本。

### 6. 音效
**现网无样例**，4.7 Demo 本体 0 个音频条目。只能给通则：先 `cli dump --search audio/` 确认条目名；
替换用 `files` 覆盖同名；新增走导入管线带产物；**发布前必须真启动听一次**——音频失败不会让冒烟失败。

### 7. 地图/场景
`.tscn` 属 `NEEDS_BASE_SUFFIXES`。改已有场景 `files` 覆盖同名 `.tscn`+自指 `.remap`；
加新场景 `files` 放 `.tscn`+资源三件套；加地图入口通常还要 `data_patches` 改地图配置 JSON。
参考 `rose.dimension_ruins`（14 files/0 data/1 text/9 hooks）。

### 三类永远不要放进包
①本体完整资源（体积爆炸、互盖）；②别的扩展的文件（跨包引用走 `requires`+`peer_access`，
直接拷被隔离扫描记 `violations`）；③联机协议代码（`netguard` 命中即拒装）。

## 二、钩子契约与正反例

回调收到一个 Dictionary，键：
| 键 | before | after | 说明 |
|---|---|---|---|
| `result` | 无 | ✅ | 原方法返回值，**改这个键才算改结果** |
| `args` | ✅ | ✅ | 形参快照 |
| `arguments` | ✅ | ✅ | 位置参数数组，改了回写成形参 |
| `instance` | ✅ | ✅ | 宿主节点 self |
| `skip_original` | ✅可写 | —— | 置 true 跳过原逻辑 |

after 返回 `ctx.get("result", 原值)` → **必须写回 `ctx["result"]`**。
`before` 适合改入参/拦截/前置校验；`after` 适合改返回值/加后缀/补副作用（void 方法也行）。

**正确写法（读—改—写，可叠加）**：
```gdscript
func _on_display_text(ctx: Dictionary) -> void:
    var original: Variant = ctx.get("result", "")
    if typeof(original) != TYPE_STRING: return
    var parts: PackedStringArray = str(original).split(":")
    if parts.size() != 2: return
    ctx["result"] = "%d 小时 %d 分" % [int(parts[0]), int(parts[1])]   # 右值用到当前值 = RMW
```
判定器看**右值有没有用到当前值**（`hook_keys.rmw_keys`）。

**三个反例**：
1. **整份替换** `ctx["result"]="0 小时 0 分"`（右值不看当前值）→ 静态判 `clash`（`整份替换了 result…`），
   运行期吃掉前面扩展的累加。只有独占 result 才可行，但静态仍报 clash。
2. **`return` 新值** → 无效，插桩读的是 ctx 不是 return 值。
3. **`before` 跳值类型** / `phase=replace` → 不触发或跳值失败。

**六个坑**（详见交付原文）：`skip_original` 吞掉同点后续回调；`phase=replace` 不报错但永不触发；
`after` 不写回 ctx 改动丢失；目标脚本换线不存在；整份替换判 clash；多包同点要 `check --pair`+`ext-audit`。

## 三、新手十问标准答法（索引）

交付包《新手十问标准答法.md》给了 10 条可直接复制的答复 + 对应错误码，覆盖：
跨线安装、check 过但被剔除、锚点 0 命中、sources.sha256 填什么、待插桩是不是失败、
两包冲突、剧情更新失效、我这儿能装别人装不上、自定义改版能不能挂 mod、导入时能不能启动。
**答法入口**：`04-author-faq.md`（8 问 + 10 现象）、`03-error-codes.md`（错误码）、
`14-success-signals.md`（怎么算过了）。工具命令形式以 `11-command-reference.md` 为准。
