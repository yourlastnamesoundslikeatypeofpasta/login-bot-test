

def get_payout(package_count, weight_count, item_count, tier, points):
    """
    Calculate logger dollar payout
    :param points:
    :param package_count: float, packages
    :param weight_count: float, weight
    :param item_count: float, items
    :param tier: str, tier
    :return: float, dollar payout
    """
    tier_value_dict = {
        "tier_1": {
            "packages": 0.23,
            "items": 0.07,
            "weight": 0
        },
        "tier_2": {
            "packages": 0.23,
            "items": 0.08,
            "weight": 0
        },
        "tier_3": {
            "packages": 0.26,
            "items": 0.08,
            "weight": 0
        },
        "personal_shopper": {
            "packages": 0.25,
            "items": 0.02,
            "weight": 0
        },
        "special_handling": {
            "packages": 0.08,
            "items": 0.15,
            "weight": 0
        },
        "heavies": {
            "packages": 0.25,
            "items": 0.08,
            "weight": 0.023
        }
    }
    package_value = tier_value_dict[tier]['packages']
    weight_value = tier_value_dict[tier]['weight']
    item_value = tier_value_dict[tier]['items']
    payout_value = (package_value * package_count) + (weight_value * weight_count) + (item_value * item_count)

    # get deduction dollar value
    deduction = 0
    if points:
        if points <= 2:
            deduction = 0
        elif 3 <= points <= 6:
            deduction = 50
        elif 7 <= points <= 9:
            deduction = 100
        elif 10 <= points <= 13:
            deduction = 150
        elif 14 <= points <= 17:
            deduction = 200
        elif 18 <= points <= 21:
            deduction = 250
        elif 22 <= points <= 29:
            deduction = 300
        else:
            payout_value = 0
            return payout_value

    # default payout value to 0 if the deduction is larger
    if deduction > payout_value:
        payout_value = 0
        return payout_value

    payout_value -= deduction
    return payout_value
