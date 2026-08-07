import pytest

from ml.predictor import calculate_dynamic_threshold


def test_default_profile_uses_base_threshold():
    assert calculate_dynamic_threshold({}) == pytest.approx(0.40)


def test_poor_credit_lowers_threshold():
    threshold = calculate_dynamic_threshold({"cibil": 450, "dti": 0.3, "emis": 0, "income": 1})
    assert threshold == pytest.approx(0.30)


def test_excellent_credit_raises_threshold():
    threshold = calculate_dynamic_threshold({"cibil": 800, "dti": 0.3, "emis": 0, "income": 1})
    assert threshold == pytest.approx(0.50)


def test_high_dti_and_emi_burden_stack_reductions():
    threshold = calculate_dynamic_threshold(
        {"cibil": 600, "dti": 0.7, "emis": 6000, "income": 10000}
    )
    assert threshold == pytest.approx(0.30)


def test_threshold_is_clamped_to_lower_bound():
    threshold = calculate_dynamic_threshold(
        {"cibil": 300, "dti": 0.9, "emis": 9000, "income": 10000}
    )
    assert threshold == pytest.approx(0.20)


def test_threshold_is_clamped_to_upper_bound():
    threshold = calculate_dynamic_threshold({"cibil": 900, "dti": 0.0, "emis": 0, "income": 1})
    assert threshold == 0.50


def test_invalid_values_fall_back_to_defaults():
    threshold = calculate_dynamic_threshold(
        {"cibil": "not-a-number", "dti": None, "emis": "oops", "income": 0}
    )
    assert threshold == 0.40
