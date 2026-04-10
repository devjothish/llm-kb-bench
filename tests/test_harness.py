from benchmarks.harness import discover_tools, TOOL_REGISTRY

def test_tool_registry_has_entries():
    assert len(TOOL_REGISTRY) >= 2
    assert "graphify" in TOOL_REGISTRY
    assert "naive-rag" in TOOL_REGISTRY

def test_discover_tools_returns_wrappers():
    tools = discover_tools()
    assert len(tools) >= 2
    for tool in tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "setup")
        assert hasattr(tool, "compile")
        assert hasattr(tool, "query")
