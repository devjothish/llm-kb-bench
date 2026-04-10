import yaml
import pytest
from pathlib import Path

def test_manifest_loads():
    manifest_path = Path("corpus/manifest.yaml")
    assert manifest_path.exists(), "manifest.yaml must exist"
    with open(manifest_path) as f:
        data = yaml.safe_load(f)
    assert "sources" in data
    assert "repos" in data["sources"]
    assert "blog_posts" in data["sources"]
    assert len(data["sources"]["repos"]) >= 3

def test_manifest_repos_have_required_fields():
    with open("corpus/manifest.yaml") as f:
        data = yaml.safe_load(f)
    for repo in data["sources"]["repos"]:
        assert "name" in repo, f"repo missing name: {repo}"
        assert "url" in repo, f"repo missing url: {repo}"
        assert "commit" in repo, f"repo missing commit: {repo}"
        assert "include" in repo, f"repo missing include: {repo}"

def test_manifest_blog_posts_have_required_fields():
    with open("corpus/manifest.yaml") as f:
        data = yaml.safe_load(f)
    for post in data["sources"]["blog_posts"]:
        assert "name" in post, f"post missing name: {post}"
        assert "url" in post, f"post missing url: {post}"
