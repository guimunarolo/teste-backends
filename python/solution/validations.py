MAX_LOAN_VALUE = 3000000.0
MIN_LOAN_VALUE = 30000.0

MAX_LOAN_INSTALLMENTS = 180
MIN_LOAN_INSTALLMENTS = 24

LIMIT_MAIN_PROPONENTS = 1
MIN_PROPONENTS_QUANTITY = 2
MIN_PROPONENTS_AGE = 18
MIN_MAIN_PROPONENT_INCOME = {
    # AGE / LOAN PORTION MULTIPLIER
    51: 2,
    24: 3,
    18: 4,
}

MIN_WARRANTIES_QUANTITY = 1
NOT_ACCEPTED_WARRANTIES_PROVINCES = ("PR", "SC", "RS")


def has_valid_loan_value(proposal):
    return MIN_LOAN_VALUE <= proposal.proposal_loan_value <= MAX_LOAN_VALUE


def has_valid_loan_installments_number(proposal):
    return MIN_LOAN_INSTALLMENTS <= proposal.proposal_number_of_monthly_installments <= MAX_LOAN_INSTALLMENTS


def has_valid_proponents_number(proposal):
    return len(proposal.proponents) >= MIN_PROPONENTS_QUANTITY


def has_valid_main_proponents_number(proposal):
    main_proponents = [
        proponent for _, proponent in proposal.proponents.items() if proponent.proponent_is_main
    ]
    return len(main_proponents) == LIMIT_MAIN_PROPONENTS


def has_proponents_with_valid_age(proposal):
    return all(
        [proponent.proponent_age >= MIN_PROPONENTS_AGE for _, proponent in proposal.proponents.items()]
    )


def has_valid_warranties_number_and_valid_warranted_value(proposal):
    accepted_warranties = [
        warranty
        for _, warranty in proposal.warranties.items()
        if warranty.warranty_province not in NOT_ACCEPTED_WARRANTIES_PROVINCES
    ]
    if not len(accepted_warranties) >= MIN_WARRANTIES_QUANTITY:
        return False

    warranted_value = sum([warranty.warranty_value for warranty in accepted_warranties])

    return warranted_value >= (proposal.proposal_loan_value * 2)


def has_main_proponent_with_valid_monthly_income(proposal):
    main_proponent = [
        proponent for _, proponent in proposal.proponents.items() if proponent.proponent_is_main
    ]
    main_proponent = main_proponent[0]

    for age_limit, multiplier in MIN_MAIN_PROPONENT_INCOME.items():
        if main_proponent.proponent_age >= age_limit:
            loan_portion_multiplier = multiplier
            break

    loan_monthly_portion = proposal.proposal_loan_value / proposal.proposal_number_of_monthly_installments

    return main_proponent.proponent_monthly_income >= (loan_monthly_portion * loan_portion_multiplier)
