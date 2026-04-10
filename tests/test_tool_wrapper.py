from tools.base import ToolWrapper
import pytest


def test_tool_wrapper_is_abstract():
    with pytest.raises(TypeError):
        ToolWrapper()


def test_tool_wrapper_interface():
    assert hasattr(ToolWrapper, "setup")
    assert hasattr(ToolWrapper, "compile")
    assert hasattr(ToolWrapper, "query")
    assert hasattr(ToolWrapper, "lint")
    assert hasattr(ToolWrapper, "name")
    assert hasattr(ToolWrapper, "version")
