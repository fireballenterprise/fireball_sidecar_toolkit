"""Tests for common utilities."""

from pathlib import Path

import pytest
from modules.toolkit.common import utils

pytestmark = pytest.mark.common


def test_create_slug():
    """Test slug creation from text."""
    assert utils.create_slug("Hello World") == "hello_world"
    assert utils.create_slug("Test-Case") == "test-case"
    assert utils.create_slug("Special!@#$%Characters") == "specialcharacters"
    assert utils.create_slug("Multiple   Spaces") == "multiple_spaces"


def test_get_topic_path():
    """Test extracting topic path from directory."""
    test_path = Path("/Users/test/repo/topics/workshop/3d_printing")
    result = utils.get_topic_path(test_path)
    assert result == "workshop/3d_printing"


def test_get_topic_path_invalid():
    """Test that invalid path raises error."""
    test_path = Path("/Users/test/not_in_topics/")
    with pytest.raises(SystemExit):
        utils.get_topic_path(test_path)


def test_validate_topics_directory_valid():
    """Test validating a valid topics directory."""
    test_path = Path("/Users/test/repo/topics/business")
    result = utils.validate_topics_directory(test_path)
    assert result == test_path


def test_validate_topics_directory_invalid():
    """Test validating an invalid directory."""
    test_path = Path("/Users/test/repo/not_topics")
    with pytest.raises(SystemExit):
        utils.validate_topics_directory(test_path)
