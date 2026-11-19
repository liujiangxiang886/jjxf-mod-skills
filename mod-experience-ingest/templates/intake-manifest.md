# intake-manifest 样例（JSON）

把他人的经验资料提炼成下面这份 JSON，交给 `scripts/ingest_experience.py`。
字段含义见 `references/intake-schema.md`。删除注释后保存为 .json（JSON 不支持注释）。

```json
{
  "intake_id": "2026-11-19-community-mod-tips",
  "intake_date": "2026-11-19",
  "contributor": "某社区作者（已脱敏）",
  "source_type": "note",
  "items": [
    {
      "date": "2026-11-19",
      "title": "4.7 线文案补丁锚点因 CRLF 不一致导致 0 命中",
      "source": "来源：社区作者踩坑笔记（已脱敏），2026-11 整理",
      "layer": "项目",
      "category": "新坑",
      "lines": ["4.7"],
      "severity": "warn",
      "supersedes": "",
      "phenomenon": "text_patches 的锚点在本体上 0 命中，报错只说未命中、不说是换行符问题。",
      "conclusion": "锚点文本与本体脚本换行符（CRLF/LF）不一致会导致 0 命中，先统一换行再重算锚点。",
      "evidence": "- 出处：社区笔记 §文案补丁\n- 关键数字：统一换行后命中从 0 变为全部命中\n- 可信度：C经验判断，待版本作者确认",
      "fix": "1. 用编辑器把补丁锚点与本体脚本统一为同一种换行符\n2. 重新计算锚点后再 check",
      "prevention": "交付前用脚本统一仓库换行符（.gitattributes 设 text=auto），避免跨平台混入 CRLF。",
      "related": "- 相关稳定知识：references/04-author-faq.md 避坑 4\n- 相关错误码：anchor.miss，见 references/03-error-codes.md"
    },
    {
      "date": "2026-11-19",
      "title": "Godot AnimatedSprite2D 逐帧动画的 FPS 与有效帧对齐",
      "source": "来源：通用 Godot 教程整理（已脱敏）",
      "layer": "通用",
      "category": "新工具用法",
      "lines": ["通用"],
      "severity": "info",
      "supersedes": "",
      "phenomenon": "导入序列帧后动画播放卡顿、攻击动作收尾不齐。",
      "conclusion": "AnimatedSprite2D 配 SpriteFrames 时需按帧设置 FPS，并把攻击/受击等一次性动画与循环动画分开。",
      "evidence": "- 出处：Godot 官方 AnimatedSprite2D 文档机制\n- 可信度：B权威文档",
      "fix": "1. 在 SpriteFrames 资源里按序列设置每帧时长\n2. 攻击动画关闭循环，待机动画开启循环",
      "prevention": "建帧时先定 FPS 与帧尺寸，按动作类型分组，避免攻击帧混入循环组。",
      "related": "- 相关稳定知识：references/10-general-mod-dev.md §动画帧搭配"
    }
  ]
}
```

生成空白模板（命令行）：

```bash
python3 scripts/ingest_experience.py --emit-template
```
