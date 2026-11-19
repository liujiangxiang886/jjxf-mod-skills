# 03 · 错误码速查全集

> 出处：对外知识库《错误码全集.md》（完整版）。按出现阶段分 5 节。
> 日志原文变量用 `{…}` 表示，可直接搜关键词。作者排障先确定阶段，再按码找触发条件。
> 需要完整日志原文时查知识库 04-常见问题FAQ/错误码全集.md。

**级别**：error=打包失败或安装/启动被拒；warn=提醒不阻断（但可能功能静默缺失）；剔除=启动器把包排除；提示=信息。

**排查顺序**：① 先看码的阶段 → ② 再看是不是被剔除（verify.*/conflict.*/gate.*/baseline.*，这类不是包坏了，是"与环境对不上"）→ ③ 最后才怀疑本体。同一条日志多个码，**先修级别最高的**。

---

## 一、打包检查（jjm_pack.py check / verify）

### 包与结构
| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| PKG-00 | error | 路径不存在 | 检查拼写 |
| PKG-01 | error | 根目录无 extension.json | 清单放根目录，别套一层文件夹 |
| PKG-02 | error | 清单非合法 UTF-8 JSON | 存无 BOM UTF-8 |
| PKG-03 | error | 顶层是数组/字符串 | 顶层必须是对象 {} |
| PKG-04 | error | 条目数 > 20,000 | 去掉无用文件 |
| PKG-05 | error | 单文件 > 512 MB | 拆分 |
| PKG-06 | error | 解压后 > 2 GB | 精简载荷，别带本体资源 |
| PACK-00/01/02/03 | error | 输入非目录 / 缺清单 / 自检有 error / 含符号链接 | 逐项修 |
| MANI-01/02 | error | 已有清单未加 --force / id 不合规 | 加 --force / 改 id |

### 清单字段（MAN）
| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| MAN-01 | error | 缺 schema/id/name/version | 补齐四必填 |
| MAN-02 | error | schema 不在 1/2/3/4 | 新包写 4 |
| MAN-03 | warn | 用了 schema 1/2 | 新包直接写 4 |
| MAN-04 | error | id 不合规 | 小写字母数字开头，仅 a-z0-9._-，2-64 位 |
| MAN-05 | error/warn | kind 不在枚举/没写 | extension/minigame/theme/framework |
| MAN-06 | error | baseline.id 不认识或不匹配 | 4.6 写 jjxf.v1.45；4.7 写 jjxf.v4.7 |
| MAN-07 | error | engine.line 与目标线不一致 | 改成目标线 |
| MAN-08~12 | error | files 数组/项/字段/files[i] target 越界/源文件不在包内 | 逐项修 |
| MAN-13~16 | error | patches/hooks 数组/项/缺 target/target 越界 | 逐项修 |
| MAN-17 | warn | 白名单外顶层字段 | 自定义字段用 x_ 前缀 |
| MAN-18 | error | op 不在白名单 | add/remove/replace/move/copy/test/merge/merge_patch/set |
| MAN-19 | error | path 不以 / 开头 | JSON Pointer 形如 /catalog/360261 |
| MAN-20 | error/warn | expect 键不支持 / sha256 非 64 位 | 只用 eq/ne/exists/type/sha256/size |
| MAN-21 | error | on_miss 取值不认识 | abort/warn/skip |
| MAN-22 | error | overrides 点名自己 | 写别人的 id |
| MAN-23 | error | 声明 overrides 没写 expect | 补断言 |
| MAN-24 | warn | 包内两条改动打同一处 | 合并或改深指针 |
| MAN-25 | warn | 接管别人但 requires 没写 | 补 requires |
| MAN-26 | error | text_patches 项没有 find | 补锚点 |

### 文本补丁（PATCH）
| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| PATCH-00 | warn | 本机无该线源码，锚点无法核对 | 放 sources-<线>.zip 或 --source |
| PATCH-01 | error(4.7)/warn(4.6) | 锚点命中数与 expect_count 不符 | 换行归一/加 scope/重写锚点 |
| PATCH-02 | error(4.7)/warn(4.6) | scope 写法错或函数不存在 | 写 function:函数名，核对源码 |
| PATCH-03 | warn | expect_count=0 且 0 命中按放行 | 改成真实条数，否则等于没写 |

### 源码声明（SRC）
| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| SRC-00 | warn | 有补丁/钩子但没 sources，schema≤3 | 补三字段（旧格式放行） |
| SRC-01 | error | 同上但 schema≥4 | 补 {"name","sha256","line"} |
| SRC-02 | error | sources.line 与包声明线不一致 | 改成目标线 |
| SRC-03 | error/warn | sources.sha256 缺失 | 用 manifest 自动生成 |
| SRC-04 | warn | 本机无 sources-<线>.zip | 放源码包 |
| SRC-05 | error | sha256 与随包源码不一致 | 填 zip **文件本身**的哈希 |
| SRC-06 | warn | sources.name 与本地名不同但内容一致 | 可忽略，建议对齐 |

### 钩子（HOOK，打包期）
| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| HOOK-00 | warn | 本机无该线源码 | 同 PATCH-00 |
| HOOK-01 | error(4.7)/warn(4.6) | 目标脚本不在源码/包内、没声明 requires | 补脚本/改目标/声明依赖 |
| HOOK-02 | error(4.7)/warn(4.6) | 脚本里找不到方法 | 按目标线源码改名 |
| HOOK-03 | warn | 目标不在源码但 requires 声明了 | 安装时先装依赖 |
| HOOK-04 | error(4.7)/warn(4.6) | 缺 target 或 method | 两个都写 |

### 自带基底 / 联机拦截 / 配对 / 准入 / 签封 / 修复
| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| SELF-01 | error | 补丁目标取不到原文 | jjm_pack.py fix <包> --source <反解工程> |
| SELF-02/03 | warn | 目标无扩展名 / 未随包提供按依赖处理 | 补后缀 / 先装依赖 |
| SELF-04 | 提示 | 目标由随包源码兜底 | 无需处理 |
| NET-00 | error | 清单自述携带联机能力 | 去掉声明与代码 |
| NET-01 | error | 命中联机实现（ENet/WebSocket/TCP/UDP/IP:端口） | 删除；本版本不支持 |
| NET-02 | warn | 命中可疑规则（@rpc 等） | 确认无对等端可保留 |
| PAIR-00 | error | 有包读不了/schema 不支持 | 先修包本身 |
| PAIR-01 | 提示 | 两包改同一处（静态判定） | 收窄锚点/接管/二选一 |
| PAIR-02 | warn | 一方显式接管另一方 | 安装顺序先装被接管方 |
| ADM-01 | warn | schema 1/2 | 新包写 4 |
| ADM-02 | error | 清单读不到/非 JSON 对象 | 修清单 |
| ADM-03/04 | warn | 钩子依赖升格 / 包内两改动同一处 | 实测插桩 / 合并 |
| ADM-05 | error | overrides 点名的包不在 requires | 补 requires |
| ADM-06 | error | 声明接管却缺 expect | 补断言 |
| ADM-07/08/09 | error | 位置重叠未处置 / 依赖未在 --with / 合集成员未通过 | 逐项修 |
| ADM-10 | warn | 没带 --with 组合准入没验 | 至少带两个包一起跑 |
| SEAL-00~04 | error | 路径不存在/读不到清单/无法确定线/找不到 identity/检查未通过 | 逐项修，seal 前先 check |
| FIX-00/01 | error | --source 非目录 / 缺清单 | 修参数/补清单 |
| FIX-02/04 | 提示 | 已自带基底/产物已生成 | 无需处理 |
| FIX-03 | warn | 反解工程找不到目标 | 若依赖提供则正常，否则补基底 |

---

## 二、安装期（启动器）

### install.*
| 码 | 触发条件 | 修法 |
|---|---|---|
| install.not_found | 找不到包文件 | 检查路径 |
| install.manifest | 清单缺失/格式不支持 | 用 1.7 工具重新导出 |
| install.baseline | 不是给当前版本做的 | 换对应版本本体或等作者适配 |
| install.verify | 验证记录与当前版本对不上 | 让作者按当前版本重新 seal |
| install.unpack / corrupt / pck | 解压失败/结构损坏/装后自校验不过 | 重新下载 |
| install.longpath | Windows 路径过长 | 启动器移到更浅目录 |
| install.netguard | 含联机实现 | 删除联机部分 |
| install.isolation | 与游戏其它部分干扰 | 检查是否改了不该改的文件 |
| install.overlay | 覆盖层生成失败/旧产物 | 用当前工具重打包 |
| install.smoke | 装上后游戏起不来（已自动撤销） | 停用该扩展，日志给作者 |
| install.register | 记录写入失败 | 检查磁盘/权限 |
| install.conflict | 未处置的位置冲突 | 卸掉其一或收窄锚点 |
| install.no_source | 取不到可用源码 | 装标准本体或指向反解工程 |
| install.incompatible | 不适配当前启动器 | 等作者出新版 |
| install.partial | 成功但有补丁未落地 | 看 failed_patches，修锚点 |
| install.unknown | 兜底 | 看日志详情与诊断包 |

### 清单静态校验（schema.unsupported / id.invalid / name.empty / version.format / field.unknown /
baseline.* / sources.* / files.* / entry.not_in_files / data.empty_target / op.unknown /
pointer.invalid / expect.bad_shape / override.bad_shape / hook.*）
关键码：
| 码 | 级别 | 触发条件 |
|---|---|---|
| sources.missing | error(schema4)/warn | 有补丁/钩子但没 sources 声明 |
| sources.line_mismatch | error | sources.line 与包声明线不符 |
| sources.sha_mismatch | error | sha256 与随包源码不符，锚点可能命中但改错位置 |
| sources.sha_unknown | warn | 本机取不到源码指纹 |
| hook.target_missing | error | 钩子目标脚本不存在 |
| hook.method_missing | error | 钩子目标方法不存在 |
| hook.incomplete | error | 钩子缺 target/method |
| hook.phase | error | phase 非 before/after |
| hook.res_prefix | warn | 目标写了 res:// 前缀，建议省略 |
| files.override_baseline | warn | 用 files 覆盖了基线资源，自动写自指 remap |
| files.need_remap | info | 覆盖脚本/场景类但缺 .remap |
| entry.not_in_files | warn | scripts.entry 指向的文件没在 files 里 |

合集：bundle.member（成员失败，看点名成员）/ bundle.warn（预检提醒）。

---

## 三、组合与冲突

| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| compose.anchor / base / files / patch / decision | warn | 叠加后锚点找不到/取不到原文/整文件副本冲突/补丁异常/决策点合并失败 | 看 reason，通常加 scope 或自带基底 |
| conflict.files | 剔除(严格档) | 目录与子文件提供范围重叠 | 改 files[].target |
| conflict.location | 剔除(严格档) | 两包改同一处且未处置 | 收窄/接管/二选一 |
| conflict.declared / claims / replace_hook | 剔除 | 声明互斥 / 抢同一能力 / 都要求替换同一钩子 | 卸掉其一或只留一个 |
| merge.decision / override | warn | 决策点冲突降级 / 覆盖关系生效 | 确认顺序符合预期 |
| patch.skipped | warn | 有补丁未应用 | 按该线源码重算锚点 |
| units.overlap | warn | 两包文件提供范围重叠 | 改 target |

---

## 四、启动与就绪

| 码 | 级别 | 触发条件 | 修法 |
|---|---|---|---|
| launch.baseline / runtime / conflict | error | 没找到版本/缺运行文件/扩展组合有冲突 | 指定游戏目录/重新解压/先处理冲突 |
| ext.disabled | 剔除 | 扩展被停用 | 扩展页启用 |
| ext.unknown | 剔除 | 状态异常 | 重装该扩展 |
| ext.check_failed | warn | 就绪检查未完成 | 看日志异常 |
| gate.dependency | 剔除 | 依赖的包被剔除连带剔除 | 先修被依赖方 |
| gate.dropped | 剔除 | 被准入闸门剔除（汇总） | 看同条日志具体码 |
| verify.absent | 剔除 | 没有验证记录 | 让作者 seal |
| verify.stale | 剔除 | 记录与代码层指纹不符 | 按当前版本重新 seal |
| verify.unavailable | 提示 | 该线还没代码层指纹 | 补 identity-<线>.json |
| baseline.mismatch / code_mismatch / size_mismatch | 剔除 | 本体与基线不符/代码层不符/pck 大小不符 | 换标准本体，基本就是本体不对 |
| overlay.missing | warn(跳过) | 覆盖层文件丢失 | 重装扩展 |
| hooks.method_missing | 剔除 | 钩子目标方法找不到 | 让作者改名 |
| hooks.script_missing | 剔除 | 钩子目标脚本找不到 | 让作者改目标 |
| hook.not_registered | warn | 声明插桩点但没回调注册上 | 检查 handler，功能大概率不生效 |
| anchor.miss | warn | 运行期补丁锚点未命中 | 让作者重算锚点 |
| anchor.unavailable | warn | 读不到原版内容（多半没导入本体） | 导入标准本体 |
| manifest.missing / schema / unknown_field | 剔除/warn | 覆盖层清单副本读不出/schema 不支持/未知字段 | 作者重打包 / 忽略 |
| members.incomplete / invalid_name | 剔除 | script_members 缺字段/成员名非法（会 Parse Error） | 让作者补齐/改名 |

> 完整日志原文见知识库《错误码全集.md》五个章节。
