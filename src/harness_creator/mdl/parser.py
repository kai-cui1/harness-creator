"""MDL 文件解析器。

将 .mdl.md 文件解析为结构化的 MDLDocument 对象。
支持：
- YAML Frontmatter 解析（L1 元层）
- Markdown 体内 YAML 代码块提取（L3 组件规格等）
- Markdown 表格提取（半结构化数据）
- 自然语言段落保留
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

import yaml
from frontmatter import loads as fm_loads

from .models import (
    MDLDocument,
    MetaLayer,
    PrincipleLayer,
    DesignPrinciple,
    ComponentSpec,
    ComponentVariant,
    ComponentField,
    ExclusionConstraint,
    LayoutRule,
    VisualSpec,
    InstanceTableRow,
    RationaleEntry,
    InstanceLayer,
    SpecialRule,
    PendingItem,
    ChangeRecord,
    ChecklistItem,
    ChecklistLevel,
    ImplementationStatus,
    HarnessStatus,
    HarnessCategory,
)


class MDLParseError(Exception):
    """MDL 解析错误"""


class MDLParser:
    """MDL .mdl.md 文件解析器"""

    def parse_file(self, filepath: Path) -> MDLDocument:
        """解析 .mdl.md 文件，返回结构化 MDLDocument 对象"""
        if not filepath.exists():
            raise MDLParseError(f"文件不存在: {filepath}")

        content = filepath.read_text(encoding="utf-8")
        return self.parse_string(content, source_path=filepath)

    def parse_string(self, content: str, source_path: Optional[Path] = None) -> MDLDocument:
        """从字符串内容解析 MDL 文档"""
        # Step 1: 分离 Frontmatter 和 Body
        meta, body = self._parse_frontmatter(content)

        # Step 2: 保留原始 body（用于 round-trip）
        doc = MDLDocument(meta=meta, raw_body=body)

        # Step 3: 从 Body 中提取各层内容
        self._extract_principle_layer(doc, body)
        self._extract_component_spec(doc, body)
        self._extract_instance_table(doc, body)
        self._extract_rationale_entries(doc, body)
        self._extract_instance_layer(doc, body)

        return doc

    # ------------------------------------------------------------------
    # Frontmatter 解析
    # ------------------------------------------------------------------

    def _parse_frontmatter(self, content: str) -> tuple[MetaLayer, str]:
        """分离并解析 YAML Frontmatter，返回 (MetaLayer, body_markdown)"""
        post = fm_loads(content)
        fm_data = post.metadata or {}
        body = post.content or ""

        if not fm_data.get("name"):
            raise MDLParseError("Frontmatter 缺少必填字段: name")

        # 构造 MetaLayer — 只提取已知字段，忽略未知字段
        meta_dict = {
            "name": fm_data.get("name", ""),
            "version": fm_data.get("version", "0.1.0"),
            "author": fm_data.get("author", ""),
            "date": fm_data.get("date"),
            "status": HarnessStatus(fm_data.get("status", "draft")),
            "category": HarnessCategory(
                fm_data.get("category", "component-spec")
            ),
        }

        # 可选的嵌套对象
        if "source" in fm_data and isinstance(fm_data["source"], dict):
            meta_dict["source"] = fm_data["source"]
        if "platform" in fm_data and isinstance(fm_data["platform"], dict):
            meta_dict["platform"] = fm_data["platform"]
        if "references" in fm_data and isinstance(
            fm_data["references"], list
        ):
            meta_dict["references"] = fm_data["references"]

        meta = MetaLayer(**meta_dict)
        return meta, body

    # ------------------------------------------------------------------
    # L2 原则层提取
    # ------------------------------------------------------------------

    def _extract_principle_layer(self, doc: MDLDocument, body: str) -> None:
        """从 Markdown body 中提取设计原则（L2）"""
        # 查找设计原则相关章节
        # 策略：查找 ## 设计原则 / ## 设计策略 等标题下的内容
        principle_section = self._extract_section(body, [
            "设计原则", "设计策略", "Design Principles"
        ])

        if not principle_section:
            return

        principles = []
        # 尝试从 Markdown 表格中提取原则
        tables = self._extract_markdown_tables(principle_section)
        for table in tables:
            if len(table) >= 2:  # 至少 header + 1 row
                headers = table[0]
                # 寻找包含 原则/定义/行为假设 的表头
                name_col = self._find_column(headers, ["原则", "名称", "Principle"])
                def_col = self._find_column(headers, ["定义", "Definition"])
                assume_col = self._find_column(headers, ["行为假设", "假设", "Assumption"])

                for row in table[1:]:
                    if name_col < len(row) and row[name_col]:
                        principle = DesignPrinciple(
                            name=row[name_col],
                            definition=row[def_col] if def_col < len(row) else "",
                        )
                        if assume_col < len(row) and row[assume_col]:
                            principle.behavior_assumptions = [row[assume_col]]
                        principles.append(principle)

        if principles:
            doc.principle = PrincipleLayer(principles=principles)

    # ------------------------------------------------------------------
    # L3 组件规格提取
    # ------------------------------------------------------------------

    def _extract_component_spec(self, doc: MDLDocument, body: str) -> None:
        """从 Markdown body 中提取组件规格（L3）— 核心方法"""
        # 查找组件规格相关章节
        spec_section = self._extract_section(body, [
            "组件规格", "Component Spec", "结构化约束"
        ])

        if not spec_section:
            return

        # 策略 1: 提取 ```yaml 代码块中的组件定义
        yaml_blocks = self._extract_yaml_blocks(spec_section)
        for yaml_content in yaml_blocks:
            try:
                data = yaml.safe_load(yaml_content)
                if isinstance(data, dict):
                    doc.component_spec = self._parse_component_spec_from_yaml(data)
                    return  # 找到第一个有效的组件规格就返回
            except yaml.YAMLError:
                continue

        # 策略 2: 如果没有 YAML block，尝试从表格中推断基本信息
        basic_info = self._extract_section(body, ["基本信息"])
        if basic_info:
            tables = self._extract_markdown_tables(basic_info)
            for table in tables:
                if len(table) >= 2:
                    spec = self._parse_component_spec_from_table(table)
                    if spec:
                        doc.component_spec = spec
                        return

    def _parse_component_spec_from_yaml(self, data: dict[str, Any]) -> ComponentSpec:
        """将 YAML dict 转换为 ComponentSpec Pydantic 对象"""
        # 处理可能的包装键（如 component: { name: Tile, ... }）
        if len(data) == 1 and "component" in data:
            data = data["component"]

        spec_dict: dict[str, Any] = {
            "name": data.get("name", "Unknown"),
            "type": data.get("type", ""),
        }

        # Variants
        variants = data.get("variants", [])
        if variants:
            spec_dict["variants"] = [
                ComponentVariant(**v) if isinstance(v, dict) else v
                for v in variants
            ]

        # Fixed fields
        fixed_fields = data.get("fixed_fields", [])
        if fixed_fields:
            spec_dict["fixed_fields"] = [
                self._parse_field(f) if isinstance(f, dict) else f
                for f in fixed_fields
            ]

        # Optional fields
        optional_fields = data.get("optional_fields", [])
        if optional_fields:
            spec_dict["optional_fields"] = [
                self._parse_field(f) if isinstance(f, dict) else f
                for f in optional_fields
            ]

        # Constraints (排除性约束)
        constraints = data.get("constraints", [])
        if constraints:
            spec_dict["constraints"] = [
                ExclusionConstraint(**c) if isinstance(c, dict) else c
                for c in constraints
            ]

        # Layout rules
        layout = data.get("layout_rules")
        if layout and isinstance(layout, dict):
            spec_dict["layout_rules"] = LayoutRule(**layout)

        return ComponentSpec(**spec_dict)

    def _parse_field(self, data: dict[str, Any]) -> ComponentField:
        """解析单个组件字段定义"""
        field_dict = {
            "field": data.get("field", ""),
            "type": data.get("type", "string"),
            "required": data.get("required", True),
            "description": data.get("description", ""),
        }

        # 可选字段
        for opt_key, pydantic_key in [
            ("max_length", "max_length"),
            ("rationale", "rationale"),
            ("note", "note"),
        ]:
            if opt_key in data:
                field_dict[pydantic_key] = data[opt_key]

        # Visual spec
        vs = data.get("visual_spec")
        if vs and isinstance(vs, dict):
            field_dict["visual_spec"] = VisualSpec(**vs)

        # Implementation status
        status = data.get("implementation_status")
        if status:
            try:
                field_dict["implementation_status"] = ImplementationStatus(status)
            except ValueError:
                pass

        # Examples
        examples = data.get("examples")
        if examples and isinstance(examples, list):
            field_dict["examples"] = examples

        return ComponentField(**field_dict)

    def _parse_component_spec_from_table(
        self, table: list[list[str]]
    ) -> Optional[ComponentSpec]:
        """从 Markdown 表格中解析基本组件信息（降级策略）"""
        # 尝试匹配 属性|值 格式的表格
        for row in table:
            if len(row) >= 2:
                key, value = row[0].strip(), row[1].strip()
                if key == "组件名":
                    return ComponentSpec(name=value)
        return None

    # ------------------------------------------------------------------
    # 实例表提取
    # ------------------------------------------------------------------

    def _extract_instance_table(self, doc: MDLDocument, body: str) -> None:
        """从 Markdown body 中提取实例配置表（如各功能磁贴规格表）"""
        # 查找实例表相关章节
        table_section = self._extract_section(body, [
            "各功能磁贴规格表",
            "功能磁贴内容",
            "实例表",
            "Instance Table",
        ])

        if not table_section:
            return

        tables = self._extract_markdown_tables(table_section)
        for table in tables:
            if len(table) < 3:  # 至少 header + 2 行数据
                continue

            headers = table[0]
            rows = table[1:]

            # 检查是否是功能规格表（有 功能/尺寸 等列）
            func_col = self._find_column(headers, ["功能", "Function", "名称"])
            size_col = self._find_column(headers, ["尺寸", "Size", "类型"])
            bg_col = self._find_column(headers, ["背景", "Background"])

            if func_col >= 0 and size_col >= 0:
                instance_rows = []
                for row in rows:
                    if func_col < len(row) and row[func_col]:
                        instance_rows.append(InstanceTableRow(
                            function_name=row[func_col],
                            size=row[size_col] if size_col < len(row) else "",
                            background=row[bg_col] if bg_col < len(row) else "",
                            has_app_name=True,  # 默认值，从 √/× 推断可后续增强
                            has_app_logo=True,
                            dynamic_info=None,
                        ))
                if instance_rows:
                    doc.instance_table = instance_rows
                    return

    # ------------------------------------------------------------------
    # 设计理由提取
    # ------------------------------------------------------------------

    def _extract_rationale_entries(self, doc: MDLDocument, body: str) -> None:
        """从 Markdown body 中提取设计理由条目"""
        rationale_section = self._extract_section(body, [
            "设计理由汇总",
            "Rationale",
            "设计理由",
        ])

        if not rationale_section:
            return

        tables = self._extract_markdown_tables(rationale_section)
        for table in tables:
            if len(table) < 2:
                continue

            headers = table[0]
            elem_col = self._find_column(headers, ["元素", "Element", "项目"])
            story_col = self._find_column(headers, ["故事", "Story", "设计理由", "理由"])
            value_col = self._find_column(headers, ["用户价值", "Value", "价值"])

            if elem_col >= 0 and story_col >= 0:
                entries = []
                for row in table[1:]:
                    if elem_col < len(row) and row[elem_col]:
                        entries.append(RationaleEntry(
                            element=row[elem_col],
                            design_story=row[story_col] if story_col < len(row) else "",
                            user_value=row[value_col] if value_col < len(row) else "",
                        ))
                if entries:
                    doc.rationale_entries = entries
                    return

    # ------------------------------------------------------------------
    # L4 实例层提取
    # ------------------------------------------------------------------

    def _extract_instance_layer(self, doc: MDLDocument, body: str) -> None:
        """从 Markdown body 中提取 L4 实例层内容"""
        layer = InstanceLayer()

        # 待定项清单
        pending_section = self._extract_section(body, ["待定项清单", "待定项", "TBD"])
        if pending_section:
            tables = self._extract_markdown_tables(pending_section)
            for table in tables:
                if len(table) >= 2:
                    headers = table[0]
                    marker_col = self._find_column(headers, ["标记", "Marker"])
                    content_col = self._find_column(headers, ["内容", "Content"])
                    impact_col = self._find_column(headers, ["影响范围", "Impact"])
                    suggest_col = self._find_column(headers, ["建议", "Suggestion"])

                    if marker_col >= 0 and content_col >= 0:
                        for row in table[1:]:
                            if marker_col < len(row) and row[marker_col]:
                                layer.pending_items.append(PendingItem(
                                    marker=row[marker_col],
                                    content=row[content_col] if content_col < len(row) else "",
                                    impact_scope=row[impact_col] if impact_col < len(row) else "",
                                    suggestion=row[suggest_col] if suggest_col < len(row) else "",
                                ))

        # 变更记录
        change_section = self._extract_section(body, ["变更记录", "Change Record"])
        if change_section:
            tables = self._extract_markdown_tables(change_section)
            for table in tables:
                if len(table) >= 2:
                    headers = table[0]
                    seq_col = self._find_column(headers, ["序号", "Seq", "#"])
                    time_col = self._find_column(headers, ["时间", "Time", "日期"])
                    req_col = self._find_column(headers, ["需求名", "Requirement"])
                    content_col = self._find_column(headers, ["修订内容", "Change", "内容"])
                    author_col = self._find_column(headers, ["提出人", "Author"])

                    if seq_col >= 0:
                        for row in table[1:]:
                            if seq_col < len(row) and row[seq_col]:
                                try:
                                    seq = int(row[seq_col])
                                except (ValueError, TypeError):
                                    seq = 0
                                layer.change_records.append(ChangeRecord(
                                    seq=seq,
                                    time=row[time_col] if time_col < len(row) else "",
                                    requirement_name=row[req_col] if req_col < len(row) else "",
                                    change_content=row[content_col] if content_col < len(row) else "",
                                    author=row[author_col] if author_col < len(row) else "",
                                ))

        # 检查清单
        checklist_section = self._extract_section(body, [
            "审查检查清单", "检查清单", "Checklist"
        ])
        if checklist_section:
            # 检查清单通常以 - [ ] 或 - [x] 列表形式出现
            items = self._extract_checklist_items(checklist_section)
            if items:
                layer.checklist_items = items

        # 特殊规则（标注说明）
        special_section = self._extract_section(body, [
            "实例标注说明", "特殊规则", "标注说明"
        ])
        if special_section:
            # 特殊规则通常是有编号的文本列表
            lines = special_section.split("\n")
            idx = 0
            for line in lines:
                match = re.match(r"^\s*(\d+)[\.、：]\s*(.+)", line)
                if match:
                    idx += 1
                    layer.special_rules.append(SpecialRule(
                        id=idx,
                        function_name="",
                        special_description=match.group(2).strip(),
                    ))

        if any([layer.pending_items, layer.change_records,
               layer.checklist_items, layer.special_rules]):
            doc.instance_layer = layer

    # ------------------------------------------------------------------
    # 通用提取工具方法
    # ------------------------------------------------------------------

    def _extract_section(self, body: str, keywords: list[str]) -> Optional[str]:
        """根据关键词提取 Markdown 章节（从 ## 标题到下一个同级/更高级标题之前的内容）"""
        lines = body.split("\n")
        start_idx = None
        depth = 0

        for i, line in enumerate(lines):
            # 匹配 ## 标题行
            heading_match = re.match(r"^(#{2,4})\s+(.+)", line)
            if heading_match:
                h_depth = len(heading_match.group(1))
                h_text = heading_match.group(2).strip()

                if start_idx is not None and h_depth <= depth:
                    # 遇到同级或更高级标题，结束当前章节
                    return "\n".join(lines[start_idx:i])

                for kw in keywords:
                    if kw.lower() in h_text.lower():
                        start_idx = i + 1  # 不包含标题行本身
                        depth = h_depth
                        break

        if start_idx is not None:
            return "\n".join(lines[start_idx:])
        return None

    def _extract_yaml_blocks(self, text: str) -> list[str]:
        """从文本中提取所有 ```yaml 代码块内容"""
        pattern = r"```ya?ml\s*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    def _extract_markdown_tables(self, text: str) -> list[list[list[str]]]:
        """从文本中提取所有 Markdown 表格（返回二维字符串数组列表）"""
        tables = []
        lines = text.split("\n")

        i = 0
        while i < len(lines):
            # 检测表头行（至少有一个 |）
            if "|" in lines[i] and lines[i].strip().startswith("|"):
                # 收集表格行
                table_lines = []
                while i < len(lines) and "|" in lines[i]:
                    stripped = lines[i].strip()
                    if stripped.startswith("|"):
                        cells = [c.strip() for c in stripped.split("|")[1:-1]]
                        # 跳过分隔行（如 |---|---|）
                        if not all(re.match(r"^[\s\-:]+$", c) or c == "" for c in cells):
                            table_lines.append(cells)
                    i += 1

                if len(table_lines) >= 2:  # 至少 header + 1 data row
                    tables.append(table_lines)
                continue

            i += 1

        return tables

    def _find_column(
        self, headers: list[str], candidates: list[str]
    ) -> int:
        """在表头中查找匹配的列索引"""
        for i, h in enumerate(headers):
            h_lower = h.strip().lower()
            for candidate in candidates:
                if candidate.lower() in h_lower:
                    return i
        return -1

    def _extract_checklist_items(self, text: str) -> list[ChecklistItem]:
        """从文本中提取检查清单项（- [ ] / - [x] 格式）"""
        items = []

        # 检测当前级别（must/should/must_not）
        current_level = ChecklistLevel.SHOULD

        for line in text.split("\n"):
            # 检测级别标题
            level_match = re.match(
                r"^#+\s*(必须|MUST|应该|SHOULD|不应该|MUST\s*NOT)", line, re.IGNORECASE
            )
            if level_match:
                level_text = level_match.group(1).upper()
                if "MUST NOT" in level_text or "不应该" in level_text:
                    current_level = ChecklistLevel.MUST_NOT
                elif "MUST" in level_text or "必须" in level_text:
                    current_level = ChecklistLevel.MUST
                elif "SHOULD" in level_text or "应该" in line.upper():
                    current_level = ChecklistLevel.SHOULD
                continue

            # 检测列表项
            item_match = re.match(r"^[\s]*-\s*\[[ x]\]\s*(.+)", line)
            if item_match:
                items.append(ChecklistItem(
                    level=current_level,
                    item=item_match.group(1).strip(),
                ))

        return items
