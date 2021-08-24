def get_production_score(pkgs, weight, items, hours):
    """
    Get production score
    :param pkgs: float, package count
    :param weight: float, weight of packages
    :param items: float, items logged in
    :param hours: float, hours worked
    :return: float, production score
    """
    pkg_points = 14.7
    item_points = 2.03
    lbs_points = 0.99
    score = ((pkg_points * pkgs) + (item_points * items) + (lbs_points * weight)) / hours
    return score
