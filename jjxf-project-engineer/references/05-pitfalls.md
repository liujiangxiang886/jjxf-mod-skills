# 05 · 踩坑记录与工程经验

> 出处：内部完整版 §二（Godot 侧坑 1-5）、§三（启动器侧坑 1-7）、§2.4 性能优化、§2.1-2.3 底座架构。

## A. Godot 侧踩坑

1. **业务参数放 `--` 前面会被引擎吃掉**。Godot 自己解析 argv，`--` 之前的未识别参数会被丢弃；
   底座用 `OS.get_cmdline_user_args()` 只拿得到 `--` 之后。所有业务参数统一放 `--` 之后：
   `jjxf47.exe --headless --main-pack jjxf47.pck -- --packset=... --main=... --log=... --smoke`
2. **内嵌在 exe 尾部的 pck 必须给 offset**。1.45 pck 接在 exe 尾部，不传 offset 从文件头读签名对不上。
   实测起点 104,599,040。packset 条目支持 `offset` 字段。
3. **Autoload 顺序是命门**。Compat 必须排 `[autoload]` 第一位，挂载写在 `_init()`（比 `_ready` 更早）——
   游戏自己的 Autoload 脚本就在被挂载的包里，顺序错了主场景报 `res://scripts/game.gd 不存在`。
4. **给 4.6 挂 4.7 分片报 `Pack version unsupported: 4`**，和"文件坏了"极像。pack 版本是格式版本，
   不是游戏版本；启动前 `check_packset_versions()` 逐片比对，直接给中文结论。
5. **底座 pck 少装 3 个脚本功能静默失效**。host47.pck 曾只有 7 条目，缺 frame_probe/audio_guard/mem_slim。
   补全为 10 条目 / 91,282 B；build_base.py 改"整目录 _compat 全装"，不手写文件名清单。

## B. 启动器侧踩坑

1. **导入 mod 期间还能启动游戏**。三层闸口：① 入队前确认框；② `_sync_launch_button()` 判
   `_install_active` → 按钮置灰；③ `_launch()` 开头再拦一道。反方向也堵：running 实例拒绝导入。
2. **4.6 线所有 mod 报"锚点 0 命中"**。`basecontent.source_root()` 无条件优先读
   `sources.reversed_project`（指向 4.7）。改：先看本线 `runtime_sources`，退回时用 project.godot 的
   config/features 校验归属。效果 27/27。源码来源做成 5 级回落链。
3. **sources-4.7.zip 与 pck 内容不一致，21 扩展全失效**。zip 被换成改过 texture_cache 的版本，
   而 pck 仍是旧版；json 的 sha256 字段语义是"随包 zip 文件本身的哈希"。从 .bak 恢复 + 改回字段。
   发布脚本增加"字段==实际文件哈希"断言。
4. **配置写坏后双击没反应（窗口化 exe 最凶）**。config.load 遇坏 JSON 直接 raise，上游无 try，
   windowed exe 的 sys.stderr 是 None，连打印都做不到。改：坏文件改名留档 → 返回默认配置 → WARNING；
   app/fatal.py 装 Qt 消息处理器接管建窗口期异常。
5. **测试把真实数据写坏了**。service.install 等直接读写运行期目录。conftest._isolate_runtime_dirs
   做 autouse，把 BUILDS/PACKS/CACHE/REGISTRY 指到 tmp_path；死角是 import 时就算好的路径常量，
   改成调用时取。验收五条：用例数、退出码、stderr 无 fatal、config 哈希不变、du 不增长。
6. **测试全绿但退出码 3221225477（0xC0000005）**。deleteLater 只是排队删除，控件活到解释器退出，
   shiboken 析构 C++ 对象 access violation。统一走 qt_cleanup.dispose()：close → setParent(None) →
   deleteLater → 手动派发 DeferredDelete。
7. **宿主 safe-delete 钩子打崩测试**。sitecustomize 给 rmtree/os.remove 套壳，累计删 50 次 raise
   SystemExit（不是 Exception，ignore_errors 也兜不住）。conftest 从 nt/posix 取原生实现还原 os，
   reload(shutil)，修 sys.modules 里的旧引用。

## C. 性能与工程决策（实测后改的）

- **贴图缓存 384MiB/4096 → 64MiB/1024**，删掉诊断代码。"选完角色卡死"的最大单一原因。
- **限帧 + 垂直同步**：底座原版两项都没有，现默认 max_fps=60 + vsync=0，可调。
- **无头冒烟**：`--smoke` 只实例化主场景即退出（quit_after_frames=600, min_nodes=3），单次≈21.5s。
- **官方导出走不通**：4.7 是 template 构建没带导出功能，自建 pck 写包器（data_align=4096，
  shard_limit≈1.8GiB，写完回读校验）。
- **不写系统目录**：onedir + 相对路径，配置/存档/日志全在程序目录内；不要求管理员、不写注册表。
- **版本烧入**：JJXF_EDITION 只允许 unified/player/dev/publisher，非白名单 SystemExit。

## D. 关键数字（可复核）

- 全量测试 790 passed, 1 skipped / 88.6s；发布包 283 条 / 521.5MB 解压 / 229.51MB 压缩
- 4.7 合集导入 7.5min → 62.1s（组合冒烟替代逐包冒烟，21/21 成功）
- 就绪判定 3261ms → 487ms；扩展发现 4.6 773→33ms、4.7 1997→41ms
