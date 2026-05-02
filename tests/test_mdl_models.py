"""MDL Pydantic 数据模型单元测试"""

import pytest
from pydantic import ValidationError

from src.harness_creator.mdl.models import (
    MetaLayer,
    ComponentSpec,
    ComponentVariant,
    ComponentField,
    ExclusionConstraint,
    HarnessStatus,
    HarnessCategory,
    ImplementationStatus,
    MDLDocument,
)


class TestMetaLayer:
    """L1 元层测试"""

    def test_minimal_valid_meta(self, minimal_meta: MetaLayer):
        """最小有效元层应创建成功"""
        assert minimal_meta.name == "测试规范"
        assert minimal_meta.status == HarnessStatus.DRAFT
        assert minimal_meta.mdl == "1.0"

    def test_default_values(self):
        """默认值应正确设置"""
        meta = MetaLayer(name="x", author="y")
        assert meta.version == "0.1.0"
        assert meta.status == HarnessStatus.DRAFT
        assert meta.category == HarnessCategory.COMPONENT_SPEC

    def test_reject_empty_name(self):
        """空名称应报错"""
        with pytest.raises(ValidationError):
            MetaLayer(name="", author="test")

    def test_reject_whitespace_name(self):
        """纯空格名称应报错"""
        with pytest.raises(ValidationError):
            MetaLayer(name="   ", author="test")

    def test_invalid_version_format(self):
        """非 SemVer 格式版本号应报错"""
        with pytest.raises(ValidationError):
            MetaLayer(name="test", version="abc")


class TestComponentSpec:
    """L3 组件规格测试"""

    def test_valid_spec(self, valid_component_spec: ComponentSpec):
        """有效组件规格应创建成功"""
        assert valid_component_spec.name == "TestTile"
        assert len(valid_component_spec.variants) == 2
        assert len(valid_component_spec.fixed_fields) == 2
        assert len(valid_component_spec.constraints) == 1

    def test_reject_no_variants(self):
        """无 variant 应报错"""
        with pytest.raises(ValidationError):
            ComponentSpec(
                name="Empty",
                fixed_fields=[ComponentField(field="f", type="string")],
            )

    def test_reject_no_fixed_fields(self):
        """无 fixed_field 应报错"""
        with pytest.raises(ValidationError):
            ComponentSpec(
                name="Empty",
                variants=[ComponentVariant(name="v1")],
            )

    def test_exclusion_constraint_requires_rationale(self):
        """排除性约束 rationale 不能为空"""
        with pytest.raises(ValidationError):
            ExclusionConstraint(rule="不支持", rationale="")


class TestComponentField:
    """组件字段测试"""

    def test_valid_field(self):
        """有效字段应创建成功"""
        f = ComponentField(field="name", type="string", required=True)
        assert f.field == "name"
        assert f.type == "string"
        assert f.required is True

    def test_optional_field_with_status(self):
        """可选字段可带 implementation_status"""
        f = ComponentField(
            field="dynamic",
            type="string",
            required=False,
            implementation_status=ImplementationStatus.DEFERRED,
        )
        assert f.implementation_status == ImplementationStatus.DEFERRED


class TestMDLDocument:
    """完整 MDL 文档测试"""

    def test_create_full_document(
        self, minimal_meta: MetaLayer, valid_component_spec: ComponentSpec
    ):
        """完整的 MDLDocument 应创建成功"""
        doc = MDLDocument(meta=minimal_meta, component_spec=valid_component_spec)
        assert doc.display_name == "测试规范"
        assert doc.component_spec is not None
        assert len(doc.instance_table) == 0

    def test_display_name_property(self):
        """display_name 属性应返回 meta.name"""
        doc = MDLDocument(
            meta=MetaLayer(name="显示名称测试", author="a")
        )
        assert doc.display_name == "显示名称测试"
