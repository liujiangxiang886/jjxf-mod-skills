# verification · 落库后可检索验证清单

导入不是终点——必须验证新经验**真的能进入专家的检索与回答**。commit 后逐项执行。

## 一、文件层验证

```bash
# 1. 条目文件存在且非空
ls -la <target-experiences>/<date>-<主题>.md

# 2. frontmatter 合法（date/title/source/layer/category/lines/severity 齐全）
head -15 <target-experiences>/<date>-<主题>.md

# 3. README 索引已登记
grep -n "已有条目" -A 10 <target-experiences>/README.md
```

全部应命中；导入器 `--report` 的 `written` 列表应与实际文件一一对应。

## 二、检索路由验证（关键）

`jjxf-project-engineer/SKILL.md` 的检索路由表本就含这一行：

> 真实案例、新作者贡献的经验、最近踩的新坑 → `experiences/` 目录（按日期倒序）

因此新条目**无需改主 Skill 路由**即可进入检索范围。验证：

1. 确认该路由行仍在（未被误删）。
2. 从用户视角模拟提问：用新经验里的关键词问专家，检查回答是否引用了该条目
   （出处应形如 `experiences/<日期>-<主题>.md`）。
3. 若回答没引用，检查：条目标题是否含该关键词、`layer`/`lines` 是否与问题匹配、
   README 链接是否正确。

## 三、内容质量复核

- [ ] 六段正文齐全（现象/结论/依据/修法/防范/关联），无"（待补充）"残留（或已知会补）
- [ ] 关键数字/日志原文与来源一致
- [ ] 脱敏彻底（无本机路径、账号、真实存档名、凭据）
- [ ] C 级资料标注了"待版本作者确认"

## 四、冲突/升级验证（若 supersedes 非空）

- [ ] references 对应章节已更新并标注更新痕迹
- [ ] 口径三处一致（00-project-profile / SKILL.md 口径统一 / 新条目）
- [ ] LEARNING.md 变更记录已登记
- [ ] 专家包已重新打包并递增 version

## 五、回归验证（不破坏旧知识）

- [ ] 既有 experiences 条目未被误改（除 README 追加外）
- [ ] 导入器脚本可重复运行且不产生重复条目（幂等性：再跑一次 dry-run，conflicts 应列出刚导入的条目）
- [ ] 主 Skill 结构完整（validate_expert.py 通过）

## 验证报告模板

```
导入批次：<intake_id>
导入条目：<N> 条，成功 <M>，跳过 <K>（重复）
文件验证：✅ 索引登记：✅ 检索路由：✅ 内容质量：✅/⚠ 回归：✅
可检索确认：以「<关键词>」提问，专家引用 experiences/<文件> → ✅/❌
结论：可投入使用 / 需补料后重新导入
```
