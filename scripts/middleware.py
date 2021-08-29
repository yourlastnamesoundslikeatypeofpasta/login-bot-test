from scripts.production_score import get_production_score
from scripts.validate_input import validate_input


def fetch_user(payload, context, next):
    user = payload["user"]
    context['user'] = user
    next()


def fetch_trigger_id(body, context, next):
    trigger_id = body['trigger_id']
    context['trigger_id'] = trigger_id
    next()


def calculate_production_score(view, context, next):
    # values entered
    input_block_values = {
        "block_package": view['state']['values']['block_package']['package_input']['value'].strip(' '),
        "block_weight": view['state']['values']['block_weight']['weight_input']['value'].strip(' '),
        "block_items": view['state']['values']['block_items']['item_input']['value'].strip(' '),
        "block_hours": view['state']['values']['block_hours']['hour_input']['value'].strip(' ')
    }

    # validate input block values
    error_response_action = validate_input(input_block_values)
    if error_response_action:
        # throw validation error if blocks don't meet input req
        context['error_response'] = error_response_action
        next()
        return

    # add stats to context
    context['package_count'] = float(input_block_values['block_package'])
    context['weight_count'] = float(input_block_values['block_weight'])
    context['item_count'] = float(input_block_values['block_items'])
    context['hour_count'] = float(input_block_values['block_hours'])
    context['pkg_per_hour'] = context['package_count'] / context['hour_count']
    context['weight_per_package'] = context['weight_count'] / context['package_count']
    context['items_per_pkg'] = context['item_count'] / context['package_count']
    context['production_score'] = get_production_score(context['package_count'],
                                                       context['weight_count'],
                                                       context['item_count'],
                                                       context['hour_count'])
    next()
