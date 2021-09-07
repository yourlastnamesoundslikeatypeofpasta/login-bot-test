import time
import logging

from app import app
from slack_sdk.errors import SlackApiError
from apps.global_middleware import fetch_root_id
from apps.global_middleware import fetch_trigger_id
from apps.global_middleware import validate_input


def fetch_options():
    mistake_values = {
        'flex': 0,
        'batt min': 0,
        'pp': 0,
        'packg': 0,
        'we': 1,
        'de': 2,
        'packg2': 2,
        'de2': 2,
        'ph2': 2,
        'lu': 2,
        'pp2': 2,
        'osd': 4,
        'hk': 4,
        'da': 4,
        'l-ph': 4,
        'item': 4,
        'tw': 4,
        'upc': 4,
        'psl': 4,
        'ms': 4,
        'fsp': 4,
        'mi': 4,
        'ph4': 4,
        'sn': 4,
        'qd': 4,
        'ps': 5,
        'ml': 7,
        'wn': 7,
        'sh': 8,
        'fpp': 8,
        'fxr': 12,
        'fmd': 12,
        'ffw': 12,
        'fdg': 12,
        'batt maj': 12,
        'in': 18,
        'la': 18,
        'wa': 18,
        'cm': 22,
        'utl': 25,
    }
    options_lst = []
    for mistake_code, point_value in mistake_values.items():
        options_lst.append({
            "text": {
                "type": "plain_text",
                "text": f"{mistake_code.upper()} ({point_value} pts)"
            },
            "value": f"{mistake_code}_{point_value}"
        }
        )
    return options_lst


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


def get_tier_emoji(tier_value):
    # choose emoji according to tier
    if tier_value == 'tier_1':
        return ':baby:'
    elif tier_value == 'tier_2':
        return ':child:'
    elif tier_value == 'tier_3':
        return ':older_man:'
    else:
        return ''


def fetch_points(body, context, next):
    # check if the previous view was home view
    is_home_view = body['view']['type'] == 'home'
    if is_home_view:
        # set points
        context['points'] = "0"
        next()
    else:
        points = body['view']['private_metadata']
        context['points'] = points
        next()


def add_points(body, context, next):
    current_points = int(context['points'])

    slctd_mistake = \
        body['view']['state']['values']['block_mistake_static_select']['mistake_selection']['selected_option'][
            'value']
    slctd_mistake_point_value = int(slctd_mistake.split("_")[1])  # see fetch_options() for value structure
    context['points'] = str(current_points + slctd_mistake_point_value)
    next()


def clear_points(context, next):
    context["points"] = "0"
    next()


def create_points_block(context, next):
    points = context['points']
    points_block = {
        "type": "section",
        "block_id": "block_points_and_clear",
        "text": {
            "type": "mrkdwn",
            "text": f"Mistake Points: {points}"
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Clear Points",
            },
            "action_id": "clear_points"
        }
    }
    context['points_block'] = points_block
    next()


def create_payout_block(context, next):
    tier_value = context['tier_value']
    tier_emoji = get_tier_emoji(tier_value)
    score_block = {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*Packages* :package:: `{context['package_count']}`",
            },
            {
                "type": "mrkdwn",
                "text": f"*Weight* :weight_lifter:: `{context['weight_count']}`"
            },
            {
                "type": "mrkdwn",
                "text": f"*Items* :shopping_trolley:: `{context['item_count']}`"
            },
            {
                "type": "mrkdwn",
                "text": f"*Tier* {tier_emoji}: `{context['tier']}`"
            },
            {
                "type": "mrkdwn",
                "text": f"*Payout:moneybag::* `{context['payout']:.2f}`"
            },
        ],
    }
    context['score_block'] = score_block
    next()


def fetch_base_view(context, next):
    points = context['points']
    points_block = context['points_block']
    options = fetch_options()
    base_blocks = [
        {
            "type": "input",
            "block_id": "block_package",
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
            "block_id": "block_tier",
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a tier",
                },
                "action_id": "static_tier_select",
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 1",
                        },
                        "value": "tier_1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 2",
                        },
                        "value": "tier_2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 3",
                        },
                        "value": "tier_3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "P.S.",
                        },
                        "value": "personal_shopper"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "S.H.",
                        },
                        "value": "special_handling"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Heavies",
                        },
                        "value": "heavies"
                    }
                ],
            },
            "label": {
                "type": "plain_text",
                "text": "Pick a tier from the dropdown list",
            },
        },
        {
            "type": "section",
            "block_id": "block_mistake_static_select",
            "text": {
                "type": "mrkdwn",
                "text": "Pick a mistake _(optional)_:"
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select mistake",
                },
                "options": options,
                "action_id": "mistake_selection"
            }
        },
        points_block,
    ]
    base_view = {
        "type": "modal",
        "callback_id": "piece_pay_calc_calculate",
        "private_metadata": points,
        "title": {
            "type": "plain_text",
            "text": "Piece Pay Calculator"
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


def update_base_view(context, next):
    next()


def get_input_values(context, next):
    next()


def calculate_payout(body, context, next):
    # get stats
    package_count = body['view']['state']['values']['block_package']['package_input']['value']
    weight_count = body['view']['state']['values']['block_weight']['weight_input']['value']
    item_count = body['view']['state']['values']['block_items']['item_input']['value']
    tier = body['view']['state']['values']['block_tier']['static_tier_select']['selected_option']['text']['text']
    tier_value = body['view']['state']['values']['block_tier']['static_tier_select']['selected_option']['value']

    # add stats to context
    context['package_count'] = package_count
    context['weight_count'] = weight_count
    context['item_count'] = item_count
    context['tier'] = tier
    context['tier_value'] = tier_value

    # calculate payout and add to context
    package_count = float(package_count)
    weight_count = float(weight_count)
    item_count = float(item_count)
    points = int(context['points'])
    payout = get_payout(package_count, weight_count, item_count, tier_value, points)
    context["payout"] = payout
    next()


# root view
@app.action("piece_pay_home_button", middleware=[fetch_trigger_id,
                                                 fetch_points,
                                                 create_points_block,
                                                 fetch_base_view,
                                                 ])
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


# update mistake points
@app.action("mistake_selection", middleware=[fetch_root_id,
                                             fetch_points,
                                             add_points,
                                             create_points_block,
                                             fetch_base_view,
                                             ])
def update_block_points(ack, context, logger):
    ack()
    root_view_id = context['root_view_id']
    view = context['base_view']
    try:
        app.client.views_update(
            view_id=root_view_id,
            view=view
        )
    except SlackApiError as e:
        logger.error(e)


# update mistake points to 0
@app.action("clear_points", middleware=[fetch_root_id,
                                        fetch_points,
                                        clear_points,
                                        create_points_block,
                                        fetch_base_view,
                                        ])
def remove_mistake_block(ack, context, logger):
    ack()
    root_view_id = context['root_view_id']
    view = context['base_view']
    try:
        app.client.views_update(
            view_id=root_view_id,
            view=view
        )
    except SlackApiError as e:
        logger.error(e)


# calculate piece pay with or without mistake points
@app.view("piece_pay_calc_calculate", middleware=[fetch_points,
                                                  get_input_values,
                                                  validate_input,  # todo: work on merging with global middleware
                                                  create_points_block,
                                                  calculate_payout,
                                                  create_payout_block,
                                                  fetch_base_view,
                                                  update_base_view, ])
def piece_pay_calc_show_results_view(ack, context, logger):
    ack()
    response_action = context

    def piece_pay_calc_view(app, slackapierror, context, logger, ack=None):

        if 'error_response' in context:
            # validation error view
            error_response_action = context['error_response']
            try:
                ack(error_response_action)
            except slackapierror as e:
                logger.error(f'Error creating view: {e}')
        elif 'payout' in context:
            # update view and modal with payout and points
            score_block = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Packages* :package:: `{context['package_count']}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weight* :weight_lifter:: `{context['weight_count']}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items* :shopping_trolley:: `{context['item_count']}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Tier* {context['tier_emoji']}: `{context['tier']}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Payout:moneybag::* `{context['payout']:.2f}`"
                    },
                ],
            }
            view['private_metadata'] = context['points']
            blocks.append(score_block)
            response_action = {
                "response_action": "update",
                "view": view
            }
            ack = context['ack']
            ack(response_action)
        elif int(context['points']) > 0:
            # update private_metadata
            view["private_metadata"] = context['points']

            # update view
            app.client.views_update(
                view_id=context['root_view_id'],
                view=view
            )
        elif 'points_cleared' in context:
            # update private metadata
            view["private_metadata"] = context['points']

            # update view
            app.client.views_update(
                view_id=context['root_view_id'],
                view=view
            )
        else:
            try:
                # open root view
                trigger_id = context['trigger_id']
                app.client.views_open(
                    trigger_id=trigger_id,
                    view=view,
                )
            except slackapierror as e:
                logger.error(f'Error creating view: {e}')
            except KeyError:
                # if a user selects a mistake with a value of 0
                try:
                    app.client.views_update(
                        view_id=context['root_view_id'],
                        view=view
                    )
                except slackapierror as e:
                    logger.error(f'Error creating view: {e}')
