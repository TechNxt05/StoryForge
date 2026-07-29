import os
import sys
from pathlib import Path


def test_python_version() -> None:
    """Verify system is running on Python >= 3.11."""
    assert sys.version_info >= (3, 11), f"Expected Python >= 3.11, got {sys.version}"


def test_workspace_structure() -> None:
    """Verify fundamental directory structure exists."""
    root_dir = Path(__file__).parent.parent.parent
    required_dirs = [
        "apps/web",
        "apps/api",
        "apps/worker",
        "runtime",
        "packages",
        "providers",
        "content-packs",
        "docker",
        "scripts",
        "Documents",
        "EngineeringKit",
    ]
    for rel_dir in required_dirs:
        dir_path = root_dir / rel_dir
        assert dir_path.exists() and dir_path.is_dir(), f"Missing required directory: {rel_dir}"


def test_engineering_kit_files() -> None:
    """Verify EngineeringKit handbook documents exist."""
    root_dir = Path(__file__).parent.parent.parent
    required_handbook_files = [
        "EngineeringKit/MASTER_PROMPT.md",
        "EngineeringKit/AI_AGENT_RULEBOOK.md",
        "EngineeringKit/CODING_STANDARDS.md",
        "EngineeringKit/REVIEW_GUIDELINES.md",
        "EngineeringKit/DEBUG_GUIDELINES.md",
        "EngineeringKit/PERFORMANCE_GUIDELINES.md",
        "EngineeringKit/SECURITY_GUIDELINES.md",
        "EngineeringKit/TESTING_GUIDELINES.md",
        "EngineeringKit/OBSERVABILITY_GUIDELINES.md",
        "Prompts.md",
    ]
    for rel_file in required_handbook_files:
        file_path = root_dir / rel_file
        assert file_path.exists() and file_path.is_file(), f"Missing handbook file: {rel_file}"
