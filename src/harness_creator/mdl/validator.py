"""MDL 校验器。

对 MDLDocument 执行 schema 校验和业务规则校验，
返回结构化的 ValidationResult（含 errors/warnings 列表）。

MVP 校验范围（按设计决策 Q2）：
- L1 元层：必填字段、枚举值、格式
- L3 组件规格：骨架校验（至少 1 variant、1 fixed_field）
- 跨层一致性：instance_table 的 size 值必须在 variants 中
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from .models import (
    MDLDocument,
    HarnessCategory,
    HarnessStatus,
    ImplementationStatus,
)


class ValidationError(BaseModel):
    """校验错误"""

    layer: str  # "L1", "L2", "L3", "L4"
    field_path: str  # 如 "meta.name", "component_spec.variants[0]"
    message: str
    severity: str = "error"  # "error" 或 "warning"


class ValidationWarning(BaseModel):
    """校验警告"""

    layer: str
    field_path: str
    message: str


class ValidationResult(BaseModel):
    """校验结果"""

    is_valid: bool = True
    errors: list[ValidationError] = []
    warnings: list[ValidationWarning] = []

    def add_error(self, layer: str, field_path: str, message: str) -> None:
        self.errors.append(ValidationError(
            layer=layer, field_path=field_path, message=message
        ))
        self.is_valid = False

    def add_warning(self, layer: str, field_path: str, message: str) -> None:
        self.warnings.append(ValidationWarning(
            layer=layer, field_path=field_path, message=message
        ))


class MDLValidator:
    """MDL 校验器"""

    def validate(self, doc: MDLDocument) -> ValidationResult:
        """执行全部校验，返回校验结果"""
        result = ValidationResult()

        self._validate_l1_meta(doc, result)
        self._validate_l3_component_spec(doc, result)
        self._validate_cross_layer(doc, result)

        return result

    # ------------------------------------------------------------------
    # L1 元层校验
    # ------------------------------------------------------------------

    def _validate_l1_meta(
        self, doc: MDLDocument, result: ValidationResult
    ) -> None:
        """L1 必填字段 + 枚举值 + 格式校验"""
        meta = doc.meta

        # mdl 版本
        if meta.mdl != "1.0":
            result.add_error(
                "L1", "meta.mdl", f"MDL 版本必须是 '1.0'，当前值: {meta.mdl}"
            )

        # name 非空（Pydantic 已保证，但双重检查）
        if not meta.name or not meta.name.strip():
            result.add_error("L1", "meta.name", "name 不能为空")

        # version 格式
        parts = meta.version.split(".")
        if len(parts) < 2:
            result.add_error(
                "L1",
                "meta.version",
                f"version 应为 SemVer 格式 (如 '0.1.0')，当前值: {meta.version}",
            )

        # author 非空
        if not meta.author or not meta.author.strip():
            result.add_warning("L1", "meta.author", "建议填写 author 字段")

        # status 枚举合法性（Pydantic 已保证）
        # category 枚举合法性（Pydantic 已保证）

        # target_agent MVP 只支持 claude-code-skill
        if meta.target_agent != "claude-code-skill":
            result.add_warning(
                "L1",
                "meta.target_agent",
                f"MVP 仅支持 target_agent='claude-code-skill'，当前值: {meta.target_agent}",
            )

    # ------------------------------------------------------------------
    # L3 组件规格校验
    # ------------------------------------------------------------------

    def _validate_l3_component_spec(
        self, doc: MDLDocument, result: ValidationResult
    ) -> None:
        """L3 组件规格骨架校验"""
        spec = doc.component_spec
        if not spec:
            result.add_warning("L3", "component_spec", "未找到组件规格定义")
            return

        # 至少一个 variant
        if not spec.variants and not spec.size_variants:
            result.add_error(
                "L3",
                "component_spec",
                "组件规格必须至少定义一个 variant 或 size_variant",
            )

        # 至少一个 fixed_field
        if not spec.fixed_fields:
            result.add_error(
                "L3",
                "component_spec.fixed_fields",
                "组件规格必须至少定义一个 fixed_field",
            )

        # 校验每个 variant
        for i, v in enumerate(spec.variants):
            vpath = f"component_spec.variants[{i}]"
            if not v.name or not v.name.strip():
                result.add_error("L3", f"{vpath}.name", "variant name 不能为空")

        # 校验每个 fixed_field
        for i, f in enumerate(spec.fixed_fields):
            fpath = f"component_spec.fixed_fields[{i}]"
            if not f.field or not f.field.strip():
                result.add_error("L3", f"{fpath}.field", "field 名称不能为空")
            if f.required and not f.description:
                result.add_warning(
                    "L3",
                    f"{fpath}.description",
                    f"必填字段 '{f.field}' 建议填写 description",
                )

        # 校验排除性约束
        for i, c in enumerate(spec.constraints):
            cpath = f"component_spec.constraints[{i}]"
            if not c.rule or not c.rule.strip():
                result.add_error("L3", cpath + ".rule", "排除性约束 rule 不能为空")
            if not c.rationale or not c.rationale.strip():
                result.add_error(
                    "L3", cpath + ".rationale", "排除性约束 rationale 不能为空"
                )

    # ------------------------------------------------------------------
    # 跨层一致性校验
    # ------------------------------------------------------------------

    def _validate_cross_layer(
        self, doc: MDLDocument, result: ValidationResult
    ) -> None:
        """跨层一致性校验"""
        spec = doc.component_spec
        if not spec:
            return

        # instance_table 中的 size 值必须在 variants 中定义
        valid_sizes = {v.name.lower() for v in spec.variants}
        valid_sizes.update(spec.size_variants)  # 也允许 size_variants 中的名称

        for i, row in enumerate(doc.instance_table):
            rpath = f"instance_table[{i}]"
            size_lower = row.size.strip().lower().strip("`")
            if size_lower and size_lower not in valid_sizes and size_lower not in (
                "wide",
                "small",
            ):
                # wide/small 是常见值，不报错；其他未知值才警告
                result.add_warning(
                    "L4",
                    f"{rpath}.size",
                    f"实例表中 size='{row.size}' 未在组件 variants 中定义",
                )

        # pending_items 的 marker 应该是已知模式
        known_markers = {"(待定)", "(待 UI 定)", "(本期不实现)",
                        "(可能会去掉)", "(优先级低)"}
        if doc.instance_layer:
            for i, pi in enumerate(doc.instance_layer.pending_items):
                ppath = f"instance_layer.pending_items[{i}]"
                if pi.marker not in known_markers:
                    result.add_warning(
                        "L4",
                        f"{ppath}.marker",
                        f"待定项标记 '{pi.marker}' 不是常见格式，请确认是否正确",
                    )
