"""MDL 解析器单元测试"""

import pytest

from src.harness_creator.mdl.parser import MDLParser, MDLParseError


class TestMDLParser:
    """MDL 解析器测试"""

    def test_parse_reference_file(self, parsed_reference_doc):
        """能正确解析已有的 tile-component-spec.mdl.md"""
        doc = parsed_reference_doc
        assert doc.meta.name == "磁贴组件设计规范"
        assert doc.meta.version == "0.1.0"
        assert "黄林森" in doc.meta.author

    def test_parse_component_spec(self, parsed_reference_doc):
        """解析出的组件规格应完整"""
        spec = parsed_reference_doc.component_spec
        assert spec is not None
        assert spec.name == "Tile"
        assert len(spec.variants) == 2
        variant_names = {v.name for v in spec.variants}
        assert "wide" in variant_names
        assert "small" in variant_names
        assert len(spec.fixed_fields) >= 2
        field_names = {f.field for f in spec.fixed_fields}
        assert "app_icon" in field_names
        assert "app_name" in field_names
        assert len(spec.constraints) == 5

    def test_parse_instance_table(self, parsed_reference_doc):
        """实例表应包含 9 行数据"""
        assert len(parsed_reference_doc.instance_table) == 9
        functions = {r.function_name for r in parsed_reference_doc.instance_table}
        assert "拍照翻译" in functions
        assert "SOS" in functions

    def test_parse_principles(self, parsed_reference_doc):
        """设计原则应提取到"""
        assert parsed_reference_doc.principle is not None
        assert len(parsed_reference_doc.principle.principles) == 3

    def test_parse_rationale(self, parsed_reference_doc):
        """设计理由应提取到"""
        assert len(parsed_reference_doc.rationale_entries) == 5

    def test_parse_instance_layer(self, parsed_reference_doc):
        """L4 实例层应提取到"""
        layer = parsed_reference_doc.instance_layer
        assert layer is not None
        assert len(layer.pending_items) == 5
        assert len(layer.change_records) == 2
        assert len(layer.checklist_items) > 0

    def test_parse_nonexistent_file(self, parser: MDLParser):
        """不存在的文件应抛出 MDLParseError"""
        from pathlib import Path
        with pytest.raises(MDLParseError):
            parser.parse_file(Path("/nonexistent/file.mdl.md"))

    def test_round_trip_preserves_core_data(
        self, parsed_reference_doc, validator
    ):
        """Round-trip（parse → validate）核心数据应保留"""
        result = validator.validate(parsed_reference_doc)
        # 参考文件应该通过校验（0 errors）
        assert result.is_valid or len(result.errors) == 0
