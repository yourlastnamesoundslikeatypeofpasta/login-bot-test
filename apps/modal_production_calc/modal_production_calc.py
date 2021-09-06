import string

from app import app
from apps.global_middleware import fetch_trigger_id
from apps.global_middleware import calculate_production_score
from slack_sdk.errors import SlackApiError


def fetch_base_view(context, next):
    base_blocks = [
        {
            "type": "input",
            "block_id": "block_packages",
            "element": {
                "type": "plain_text_input",
                "action_id": "package_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "300"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Packages"
            }
        },
        {
            "type": "input",
            "block_id": "block_weight",
            "element": {
                "type": "plain_text_input",
                "action_id": "weight_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "750"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Weight"
            }
        },
        {
            "type": "input",
            "block_id": "block_items",
            "element": {
                "type": "plain_text_input",
                "action_id": "item_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "450"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Items"
            }
        },
        {
            "type": "input",
            "block_id": "block_hours",
            "element": {
                "type": "plain_text_input",
                "action_id": "hour_input",
                "placeholder": {
                    "type": "plain_text",
                    "text": "7.5"
                }
            },
            "label": {
                "type": "plain_text",
                "text": "Hours"
            }
        }
    ]
    base_view = {
        "type": "modal",
        "callback_id": "production_calc_submission",
        "title": {
            "type": "plain_text",
            "text": "Production Calculator"
        },
        "submit": {
            "type": "plain_text",
            "text": "Calculate"
        },
        "blocks": base_blocks
    }
    context['base_blocks'] = base_blocks
    context['base_view'] = base_view
    next()


def get_input_values(context, body, next):
    input_block_values = {
        "block_packages": body['view']['state']['values']['block_packages']['package_input']['value'].strip(' '),
        "block_weight": body['view']['state']['values']['block_weight']['weight_input']['value'].strip(' '),
        "block_items": body['view']['state']['values']['block_items']['item_input']['value'].strip(' '),
        "block_hours": body['view']['state']['values']['block_hours']['hour_input']['value'].strip(' ')
    }
    context['input_block_values'] = input_block_values
    next()


def validate_input(context, next, logger):
    # valid input = starts with digit > 0, all digits, <= 1 decimal
    invalid_block_id_lst = []
    digits = string.digits
    for block_id, block_stat in context['input_block_values'].items():
        if block_stat.count(".") >= 2:  # let 1 '.' through
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
        return
    else:
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
        next()


def create_blocks(context, next):
    if 'response_action' in context:
        next()
        return

    stats = context['stats']
    score = context['score']
    score_block = [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Packages/Hour:* `{stats['pkg_per_hour']:.2f}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Weight/Package:* `{stats['weight_per_pkg']:.2f}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Items/Package:* `{stats['items_per_pkg']:.2f}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Productivity Score:* `{score:.2f}` :dash:"
                },
            ]
        }
    ]
    context['new_block'] = score_block
    next()


def update_view(context, next):
    if 'response_action' in context:
        next()
        return

    # create new view key
    context['view'] = context['base_view']

    # create new blocks key with updated blocks lst
    context['blocks'] = context['base_blocks'] + context['new_block']

    # update new view key to point to new blocks key
    context['view']['blocks'] = context['blocks']
    next()


# root view
@app.action('production_calc_button_click',
            middleware=[fetch_trigger_id, fetch_base_view])
def show_root_view(ack, context, logger):
    ack()
    trigger_id = context['trigger_id']
    view = context['base_view']

    try:
        app.client.views_open(
            trigger_id=trigger_id,
            view=view
        )
    except SlackApiError as e:
        logger.error(e)


# updated view
@app.view("production_calc_submission", middleware=[fetch_base_view, get_input_values,
                                                    validate_input, calculate_production_score,
                                                    create_blocks, update_view])
def show_updated_view(ack, context, logger):
    ack()
    if 'response_action' in context:
        ack(context['response_action'])
    else:
        view = context['view']
        response_action = {
            "response_action": "update",
            "view": view
        }
        try:
            ack(response_action)
        except SlackApiError as e:
            logger.error(e)
