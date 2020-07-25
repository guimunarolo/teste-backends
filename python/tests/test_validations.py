import uuid
from unittest import mock

import pytest

import solution.validations as validations


def obj_factory(quantity=1, **kwargs):
    return {uuid.uuid4(): mock.Mock(**kwargs) for _ in range(0, quantity)}


@pytest.mark.parametrize(
    "loan_value, expexted_result",
    (
        (validations.MIN_LOAN_VALUE - 1, False),
        (validations.MAX_LOAN_VALUE + 1, False),
        (validations.MAX_LOAN_VALUE, True),
        (validations.MIN_LOAN_VALUE, True),
    ),
)
def test_has_valid_loan_value(loan_value, expexted_result, proposal):
    proposal.proposal_loan_value = loan_value

    assert validations.has_valid_loan_value(proposal) is expexted_result


@pytest.mark.parametrize(
    "loan_installments_number, expexted_result",
    (
        (validations.MIN_LOAN_INSTALLMENTS - 1, False),
        (validations.MAX_LOAN_INSTALLMENTS + 1, False),
        (validations.MAX_LOAN_INSTALLMENTS, True),
        (validations.MIN_LOAN_INSTALLMENTS, True),
    ),
)
def test_has_valid_loan_installments_number(loan_installments_number, expexted_result, proposal):
    proposal.proposal_number_of_monthly_installments = loan_installments_number

    assert validations.has_valid_loan_installments_number(proposal) is expexted_result


@pytest.mark.parametrize(
    "proponents_number, expected_result",
    ((validations.MIN_PROPONENTS_QUANTITY, True), (validations.MIN_PROPONENTS_QUANTITY - 1, False),),
)
def test_has_valid_proponents_number(proponents_number, expected_result, proposal):
    proposal.proponents = obj_factory(proponents_number)

    assert validations.has_valid_proponents_number(proposal) is expected_result


@pytest.mark.parametrize(
    "main_proponents_number, expected_result",
    (
        (validations.LIMIT_MAIN_PROPONENTS, True),
        (validations.LIMIT_MAIN_PROPONENTS + 1, False),
        (validations.LIMIT_MAIN_PROPONENTS - 1, False),
    ),
)
def test_has_valid_main_proponents_number(main_proponents_number, expected_result, proposal):
    proposal.proponents = obj_factory(main_proponents_number, proponent_is_main=True)

    assert validations.has_valid_main_proponents_number(proposal) is expected_result


def test_has_proponents_with_valid_age(proposal):
    proposal.proponents = obj_factory(2, proponent_age=validations.MIN_PROPONENTS_AGE)

    assert validations.has_proponents_with_valid_age(proposal) is True

    # add one with smaller age to list of valid ones should invalid all
    proposal.proponents.update(obj_factory(1, proponent_age=validations.MIN_PROPONENTS_AGE - 1))

    assert validations.has_proponents_with_valid_age(proposal) is False


def test_has_valid_warranties_number_and_valid_warranted_value_success(proposal, warranty):
    proposal.proposal_loan_value = 500
    proposal.warranties = obj_factory(2, warranty_value=500, warranty_province="SP")

    assert validations.has_valid_warranties_number_and_valid_warranted_value(proposal) is True


def test_has_valid_warranties_number_and_valid_warranted_value_with_invalid_provinces(proposal, warranty):
    proposal.proposal_loan_value = 500
    invalid_province = validations.NOT_ACCEPTED_WARRANTIES_PROVINCES[0]
    proposal.warranties = obj_factory(2, warranty_value=500, warranty_province=invalid_province)

    assert validations.has_valid_warranties_number_and_valid_warranted_value(proposal) is False


def test_has_valid_warranties_number_and_valid_warranted_value_with_one_invalid_provinces(proposal, warranty):
    proposal.proposal_loan_value = 500
    invalid_province = validations.NOT_ACCEPTED_WARRANTIES_PROVINCES[0]
    proposal.warranties = obj_factory(1, warranty_value=500, warranty_province=invalid_province)
    proposal.warranties.update(obj_factory(1, warranty_value=500, warranty_province="SP"))

    assert validations.has_valid_warranties_number_and_valid_warranted_value(proposal) is False


def test_has_valid_warranties_number_and_valid_warranted_value_with_unsufficient_value(proposal, warranty):
    proposal.proposal_loan_value = 500
    proposal.warranties = obj_factory(2, warranty_value=499.5, warranty_province="SP")

    assert validations.has_valid_warranties_number_and_valid_warranted_value(proposal) is False


def test_has_main_proponent_with_valid_monthly_income_success(proposal):
    for age, multiplier in validations.MIN_MAIN_PROPONENT_INCOME.items():
        value = 5000 * multiplier
        proposal.proposal_loan_value = value
        proposal.proposal_number_of_monthly_installments = multiplier
        proposal.proponents = obj_factory(
            1, proponent_is_main=True, proponent_monthly_income=value, proponent_age=age
        )

        assert validations.has_main_proponent_with_valid_monthly_income(proposal) is True


def test_has_main_proponent_with_valid_monthly_income_fail(proposal):
    for age, multiplier in validations.MIN_MAIN_PROPONENT_INCOME.items():
        value = 5000 * multiplier
        proposal.proposal_loan_value = value
        proposal.proposal_number_of_monthly_installments = multiplier
        proposal.proponents = obj_factory(
            1, proponent_is_main=True, proponent_monthly_income=value - 1, proponent_age=age
        )

        assert validations.has_main_proponent_with_valid_monthly_income(proposal) is False
