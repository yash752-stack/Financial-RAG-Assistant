from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_expected_repo_files_exist():
    expected = [
        ROOT / "app.py",
        ROOT / "README.md",
        ROOT / "requirements.txt",
        ROOT / ".env.example",
        ROOT / "Dockerfile",
        ROOT / "src" / "config.py",
        ROOT / "src" / "document_parser.py",
        ROOT / "src" / "llm.py",
        ROOT / "src" / "market_data.py",
        ROOT / "src" / "retriever.py",
        ROOT / "src" / "ui.py",
    ]
    for path in expected:
        assert path.exists(), f"Missing expected file: {path}"

