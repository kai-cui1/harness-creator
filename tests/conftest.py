"""pytest 配置和共享 fixtures"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from src.harness_creator.mdl.models import (
    MDLDocument,
    MetaLayer,
    ComponentSpec,
    ComponentVariant,
    ComponentField,
    ExclusionConstraint,
    PrincipleLayer,
    DesignPrinciple,
    InstanceTableRow,
    RationaleEntry,
    InstanceLayer,
    PendingItem,
    ChangeRecord,
    ChecklistItem,
)
from src.harness_creator.mdl.parser import MDLParser
from src.harness_creator.mdl.validator import MDLValidator, ValidationResult


@pytest.fixture
def reference_mdl_path() -> Path:
    """参考 MDL 文件路径（磁贴组件规范）"""
    return Path(__file__).parent.parent / "harnesses" / "tile-component-spec.mdl.md"


@pytest.fixture
def parser() -> MDLParser:
    return MDLParser()


@pytest.fixture
def validator() -> MDLValidator:
    return MDLValidator()


@pytest.fixture
def parsed_reference_doc(reference_mdl_path: Path, parser: MDLParser) -> MDLDocument:
    """已解析的参考文档"""
    return parser.parse_file(reference_mdl_path)


@pytest.fixture
def minimal_meta() -> MetaLayer:
    """最小有效元层"""
    return MetaLayer(
        name="测试规范",
        author="测试者",
        source={"file": "test.html"},
        platform={"os": "Android 8.1"},
    )


@pytest.fixture
def valid_component_spec() -> ComponentSpec:
    """有效组件规格（Tile 组件简化版）"""
    return ComponentSpec(
        name="TestTile",
        type="测试组件",
        variants=[
            ComponentVariant(name="wide", description="宽磁贴"),
            ComponentVariant(name="small", description="小磁贴"),
        ],
        fixed_fields=[
            ComponentField(field="icon", type="image", required=True),
            ComponentField(field="name", type="string", required=True),
        ],
        constraints=[
            ExclusionConstraint(
                rule="不支持自定义尺寸", rationale="保证一致性"
            ),
        ],
    )
