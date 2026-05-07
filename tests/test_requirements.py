from pathlib import Path


def test_requirements_contains_pytest():
    requirements = Path("requirements.txt").read_text().splitlines()
    requirements = [line.strip() for line in requirements if line.strip() and not line.startswith("#")]
    assert "pytest" in requirements, "requirements.txt must include pytest"
