"""Download and verify the Karpathy corpus."""

import hashlib
import os
import shutil
import subprocess
import yaml
from pathlib import Path

CORPUS_DIR = Path("corpus")
RAW_DIR = CORPUS_DIR / "raw"
MANIFEST_PATH = CORPUS_DIR / "manifest.yaml"


def load_manifest() -> dict:
    with open(MANIFEST_PATH) as f:
        return yaml.safe_load(f)


def download_repo(repo: dict, target_dir: Path) -> None:
    name = repo["name"]
    url = repo["url"]
    commit = repo["commit"]
    dest = target_dir / name

    if dest.exists():
        print(f"  [skip] {name} already exists")
        return

    print(f"  [clone] {name} from {url} @ {commit}")
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", commit, url, str(dest)],
        check=True,
        capture_output=True,
    )

    # Remove .git to save space
    git_dir = dest / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)

    # Filter to included extensions only
    include_exts = set()
    for pattern in repo.get("include", []):
        ext = pattern.lstrip("*")
        include_exts.add(ext)

    if include_exts:
        for fpath in dest.rglob("*"):
            if fpath.is_file() and fpath.suffix not in include_exts:
                fpath.unlink()

        for dirpath in sorted(dest.rglob("*"), reverse=True):
            if dirpath.is_dir() and not any(dirpath.iterdir()):
                dirpath.rmdir()


def download_blog_post(post: dict, target_dir: Path) -> None:
    name = post["name"]
    url = post["url"]
    dest = target_dir / "blog_posts" / f"{name}.md"

    if dest.exists():
        print(f"  [skip] {name} already exists")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  [fetch] {name} from {url}")

    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, output_format="text", include_links=True)
            if text:
                header = f"# {post.get('description', name)}\n\nSource: {url}\n\n---\n\n"
                dest.write_text(header + text)
                return
    except ImportError:
        pass

    # Fallback: save URL reference
    dest.write_text(
        f"# {post.get('description', name)}\n\nSource: {url}\n\n"
        f"Note: Auto-download failed. Manually save this URL as markdown.\n"
    )


def download_all() -> None:
    manifest = load_manifest()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading repos...")
    for repo in manifest["sources"].get("repos", []):
        download_repo(repo, RAW_DIR)

    print("Downloading blog posts...")
    for post in manifest["sources"].get("blog_posts", []):
        download_blog_post(post, RAW_DIR)

    total = sum(1 for _ in RAW_DIR.rglob("*") if _.is_file())
    print(f"\nCorpus ready: {total} files in {RAW_DIR}")


if __name__ == "__main__":
    download_all()
