# LEARNING.md · 让专家持续学习

> 这份文档回答一个问题：**新 MOD 类型在出现、新手在问新问题、项目在变，这个工程师怎么跟着变聪明？**
> 核心原则：**稳定知识不轻易动，新经验走条目，定期回流升级。**
> 适用范围是**双层**的：通用 MOD 开发经验（角色/武器/动画/其它游戏工具链）与
> 机甲旋风项目经验都收。每条经验用 frontmatter 的 `layer` 字段标注「通用」或「项目」。

## 三条学习通道

### 通道 A：作者直接反馈（最快）

任何新作者的问题、新踩的坑，按 `templates/experience-entry.md` 写成一条，
放进 `experiences/`。下次加载 Skill 时专家自动能用上。

步骤：
1. 复制 `templates/experience-entry.md` → `experiences/<日期>-<主题>.md`
2. 填 frontmatter（date / title / source / **layer** / category / lines / severity / supersedes）
   - `layer`：通用层经验填「通用」，机甲旋风项目经验填「项目」
   - `lines`：项目层填 4.6 / 4.7；通用层填「通用」或具体游戏名
3. 按"现象 → 结论 → 依据 → 修法 → 防范措施 → 关联"六段填写
4. 在 `experiences/README.md` 的"已有条目"加一行链接

### 通道 B：从知识库回流（批量）

项目的对外知识库（WorkBuddy 资料库「机甲旋风 MOD 作者知识库」）持续沉淀文档。
当知识库新增/更新内容时，定期回流进这个 Skill：

1. 对照知识库目录（00 入门 / 01 引擎线 / 02 MOD开发 / 03 启动器工具 / 04 FAQ / 06 经验沉淀）
2. 找出相对 Skill 现有 references 的**新增或变化**部分
3. 局部新经验 → 写成 experiences 条目（通道 A）
4. 大块结构性更新 → 更新对应 references 文件，并在本文件"变更记录"登记
5. 若涉及口径变化（版本号/条目数/渲染后端）→ 同时更新 `references/00-project-profile.md`
   和 `SKILL.md` 的"口径统一"节

建议节奏：每积累 5-10 条经验，或知识库有明显更新时，做一次回流。

### 通道 C：知识升级（推翻旧结论）

当新经验证明旧结论错了（如新增 4.8 线，或某错误码语义变了）：

1. 新经验写成 experiences 条目，`supersedes` 字段填被推翻的出处（如 `references/01-engine-lines.md §双线对照表`）
2. 修改对应的 references 文件，在改动处标注 `[更新于 YYYY-MM-DD：原因]`
3. 若影响"口径统一"或"检索路由"，同步改 `SKILL.md`
4. 在下方"变更记录"登记这次升级
5. 重新打包专家（见"发布流程"）

## 发布流程（让所有作者用上新知识）

Skill 内容变化后，专家包需要重新打包分发：

```bash
# 1. 校验（在专家包根目录的上级调用）
python3 <expert-manager>/scripts/validate_expert.py <专家目录>

# 2. 重新注册（修改了任何字段都必须重跑）
python3 <expert-manager>/scripts/register_expert.py <专家目录>

# 3. 打包分享
python3 <expert-manager>/scripts/package_expert.py <专家目录>

# 4. 重新校验真实存档 mtime（若期间跑过游戏测试）
```

## 质量门槛（写经验条目时的自检）

- [ ] 结论先行，一句话能说清
- [ ] 有出处（文件章节 / 日志 / 命令输出 / 日期）
- [ ] 有可复核的数字或原文（不是"感觉变快了"）
- [ ] 有防范措施（不只说怎么修，还说怎么防复发）
- [ ] 标了涉及哪条线（4.6 / 4.7 / 通用）
- [ ] 若推翻旧结论，填了 `supersedes`

## 变更记录

| 日期 | 变更 | 来源 | 影响文件 |
|---|---|---|---|
| 2026-11-17 | 初建：从内部完整版(1012行)+错误码全集+7份对外文档提炼核心知识 | 旧智能体回传资料 | SKILL.md + references/00-06 |
| 2026-11-17 | 第二批回流（通道 B）：三处口径正式裁决+V1.5 定案；补工具细则/版本维护者手册/剪藏清单/hello_world 样例包（SHA 已核） | 旧智能体第二批交付包 | 新增 references/07-09 + examples/ + SKILL.md 路由 + experiences 第一条 |
| 2026-11-17 | 升级为教学+端到端工作流：新增 5 条 SOP（workflows/），Agent MD 双路径，plugin.json 定位改写 | 用户更正需求 | workflows/6 文件 + SKILL.md + Agent MD + plugin.json |
| 2026-11-17 | **知识升级（通道 C）**：权威命令手册推翻 6 处 SOP 推断——`--line` 只认4.6/4.7、自定义线装配未开放、ADM-01 别降 schema、四关补 verify/compat、overrides 方向性、seal 目录/zip 两域。新增 5 份权威 reference + 完整样例 | 对方《本轮补充对照表》《命令权威手册》等（逐条实跑） | 新增 references/11-15 + examples/me.guide_demo-1.0.0.zip；重写 WF-2/3/4；SKILL.md/WORKFLOWS.md 路由；experiences 第 2 条（supersedes）|
