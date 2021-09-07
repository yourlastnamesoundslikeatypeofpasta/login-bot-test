from string import digits


def fetch_user_id(payload, context, next, logger):
    if 'user' in payload:
        user = payload['user']
        context['user'] = user
    elif 'user_id' in payload:
        user = payload['user_id']
        context['user'] = user
    else:
        logger.error('User not found in payload')
    next()


def fetch_trigger_id(body, context, next):
    trigger_id = body['trigger_id']
    context['trigger_id'] = trigger_id
    next()


def fetch_root_id(body, context, next):
    context['root_view_id'] = body['view']['root_view_id']
    next()


def calculate_production_score(context, next):
    # set the points that each stat is worth
    if 'response_action' not in context and 'input_block_values' in context:
        # convert input values to floats and add values to context
        for key, value in context['input_block_values'].items():
            context[key] = float(value)
        stats = {
            'packages': context['block_packages'],
            'weight': context['block_weight'],
            'items': context['block_items'],
            'hours': context['block_hours'],
            'pkg_per_hour': context['block_packages'] / context['block_hours'],
            'weight_per_pkg': context['block_weight'] / context['block_packages'],
            'items_per_pkg': context['block_items'] / context['block_packages']
        }
        context['stats'] = stats
        pkg_points = 14.7
        item_points = 2.03
        weight_points = 0.99

        score = ((pkg_points * stats['packages']) + (item_points * stats['items']) + (
                weight_points * stats['weight'])) / stats['hours']
        context['score'] = score
        next()
    else:
        next()


def validate_input(context, next, logger):
    if 'input_block_values' in context:
        # valid input = starts with digit > 0, all digits, <= 1 decimal
        invalid_block_id_lst = []
        for block_id, block_stat in context['input_block_values'].items():
            if block_stat.count(".") > 1:  # let 1 '.' through
                invalid_block_id_lst.append((block_id, 'This entry cannot have more than one decimal'))
                continue
            elif block_stat[0] not in digits[1:]:
                # skip block hours, user may enter '0.5' hours
                if block_id == 'block_hours':
                    pass
                else:
                    invalid_block_id_lst.append((block_id, 'This entry must start with a positive number'))
                    continue
            # check all string indexes
            for number in block_stat:
                if number not in digits and '.' != number:  # hours may include a decimal
                    invalid_block_id_lst.append((block_id, 'This entry can only contain numbers'))

        # create action response, send response action if inputs are invalid
        if invalid_block_id_lst:
            logger.debug('invalid blocks')
            response_action = {
                "response_action": "errors",
                "errors": {}
            }
            for block, error in invalid_block_id_lst:
                response_action['errors'][block] = error
            context['response_action'] = response_action
            next()
    next()
