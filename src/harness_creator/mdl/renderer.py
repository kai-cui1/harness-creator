"""MDL 渲染器。

将结构化 MDLDocument 对象渲染为 .mdl.md 格式文本。
使用 Jinja2 模板确保输出格式一致、可读。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml
from jinja2 import Template

from .models import (
    MDLDocument,
    ChecklistLevel,
    ImplementationStatus,
)


class MDLRenderer:
    """MDL 渲染器 — 将结构化对象渲染为 .mdl.md 文本"""

    def render(self, doc: MDLDocument) -> str:
        """渲染完整的 MDL 文档字符串"""
        parts = []

        # L1: YAML Frontmatter
        parts.append(self._render_frontmatter(doc))
        parts.append("")

        # 标题和来源信息
        parts.append(f"# {doc.meta.name}")
        parts.append("")
        parts.append(f"> **来源**：{doc.meta.source.product or doc.meta.source.file or '未知'}")
        parts.append(f"> **MDL 版本**：{doc.meta.mdl}")
        parts.append("")
        parts.append("---")
        parts.append("")

        # L2: 设计原则
        if doc.principle:
            parts.append(self._render_principle_layer(doc))
            parts.append("---")
            parts.append("")

        # L3: 组件规格
        if doc.component_spec:
            parts.append(self._render_component_spec(doc))
            parts.append("")
            parts.append("---")
            parts.append("")

        # 实例表
        if doc.instance_table:
            parts.append(self._render_instance_table(doc))
            parts.append("")

        # 设计理由
        if doc.rationale_entries:
            parts.append(self._render_rationale(doc))
            parts.append("")

        # L4: 实例层
        if doc.instance_layer:
            parts.append(self._render_instance_layer(doc))

        return "\n".join(parts)

    def render_to_file(self, doc: MDLDocument, filepath: Path) -> None:
        """渲染并写入文件"""
        content = self.render(doc)
        filepath.write_text(content, encoding="utf-8")

    # ------------------------------------------------------------------
    # L1 Frontmatter
    # ------------------------------------------------------------------

    def _render_frontmatter(self, doc: MDLDocument) -> str:
        """渲染 YAML Frontmatter"""
        meta = doc.meta
        data = {
            "mdl": meta.mdl,
            "name": meta.name,
            "version": meta.version,
            "author": meta.author,
        }

        if meta.date:
            data["date"] = meta.date

        # source（只包含非 None 字段）
        src = {}
        if meta.source.file:
            src["file"] = meta.source.file
        if meta.source.product:
            src["product"] = meta.source.product
        if src:
            data["source"] = src

        # platform（只包含非 None 字段）
        plat = {}
        if meta.platform.os:
            plat["os"] = meta.platform.os
        if meta.platform.screen:
            plat["screen"] = meta.platform.screen
        if meta.platform.screen_axure:
            plat["screen_axure"] = meta.platform.screen_axure
        if meta.platform.device:
            plat["device"] = meta.platform.device
        if plat:
            data["platform"] = plat

        data["target_agent"] = meta.target_agent
        data["status"] = meta.status.value
        data["category"] = meta.category.value

        if meta.references:
            data["references"] = [
                {"name": r.name, "relation": r.relation}
                for r in meta.references
            ]

        return "---\n" + yaml.dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1000,
        ) + "---"

    # ------------------------------------------------------------------
    # L2 原则层
    # ------------------------------------------------------------------

    def _render_principle_layer(self, doc: MDLDocument) -> str:
        """渲染 L2 原则层"""
        lines = ["## 设计原则（L2 Principle Layer）", ""]
        p = doc.principle

        if p.principles and len(p.principles) == 3:
            # 特殊处理：三大设计策略表格格式
            lines.append("### 核心设计策略")
            lines.append("")
            lines.append(
                "| 策略 | 定义 | 在具体组件中的体现 |"
            )
            lines.append("|------|------|-------------------|")
            for principle in p.principles:
                definition = principle.definition.replace("|", "\\|")
                manifestation = (
                    principle.manifestation.replace("|", "\\|")
                    if principle.manifestation
                    else ""
                )
                lines.append(
                    f"| **{principle.name}** | {definition} | {manifestation} |"
                )
            lines.append("")

        if p.scope:
            lines.append("### 适用范围")
            lines.append("")
            for s in p.scope:
                lines.append(f"- {s}")
            lines.append("")

        if p.behavior_assumptions:
            lines.append("### 行为假设")
            lines.append("")
            for a in p.behavior_assumptions:
                lines.append(f"- {a}")
            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # L3 组件规格
    # ------------------------------------------------------------------

    def _render_component_spec(self, doc: MDLDocument) -> str:
        """渲染 L3 组件规格"""
        spec = doc.component_spec
        lines = [
            f"## 组件规格：{spec.name}（L3 Specification Layer）",
            "",
        ]

        # 基本信息
        lines.append("### 基本信息")
        lines.append("")
        lines.append("| 属性 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| 组件名 | {spec.name} |")
        if spec.type:
            lines.append(f"| 类型 | {spec.type} |")
        if spec.parent_container:
            lines.append(f"| 父容器 | {spec.parent_container} |")
        if spec.size_variants:
            sizes = ", ".join(spec.size_variants)
            lines.append(f"| 尺寸变体 | `{sizes}` |")
        lines.append("")

        # 结构化约束 (YAML block)
        lines.append("### 结构化约束")
        lines.append("")
        lines.append("```yaml")
        lines.append(self._render_component_yaml(spec))
        lines.append("```")
        lines.append("")

        # 实例表（如果有的话，在 instance_table 部分单独渲染）
        # 这里不重复渲染

        # 设计理由汇总
        if doc.rationale_entries:
            lines.append("### 设计理由汇总（Rationale）")
            lines.append("")
            lines.append("| 元素 | 设计故事 | 用户价值 |")
            lines.append("|------|---------|---------|")
            for r in doc.rationale_entries:
                story = r.design_story.replace("|", "\\|")
                value = r.user_value.replace("|", "\\|")
                lines.append(f"| **{r.element}** | {story} | {value} |")
            lines.append("")

        return "\n".join(lines)

    def _render_component_yaml(self, spec) -> str:
        """将 ComponentSpec 渲染为 YAML 格式字符串"""
        data: dict = {
            "name": spec.name,
        }
        if spec.type:
            data["type"] = spec.type
        if spec.parent_container:
            data["parent_container"] = spec.parent_container

        if spec.variants:
            data["variants"] = [
                self._variant_to_dict(v) for v in spec.variants
            ]
        if spec.fixed_fields:
            data["fixed_fields"] = [
                self._field_to_dict(f) for f in spec.fixed_fields
            ]
        if spec.optional_fields:
            data["optional_fields"] = [
                self._field_to_dict(f) for f in spec.optional_fields
            ]
        if spec.constraints:
            data["constraints"] = [
                {**{"rule": c.rule, "rationale": c.rationale},
                 **({"status": c.status} if c.status else {})}
                for c in spec.constraints
            ]
        if spec.layout_rules:
            lr = spec.layout_rules
            layout_data: dict = {}
            if lr.row_1:
                layout_data["row_1"] = lr.row_1
            if lr.row_2_plus:
                layout_data["row_2_plus"] = lr.row_2_plus
            if lr.total_small_tiles is not None:
                layout_data["total_small_tiles"] = lr.total_small_tiles
            if layout_data:
                data["layout_rules"] = layout_data

        return yaml.dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            indent=2,
        )

    def _variant_to_dict(self, v) -> dict:
        d: dict = {"name": v.name}
        if v.description:
            d["description"] = v.description
        if v.aspect_ratio:
            d["aspect_ratio"] = v.aspect_ratio
        if v.contains_fixed:
            d["contains_fixed"] = v.contains_fixed
        if v.contains_optional:
            d["contains_optional"] = v.contains_optional
        return d

    def _field_to_dict(self, f) -> dict:
        d: dict = {
            "field": f.field,
            "type": f.type,
            "required": f.required,
        }
        if f.description:
            d["description"] = f.description
        if f.max_length is not None:
            d["max_length"] = f.max_length
        if f.visual_spec:
            vs = f.visual_spec
            vs_dict: dict = {}
            if vs.color:
                vs_dict["color"] = vs.color
            if vs.size:
                vs_dict["size"] = vs.size
            if vs.position:
                vs_dict["position"] = vs.position
            if vs.font_size:
                vs_dict["font_size"] = vs.font_size
            if vs.alignment:
                vs_dict["alignment"] = vs.alignment
            if vs_dict:
                d["visual_spec"] = vs_dict
        if f.rationale:
            d["rationale"] = f.rationale
        if f.implementation_status:
            d["implementation_status"] = f.implementation_status.value
        if f.examples:
            d["examples"] = f.examples
        if f.note:
            d["note"] = f.note
        return d

    # ------------------------------------------------------------------
    # 实例表
    # ------------------------------------------------------------------

    def _render_instance_table(self, doc: MDLDocument) -> str:
        """渲染实例配置表"""
        lines = [
            "### 各功能磁贴规格表",
            "",
            "| 功能 | 尺寸 | 背景 | APP 名称 | APP Logo | 动态信息 |",
            "|------|------|------|----------|----------|---------|",
        ]
        for row in doc.instance_table:
            bg = row.background.replace("|", "\\|")
            dyn = row.dynamic_info or "×（无）"
            lines.append(
                f"| {row.function_name} | `{row.size}` | {bg} | "
                f"{'√' if row.has_app_name else ''} | "
                f"{'√' if row.has_app_logo else ''} | {dyn} |"
            )
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 设计理由
    # ------------------------------------------------------------------

    def _render_rationale(self, doc: MDLDocument) -> str:
        """渲染设计理由"""
        lines = [
            "### 设计理由汇总（Rationale）",
            "",
            "| 元素 | 设计故事 | 用户价值 |",
            "|------|---------|---------|",
        ]
        for r in doc.rationale_entries:
            story = r.design_story.replace("|", "\\|")
            value = r.user_value.replace("|", "\\|")
            lines.append(f"| **{r.element}** | {story} | {value} |")
        lines.append("")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # L4 实例层
    # ------------------------------------------------------------------

    def _render_instance_layer(self, doc: MDLDocument) -> str:
        """渲染 L4 实例层"""
        layer = doc.instance_layer
        if not layer:
            return ""

        lines = [f"## 实例标注说明（L4 Instance Layer）", ""]

        # 特殊规则
        if layer.special_rules:
            lines.append("### 各功能的特殊说明")
            lines.append("")
            lines.append("| 编号 | 功能 | 特殊规则 |")
            lines.append("|------|------|---------|")
            for sr in layer.special_rules:
                desc = sr.special_description.replace("|", "\\|")
                func = sr.function_name or ""
                lines.append(f"| {sr.id} | {func} | {desc} |")
            lines.append("")

        # 待定项
        if layer.pending_items:
            lines.append("### 待定项清单")
            lines.append("")
            lines.append("| 标记 | 内容 | 影响范围 | 建议 |")
            lines.append("|------|------|---------|------|")
            for pi in layer.pending_items:
                marker = pi.marker.replace("|", "\\|")
                content = pi.content.replace("|", "\\|")
                impact = pi.impact_scope.replace("|", "\\|")
                suggest = pi.suggestion.replace("|", "\\|")
                lines.append(
                    f"| {marker} | {content} | {impact} | {suggest} |"
                )
            lines.append("")

        # 变更记录
        if layer.change_records:
            lines.append("### 变更记录")
            lines.append("")
            lines.append(
                "| 序号 | 时间 | 需求名 | 修订内容 | 提出人 |"
            )
            lines.append(
                "|------|------|--------|---------|--------|"
            )
            for cr in layer.change_records:
                content = cr.change_content.replace("|", "\\|")
                lines.append(
                    f"| {cr.seq} | {cr.time} | {cr.requirement_name} | {content} | {cr.author} |"
                )
            lines.append("")

        # 检查清单
        if layer.checklist_items:
            lines.append("## 审查检查清单（供 Agent 使用）")
            lines.append("")
            current_level: Optional[ChecklistLevel] = None
            for item in layer.checklist_items:
                if item.level != current_level:
                    current_level = item.level
                    level_names = {
                        ChecklistLevel.MUST: "必须满足（Must）",
                        ChecklistLevel.SHOULD: "应该满足（Should）",
                        ChecklistLevel.MUST_NOT: "不应该做（Must Not）",
                    }
                    lines.append(
                        f"### {level_names.get(current_level, '')}"
                    )
                    lines.append("")
                text = item.item.replace("[", "\\[").replace("]", "\\]")
                lines.append(f"- [ ] {text}")
            lines.append("")

        return "\n".join(lines).rstrip()
