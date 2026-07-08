from composition_engine.compatibility import check_version_constraint


def test_exact_match():
    assert check_version_constraint("1.2.3", "1.2.3")[0] is True


def test_exact_mismatch():
    ok, msg = check_version_constraint("1.2.4", "1.2.3")
    assert ok is False
    assert msg is not None


def test_caret_same_major_allows_higher_minor():
    assert check_version_constraint("1.5.0", "^1.2.0")[0] is True


def test_caret_different_major_fails():
    assert check_version_constraint("2.0.0", "^1.2.0")[0] is False


def test_tilde_locks_minor():
    assert check_version_constraint("1.2.9", "~1.2.0")[0] is True
    assert check_version_constraint("1.3.0", "~1.2.0")[0] is False


def test_gte_lte_operators():
    assert check_version_constraint("2.0.0", ">=1.0.0")[0] is True
    assert check_version_constraint("0.9.0", ">=1.0.0")[0] is False
    assert check_version_constraint("1.0.0", "<=1.0.0")[0] is True


def test_invalid_version_format():
    ok, msg = check_version_constraint("not-a-version", "^1.0.0")
    assert ok is False
    assert "Invalid" in msg