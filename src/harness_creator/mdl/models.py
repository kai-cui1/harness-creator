"""MDL（Methodology Description Language）Pydantic 数据模型定义。

定义 L1（元层）→ L2（原则层）→ L3（规范层）→ L4（实例层）
全部数据结构，是解析器、校验器、渲染器的基础依赖。
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ====================================================================
# 枚举类型
# ====================================================================


class HarnessStatus(str, Enum):
    """MDL 文档状态"""

    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


class HarnessCategory(str, Enum):
    """Harness 分类（MVP 仅支持 component-spec）"""

    COMPONENT_SPEC = "component-spec"
    INTERACTION_FLOW = "interaction-flow"  # v0.2+
    EXCEPTION_PATTERN = "exception-pattern"  # v0.2+
    DESIGN_PRINCIPLE = "design-principle"


class ImplementationStatus(str, Enum):
    """字段/功能的实现状态"""

    ACTIVE = "active"  # 当前有效（默认，可省略）
    DEFERRED = "deferred"  # 本期不实现
    PLANNED = "planned"  # 计划中
    DEPRECATED = "deprecated"  # 已废弃


class ChecklistLevel(str, Enum):
    """检查清单级别"""

    MUST = "must"
    SHOULD = "should"
    MUST_NOT = "must_not"


# ====================================================================
# L1 元层 (Meta Layer)
# ====================================================================


class SourceInfo(BaseModel):
    """来源信息"""

    file: Optional[str] = None
    product: Optional[str] = None


class PlatformInfo(BaseModel):
    """目标平台信息"""

    os: Optional[str] = None
    screen: Optional[str] = None
    screen_axure: Optional[str] = Field(
        default=None, description="Axure 坐标系尺寸（通常为实际像素的一半）"
    )
    device: Optional[str] = None


class ReferenceItem(BaseModel):
    """引用关系条目"""

    name: str
    relation: Literal["inherits", "extends", "conflicts", "inspired_by"]


class MetaLayer(BaseModel):
    """L1 元层 — YAML Frontmatter 对应的数据模型"""

    mdl: Literal["1.0"] = "1.0"
    name: str = Field(..., description="规范名称")
    version: str = Field(default="0.1.0", description="版本号 (SemVer)")
    author: str = Field(..., description="作者/维护者")
    date: Optional[str] = Field(None, description="原始文档日期")
    source: SourceInfo = Field(default_factory=SourceInfo)
    platform: PlatformInfo = Field(default_factory=PlatformInfo)
    target_agent: Literal["claude-code-skill"] = "claude-code-skill"
    status: HarnessStatus = HarnessStatus.DRAFT
    category: HarnessCategory = HarnessCategory.COMPONENT_SPEC
    references: list[ReferenceItem] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name 不能为空")
        return v.strip()

    @field_validator("version")
    @classmethod
    def version_must_be_semver_like(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) < 2:
            raise ValueError(f"version 应为 SemVer 格式，如 '0.1.0'，当前值: {v}")
        return v


# ====================================================================
# L2 原则层 (Principle Layer)
# ====================================================================


class DesignPrinciple(BaseModel):
    """设计原则条目"""

    name: str = Field(..., description="原则名称，如「易学」「高效」")
    definition: str = Field(..., description="原则定义")
    manifestation: str = Field(
        default="", description="在具体组件/场景中的体现"
    )
    behavior_assumptions: list[str] = Field(
        default_factory=list, description="相关的行为假设列表"
    )


class PrincipleLayer(BaseModel):
    """L2 原则层"""

    principles: list[DesignPrinciple] = Field(default_factory=list)
    scope: list[str] = Field(
        default_factory=list, description="适用范围"
    )
    exclusions: list[str] = Field(
        default_factory=list, description="不适用范围 / 排除场景"
    )
    behavior_assumptions: list[str] = Field(
        default_factory=list, description="全局行为假设"
    )


# ====================================================================
# L3 规范层 — 组件规格 (Component Specification) [MVP 核心]
# ====================================================================


class VisualSpec(BaseModel):
    """视觉规格"""

    color: Optional[str] = None
    size: Optional[str] = None
    position: Optional[str] = None
    font_size: Optional[str] = None
    alignment: Optional[str] = None


class ComponentField(BaseModel):
    """组件字段定义"""

    field: str = Field(..., description="字段名")
    type: Literal["image", "string", "number", "boolean", "enum"] = Field(
        ..., description="字段类型"
    )
    required: bool = True
    description: str = ""
    max_length: Optional[int] = Field(
        default=None, description="最大长度（字符串类型时）"
    )
    visual_spec: Optional[VisualSpec] = None
    rationale: Optional[str] = Field(
        default=None, description="设计理由（为什么有这个字段）"
    )
    implementation_status: Optional[ImplementationStatus] = None
    examples: list[str] = Field(default_factory=list)
    note: Optional[str] = None

    @field_validator("field")
    @classmethod
    def field_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field 名称不能为空")
        return v.strip()


class ComponentVariant(BaseModel):
    """组件尺寸/样式变体"""

    name: str = Field(..., description="变体名，如 'wide', 'small'")
    description: str = ""
    aspect_ratio: Optional[str] = Field(
        default=None, description="宽高比描述"
    )
    contains_fixed: list[str] = Field(
        default_factory=list, description="包含的固定字段列表"
    )
    contains_optional: list[str] = Field(
        default_factory=list, description="包含的可选字段列表"
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("variant name 不能为空")
        return v.strip().lower()


class ExclusionConstraint(BaseModel):
    """排除性约束（"不做什么"）"""

    rule: str = Field(..., description="约束规则文本")
    rationale: str = Field(..., description="设计理由")
    status: Optional[str] = Field(
        default=None, description="附加状态，如 'future_low_priority'"
    )

    @field_validator("rule")
    @classmethod
    def rule_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("排除性约束 rule 不能为空")
        return v.strip()

    @field_validator("rationale")
    @classmethod
    def rationale_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("排除性约束 rationale 不能为空")
        return v.strip()


class LayoutRule(BaseModel):
    """布局规则"""

    row_1: list[str] = Field(default_factory=list)
    row_2_plus: list[str] = Field(default_factory=list)
    total_small_tiles: Optional[int] = None
    notes: Optional[str] = None


class ComponentSpec(BaseModel):
    """L3 组件规格（MVP 核心数据结构）"""

    name: str = Field(..., description="组件名")
    type: str = Field(default="", description="组件类型描述")
    parent_container: Optional[str] = Field(
        default=None, description="父容器名称"
    )
    size_variants: list[str] = Field(
        default_factory=list, description="尺寸变体名称列表"
    )

    variants: list[ComponentVariant] = Field(default_factory=list)
    fixed_fields: list[ComponentField] = Field(default_factory=list)
    optional_fields: list[ComponentField] = Field(default_factory=list)
    constraints: list[ExclusionConstraint] = Field(default_factory=list)
    layout_rules: Optional[LayoutRule] = None

    @model_validator(mode="after")
    def validate_component_spec(self) -> "ComponentSpec":
        """组件规格的业务规则校验"""
        # 至少需要一个 variant 或一个 size_variant
        if not self.variants and not self.size_variants:
            raise ValueError(
                "组件规格必须至少定义一个 variant 或 size_variant"
            )
        # 至少需要一个 fixed_field
        if not self.fixed_fields:
            raise ValueError("组件规格必须至少定义一个 fixed_field")
        return self


# ====================================================================
# L3 规范层 — 辅助数据结构
# ====================================================================


class InstanceTableRow(BaseModel):
    """实例表行（各功能/场景的具体配置）"""

    function_name: str
    size: str
    background: str
    has_app_name: bool
    has_app_logo: bool
    dynamic_info: Optional[str] = None


class RationaleEntry(BaseModel):
    """设计理由条目"""

    element: str = Field(..., description="元素名称")
    design_story: str = Field(..., description="设计故事（用户价值叙述）")
    user_value: str = Field(..., description="用户价值")


# ====================================================================
# L4 实例层 (Instance Layer)
# ====================================================================


class SpecialRule(BaseModel):
    """特殊规则（针对特定功能/场景的补充说明）"""

    id: int
    function_name: str
    special_description: str


class PendingItem(BaseModel):
    """待定项"""

    marker: str = Field(..., description="标记文本，如 '(待定)', '(本期不实现)'")
    content: str = Field(..., description="待定内容描述")
    impact_scope: str = Field(..., description="影响范围")
    suggestion: str = Field(..., description="建议处理方式")


class ChangeRecord(BaseModel):
    """变更记录"""

    seq: int
    time: str
    requirement_name: str
    change_content: str
    author: str


class ChecklistItem(BaseModel):
    """审查检查清单项（供 Agent 使用）"""

    level: ChecklistLevel
    item: str


class InstanceLayer(BaseModel):
    """L4 实例层"""

    special_rules: list[SpecialRule] = Field(default_factory=list)
    pending_items: list[PendingItem] = Field(default_factory=list)
    change_records: list[ChangeRecord] = Field(default_factory=list)
    checklist_items: list[ChecklistItem] = Field(default_factory=list)


# ====================================================================
# 顶层 MDL 文档
# ====================================================================


class MDLDocument(BaseModel):
    """完整的 MDL 文档（所有层的容器）

    这是 MDL 解析器的输出类型和渲染器的输入类型，
    是整个系统的核心数据结构。
    """

    meta: MetaLayer
    principle: Optional[PrincipleLayer] = None
    component_spec: Optional[ComponentSpec] = None
    instance_table: list[InstanceTableRow] = Field(default_factory=list)
    rationale_entries: list[RationaleEntry] = Field(default_factory=list)
    instance_layer: Optional[InstanceLayer] = None

    # 原始 Markdown 正文（保留用于 round-trip 时非结构化内容的还原）
    raw_body: Optional[str] = Field(default=None, exclude=True)

    @property
    def display_name(self) -> str:
        """用于显示的简短名称"""
        return self.meta.name
