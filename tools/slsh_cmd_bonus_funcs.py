def bonus_score(stats):
    """
    Calculate logger score
    :param stats: dict, contains {stat:float}
    :return: float, logger score
    """
    pkg_points = 14.7
    item_points = 2.03
    lbs_points = 0.99
    score = ((pkg_points * stats['packages']) + (item_points * stats['items']) + (lbs_points * stats['lbs'])) / stats[
        'hours']
    return score


def find_stats(bare_text):
    """
    Split text, convert to floats, and attach each float to a stat in dict.
    :param bare_text: str, un-split str of int
    :return: dict, logger stats
    """
    len_bare_text = len(bare_text.split(' '))
    if len_bare_text < 4 or len_bare_text > 4:  # make sure the exact num of vars is 4
        return
    try:
        text_lst = [float(i) for i in bare_text.split(' ')]
    except ValueError:  # User may have entered in a letter in their number
        return

    if text_lst:
        stat_dict = {'packages': text_lst[0],
                     'lbs': text_lst[1],
                     'items': text_lst[2],
                     'hours': text_lst[3]}
        return stat_dict
