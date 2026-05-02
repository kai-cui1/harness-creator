"""MDL 渲染器单元测试"""

from pathlib import Path

import pytest


class TestMDLRenderer:
    """MDL 渲染器测试"""

    def test_render_produces_valid_markdown(
        self, parsed_reference_doc
    ):
        """渲染输出应为有效的 Markdown 格式"""
        from src.harness_creator.mdl.renderer import MDLRenderer

        renderer = MDLRenderer()
        output = renderer.render(parsed_reference_doc)

        # 应包含 YAML frontmatter 边界
        assert "---" in output
        assert "mdl:" in output

        # 应包含标题
        assert "# 磁贴组件设计规范" in output

        # 应包含组件规格章节
        assert "## 组件规格" in output or "Tile" in output

        # 长度合理（>1000 字符）
        assert len(output) > 1000

    def test_render_to_file_writes_content(
        self, parsed_reference_doc, tmp_path: Path
    ):
        """render_to_file 应正确写入文件"""
        from src.harness_creator.mdl.renderer import MDLRenderer

        renderer = MDLRenderer()
        out = tmp_path / "test_render_output.mdl.md"
        renderer.render_to_file(parsed_reference_doc, out)

        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert len(content) > 500
        assert "---" in content

    def test_round_trip_parse_render(
        self, parsed_reference_doc, parser
    ):
        """渲染后再解析，核心数据应保留"""
        from src.harness_creator.mdl.renderer import MDLRenderer

        renderer = MDLRenderer()
        rendered = renderer.render(parsed_reference_doc)

        # 将渲染结果写入临时文件再解析
        from src.harness_creator.mdl.models import MDLDocument
        import tempfile

        with tempfile.NamedTemporaryFile(
            suffix=".mdl.md", mode="w", encoding="utf-8", delete=False
        ) as f:
            f.write(rendered)
            f.flush()
            temp_path = Path(f.name)

        try:
            doc2 = parser.parse_file(temp_path)
            # 核心字段应一致
            assert doc2.meta.name == parsed_reference_doc.meta.name
            assert doc2.component_spec is not None
            assert (
                len(doc2.component_spec.variants)
                == len(parsed_reference_doc.component_spec.variants)
            )
            assert (
                len(doc2.component_spec.constraints)
                == len(parsed_reference_doc.component_spec.constraints)
            )
            assert len(doc2.instance_table) == len(parsed_reference_doc.instance_table)
        finally:
            temp_path.unlink(missing_ok=True)


@pytest.fixture
def tmp_path(tmpdir):
    return Path(tmpdir)
