import string


def validate_input(b_input_value_dict):
    """
    Validate that input is only numbers and contains one decimal point
    :param b_input_value_dict: dict, production stats
    :return: dict, response action errors
    """

    # check if input is only numbers
    error_block_id_list = []
    numbers = string.digits
    error_str = 'This entry can only contain numbers'
    for block_id, block_stat in b_input_value_dict.items():
        if block_stat.count(".") >= 2:
            error_block_id_list.append((block_id, 'This entry cannot have more than one decimal'))
            continue
        for number in block_stat:
            if number not in numbers and '.' != number:  # let '.' through. Hours might include them
                error_block_id_list.append((block_id, error_str))

    # check if input starts with '0'
    error_str = 'This entry cannot start with 0'
    for block_id, block_stat in b_input_value_dict.items():
        if block_stat.startswith('0'):
            error_block_id_list.append((block_id, error_str))

    # create action response
    if error_block_id_list:
        response_action_temp = {
            "response_action": "errors",
            "errors": {
            }
        }
        for block, error in error_block_id_list:
            response_action_temp['errors'][block] = error
        return response_action_temp
