# 09 · 资源与剪藏清单（该剪什么，不是链接大全）

> 出处：对外知识库《05-资源与剪藏/剪藏清单.md》（82 行）。注意：这是**给负责网页剪藏的人的入口清单**，
> 只给"章节名 + 稳定入口"，不含剪藏结果（深链换版本会 404）。作者问"某知识点官方怎么查"时用本篇指路。

## 原则
只剪**官方与原始来源**，不剪转载、不剪破解/联机内容。每条记「版本 + 抓取日期」。
标题格式 `[官方] 章节名 · 版本 · YYYY-MM-DD`；正文首行留原始 URL 纯文本（防链接失效找不到来源）。

## Godot 官方文档（每条线各剪一份）
入口 `https://docs.godotengine.org/`（左上角版本选择器切 4.6 / 4.7）。

| 优先级 | 章节 | 为什么剪 | 检索关键词 |
|---|---|---|---|
| P0 | Exporting projects | pck 怎么生成、导出预设、`--export-pack` | `export pck`, `export presets` |
| P0 | Command line tutorial | `--main-pack`/`--path`/`--headless`/用户目录 | `command line`, `main-pack` |
| P0 | Project settings | `application/config/features`、`run/max_fps`、`rendering/rendering_device/driver` | `project settings`, `features` |
| P1 | Feature tags | 为何用 `config/features` 判断引擎线 | `feature tags` |
| P1 | File paths（`res://`/`user://`） | 存档与用户目录在哪 | `user://`, `res://` |
| P1 | GDScript reference（选读 `@rpc`、类继承） | 读扩展脚本、判断钩子目标 | `GDScript`, `class_name` |
| P2 | Exporting for Windows | 模板 exe 与 pck 配对 | `export windows`, `template` |
| P2 | PCK encryption（若有） | "目录区加密时无法列举条目" | `pck encryption` |

要求：每篇保留页面标题/版本/抓取日期三行元信息；4.6 与 4.7 各存一份带版本后缀；别只存正文丢代码块。

## PCK 格式
官方**没有**单独"PCK 格式"文档页，权威来源是引擎源码：
- `core/io/file_access_pack.cpp`、`core/io/pck_packer.cpp`：头部字段顺序（magic/pack_version/偏移/目录区）
- `core/io/file_access_pack.h`：目录项结构、加密标志位
- 社区文章（搜 `Godot PCK format`/`GDPC`）只作对照，**以源码为准**

本项目 `app/core/pck/format.py` 已把常量写成注释；内部排障可对照，对外文档不贴源码只讲结论。

## GDRE 工具（反解）
仓库 `https://github.com/GDRETools/gdsdecomp`；剪 README + Releases（版本号与支持范围）+ 命令行用法。
只剪"怎么用"，不剪游戏资源；反解产物不进知识库。

## 版本信息
- Godot 发布说明 `https://godotengine.org/releases/`：4.6/4.7 release notes、破坏性变更
- Godot 博客 `https://godotengine.org/blog/`：pck/导出/渲染后端相关公告

理由：4.7 的 pack v4 与 4.6 的 v3 不兼容，版本说明是"为什么 v3 引擎读不了 v4 包"的公开依据。

## 不要剪
转载的 Godot 镜像（版本滞后）/ 破解·联机·私服教程 / 论坛"改 pck 变简单"帖 / 带游戏资源下载的页面（版权风险）。

## 剪完入库
归到 `05-资源与剪藏/` 下「官方文档 / PCK / 工具 / 版本」四个子目录；回填一句
"对应《4.6线与4.7线》第 X 节"方便交叉引用。
建议顺序：Exporting projects（各一份）→ Command line（各一份）→ Project settings/Feature tags（合并）→ PCK 源码两文件（注明 commit）→ GDRE README+Releases → 4.6/4.7 release notes。
