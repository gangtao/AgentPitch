"""StorageConfig Pydantic model for HTTP validation."""
from __future__ import annotations
import os
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StorageConfig(BaseModel):
    """Storage configuration for data home path validation."""

    model_config = ConfigDict(frozen=True)

    data_home: str = Field(min_length=1, description="Path to data directory")

    @field_validator('data_home')
    @classmethod
    def validate_data_home_field(cls, v: str) -> str:
        """Validate data_home field using the helper function."""
        # Use the helper function to validate and get the resolved path
        resolved_path = validate_data_home(v)
        # Return the original string value (not the Path object)
        return v


def validate_data_home(path: str) -> Path:
    """Validate and resolve a data home path.

    Args:
        path: Path string to validate

    Returns:
        Resolved Path object if valid

    Raises:
        ValueError: If path is invalid (contains .., not writable, etc.)
    """
    if not path.strip():
        raise ValueError("Path cannot be empty")

    # Check for .. in path components (security risk)
    if '..' in Path(path).parts:
        raise ValueError("Path may not contain \"..\"")

    # Resolve the path
    try:
        resolved = Path(path).expanduser().resolve()
    except Exception as e:
        raise ValueError(f"Invalid path: {e}")

    # Check if path exists and is a directory, or can be created.
    # PermissionError can be raised by exists()/is_dir()/access() when the
    # path is inside an unreadable parent — treat as not-writable.
    try:
        if resolved.exists():
            if not resolved.is_dir():
                raise ValueError("Path exists but is not a directory")
            if not os.access(resolved, os.W_OK):
                raise ValueError("Path is not writable")
        else:
            parent = resolved.parent
            if not parent.exists():
                raise ValueError("Parent directory does not exist")
            if not os.access(parent, os.W_OK):
                raise ValueError("Cannot create directory - parent not writable")
    except PermissionError:
        raise ValueError("Path is not accessible (permission denied)")

    return resolved