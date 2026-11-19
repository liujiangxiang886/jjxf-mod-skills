# 机甲旋风单机版 MOD 开发师 · 配套技能

这是 WorkBuddy 专家「机甲旋风单机版MOD开发师」（花名：戈启明）配套的两个技能的**源目录**。

以《机甲旋风》新起点兼容启动器的 Godot 引擎为唯一基准，提供 MOD 开发教学、打包验证、安装冒烟、排障，以及后续开发经验的规范化导入。

> 本项目为同人非商业作品，与《机甲旋风》原权利人无关。使用前请阅读 [DISCLAIMER.md](./DISCLAIMER.md)。

## 两个技能

| 技能 | 作用 |
|---|---|
| `jjxf-project-engineer` | 主技能：双层知识库（通用 Godot MOD 基础 + 本项目驻场事实）+ 5 条端到端工作流。覆盖新内容教学、4.6/4.7 与自定义基线打包验证、安装冒烟、排障。 |
| `mod-experience-ingest` | 经验导入：把他人的 MOD 开发经验资料（文档/案例/笔记）规范化提炼、校验、去重后导入知识库，默认只读、需显式确认才落库。 |

## 目录结构

```
jjxf-mod-skills/
├── README.md                   本文件
├── DISCLAIMER.md               版权与免责声明
├── jjxf-project-engineer/
│   ├── SKILL.md                技能入口：定位、检索路由、防回环预算
│   ├── LEARNING.md             经验沉淀与学习通道
│   ├── references/             静态知识（16 份，项目事实/工具链/错误码/FAQ…）
│   ├── workflows/              5 条端到端工作流 + 总览
│   ├── experiences/            增量经验条目（含索引 README.md）
│   └── templates/              经验条目模板
└── mod-experience-ingest/
    ├── SKILL.md                技能入口
    ├── references/             导入清单约定、规范化规则、验证方法
    ├── scripts/
    │   └── ingest_experience.py  导入器（Python 标准库，默认 dry-run）
    └── templates/              经验条目 / 导入清单模板
```

## 在 WorkBuddy 中使用

这两个技能随专家包 `godot-game-launcher` 一起分发，安装专家后自动可用。若需单独导入：

1. 把某个技能目录（如 `jjxf-project-engineer/`）打包为 zip（zip 内第一层即该目录本身）。
2. 在 WorkBuddy 的技能包发布入口上传该 zip。
3. 技能包 zip 内路径层级不超过两级；`SKILL.md` 需含 7 个 frontmatter 字段：`name` / `version` / `display_name` / `display_name_en` / `description` / `description_zh` / `description_en`。

## 关于样例包

主技能文档中引用的 `examples/me.hello_world-1.0.0.zip` 与 `examples/me.guide_demo-1.0.0.zip` 是 MOD 最小可运行样例包（二进制 zip）。**本仓库未附带这两个样例包**——GitHub 仓库只放文本文件源。文档正文中已内联展示其目录结构与 `extension.json` 写法，照着建即可；如获取到样例包，解压看结构最快。

## 版本

- `jjxf-project-engineer`：`1.0.1`
- `mod-experience-ingest`：`1.0.0`
- 配套专家包 `godot-game-launcher`：`1.0.5`
