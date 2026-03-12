"""Tests for the licensing module."""

from unittest.mock import patch

import pytest

from content_forge.licensing import (
    activate_license,
    check_limit,
    get_limits,
    get_status,
    get_tier,
)


@pytest.fixture(autouse=True)
def temp_license_store(tmp_path):
    store = tmp_path / "license.json"
    with patch("content_forge.licensing.LICENSE_STORE", store):
        yield store


def test_first_run_is_trial():
    assert get_tier() == "trial"


def test_trial_has_premium_limits():
    limits = get_limits()
    assert limits["max_words"] is None
    assert limits["humanize"] is True


def test_activate_license():
    ok, _ = activate_license("test-key")
    assert ok is True
    assert get_tier() == "premium"


def test_check_limit_words_free():
    with patch("content_forge.licensing.get_tier", return_value="free"):
        allowed, _ = check_limit("max_words", 300)
        assert allowed is True
        allowed, msg = check_limit("max_words", 1000)
        assert allowed is False


def test_check_limit_content_type_free():
    with patch("content_forge.licensing.get_tier", return_value="free"):
        allowed, _ = check_limit("content_type", "blog_post")
        assert allowed is True
        allowed, _ = check_limit("content_type", "email")
        assert allowed is False


def test_get_status():
    status = get_status()
    assert status["product"] == "content-forge"
    assert "limits" in status
