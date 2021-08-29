import os
import sqlite3
from pprint import pprint
import re
import random

from copy import deepcopy
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from scripts.command_score import bonus_score
from scripts.command_score import find_stats
from scripts.base_views import production_calc_base_view
from scripts.validate_input import validate_input
from scripts.get_payout import get_payout
from scripts.production_score import get_production_score
from scripts.get_error_msg_str import get_error_msg_str
from scripts.base_views import build_options
from scripts.db import *
from scripts.mistake import Mistake
from scripts.views import *
from scripts.middleware import *

# start Slack app
app = App(token=os.environ['bot_token'], signing_secret=os.environ['signin_secret'])
BOT_ID = app.client.auth_test()['user_id']


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Slack App Modals and Views@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# ##############################################Home View###############################################################
@app.event("app_home_opened", middleware=[fetch_user])
def app_home_root_view(context, logger):
    """
    Show home buttons
    :param context:
    :param logger: logger
    :return: None
    """
    show_home_buttons_view(app, SlackApiError, context, logger)


# ######################################Productivity Score Calculator Modal#############################################
@app.action('productivity_score_calculator_button_click')
def productivity_score_calculator_root_view(ack, body, logger):
    """
    Open production score calculator when "Production Calculator" is clicked
    :param logger:
    :param ack: slack obj
    :param body: slack obj, https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html#slack_bolt.kwargs_injection.args.Args.action
    :return: None
    """
    ack()
    trigger_id = body['trigger_id']
    try:
        # open score input field view
        app.client.views_open(
            trigger_id=trigger_id,
            view=production_calc_base_view
        )
    except SlackApiError as e:
        logger.info(f'Error creating view: {e}')


@app.view("calc_score_modal")
def get_stats_update_calc_score_modal(ack, view, logger):
    """
    Updated production score calculator modal.
    :param logger: logger obj
    :param ack: slack obj
    :param view: slack obj
    :return: None
    """
    ack()
    block_values = {
        "block_package": view['state']['values']['block_package']['package_input']['value'].strip(' '),
        "block_weight": view['state']['values']['block_weight']['weight_input']['value'].strip(' '),
        "block_items": view['state']['values']['block_items']['item_input']['value'].strip(' '),
        "block_hours": view['state']['values']['block_hours']['hour_input']['value'].strip(' ')
    }
    error_response_action = validate_input(block_values)
    if error_response_action:
        ack(error_response_action)
        return
    try:
        package_count = float(block_values['block_package'])
        weight_count = float(block_values['block_weight'])
        item_count = float(block_values['block_items'])
        hour_count = float(block_values['block_hours'])
        pkg_per_hour = package_count / hour_count
        weight_per_package = weight_count / package_count
        items_per_pkg = item_count / package_count
        production_score = get_production_score(package_count, weight_count, item_count, hour_count)

        view_update_blocks = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Packages* :package:: `{package_count:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weight* :weight_lifter:: `{weight_count:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items* :shopping_trolley:: `{item_count:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Hours* :clock1:: `{hour_count:.2f}`"
                    },
                ],
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Packages/Hour*: `{pkg_per_hour:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weight/Package*: `{weight_per_package:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items/Package*: `{items_per_pkg:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Productivity Score:* `{production_score:.2f}` :dash:"
                    },
                ]
            }
        ]
        view_update = deepcopy(production_calc_base_view)
        for block in view_update_blocks:
            view_update['blocks'].append(block)

        ack({
            "response_action": "update",
            "view": view_update
        })
    except (SlackApiError, ValueError) as e:
        print(e)
        logger.info(e)


# #########################################Piece Pay Calculator Modal###################################################

def piece_pay_calc_root_view(ack, body, context, logger, view):
    """
    Open piece pay calculator when "Piece Pay Calculator" is clicked
    :param mistake:
    :param ack: slack obj
    :param body: slack obj
    :param logger: slack obj
    :return: None
    """
    # Set mistake value
    trigger_id = body['trigger_id']
    mistake_points = context['mistake_points']
    piece_pay_calc_base_view = {
        "type": "modal",
        "callback_id": "calc_piecepay_modal",
        "title": {
            "type": "plain_text",
            "text": "Piece Pay Calculator"
        },
        "submit": {
            "type": "plain_text",
            "text": "Calculate"
        },
        "clear_on_close": True,
        "blocks": [
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
                        "text": "Select a tier...",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Tier 1",
                                "emoji": True
                            },
                            "value": "tier_1"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Tier 2",
                                "emoji": True
                            },
                            "value": "tier_2"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Tier 3",
                                "emoji": True
                            },
                            "value": "tier_3"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Personal Shopper",
                                "emoji": True
                            },
                            "value": "personal_shopper"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Special Handling",
                                "emoji": True
                            },
                            "value": "special_handling"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Heavies",
                                "emoji": True
                            },
                            "value": "heavies"
                        }
                    ],
                    "action_id": "static_select-action"
                },
                "label": {
                    "type": "plain_text",
                    "text": "Tier",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Mistake Points _(optional)_: {mistake_points}"
                },
                "accessory": {
                    "type": "button",
                    "action_id": "add_mistakes_button_click",
                    "text": {
                        "type": "plain_text",
                        "text": "Add Mistake",
                    },
                    "style": "danger"
                }
            }

        ],
    }
    clear_mistake_block = {
        "block_id": "block_clear_mistake_button",
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": " "
        },
        "accessory": {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Clear Mistakes",
                "emoji": True
            },
            "action_id": "clear_mistakes",
        }
    }
    # TODO: Add blocks to separate dir, and files
    try:
        if context['calculate'] and mistake_points:
            score_blocks = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Packages* :package:: `{context['package_count']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weight* :weight_lifter:: `{context['weight_count']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items* :shopping_trolley:: `{context['item_count']:.2f}`"
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
            piece_pay_calc_base_view['blocks'].append(clear_mistake_block)
            piece_pay_calc_base_view['blocks'].append(score_blocks)
            ack({
                "response_action": "update",
                "view": piece_pay_calc_base_view
            })
        elif context['calculate']:
            score_blocks = {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Packages* :package:: `{context['package_count']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weight* :weight_lifter:: `{context['weight_count']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items* :shopping_trolley:: `{context['item_count']:.2f}`"
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
            piece_pay_calc_base_view['blocks'].append(score_blocks)
            ack({
                "response_action": "update",
                "view": piece_pay_calc_base_view
            })
        elif context['mistakes_cleared']:
            app.client.views_update(
                view_id=body['view']['root_view_id'],
                view=piece_pay_calc_base_view,
            )
        elif mistake_points:
            piece_pay_calc_base_view['blocks'].append(clear_mistake_block)
            app.client.views_update(
                view_id=body['view']['root_view_id'],
                view=piece_pay_calc_base_view,
            )
        else:
            app.client.views_open(
                trigger_id=trigger_id,
                view=piece_pay_calc_base_view,
            )
    except SlackApiError as e:
        logger.info(f'Error creating view: {e}')


@app.action("piece_pay_home_button")
def piece_pay_calc(ack, body, context, logger, view):
    """
    Open piece pay calculator when "Piece Pay Calculator" is clicked
    :param ack: slack obj
    :param body: slack obj
    :param logger: slack obj
    :return: None
    """
    ack()
    piece_pay_calc.mistake = Mistake()
    context['mistakes_cleared'] = False
    context['calculate'] = False
    context['mistake_points'] = 0
    piece_pay_calc_root_view(ack, body, context, logger, view)


@app.action('add_mistakes_button_click')
def open_mistake_view(ack, body, context):
    ack()
    context['mistakes_cleared'] = False
    context['calculate'] = False
    trigger_id = body['trigger_id']
    blocks = [{
        "type": "input",
        "block_id": "block_mistake_static_select",
        "label": {
            "type": "plain_text",
            "text": "Select Mistake",
        },
        "element": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select Mistake..."
            },
            "action_id": "action_static_mistake",
            "options": build_options(mistake_values)
        }
    }]
    try:
        app.client.views_push(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "piece_pay_home_button_click",
                "title": {
                    "type": "plain_text",
                    "text": "Select Mistakes"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Add Mistakes",
                },
                "close": {
                    "type": "plain_text",
                    "text": "Close",
                },
                "blocks": blocks
            },
        )
    except SlackApiError as e:
        print(e.response)


@app.view('piece_pay_home_button_click')
def open_piece_pay_view_with_mistakes(ack, body, context, payload, logger, view):
    ack()
    mistake = piece_pay_calc.mistake
    context['calculate'] = False
    context['mistakes_cleared'] = False
    mistake_code = \
        payload['state']['values']['block_mistake_static_select']['action_static_mistake']['selected_option'][
            'value']
    mistake.add_mistake(mistake_code)
    context['mistake_points'] = mistake.get_mistake_points()
    return piece_pay_calc_root_view(ack, body, context, logger, view)


@app.action("clear_mistakes")
def clear_mistake_points_from_root_view(ack, body, context, logger, view, payload):
    ack()
    piece_pay_calc.mistake.remove_all_mistakes()
    context['mistake_points'] = piece_pay_calc.mistake.get_mistake_points()
    context['mistakes_cleared'] = True
    context['calculate'] = False
    piece_pay_calc_root_view(ack, body, context, logger, view)


@app.view("calc_piecepay_modal")
def get_stats_update_calc_piecepay_modal(ack, view, context, payload, body, logger):
    """
    Updated piece pay calculator modal
    :param ack: slack obj
    :param view: slack obj
    :param body: slack obj
    :return: None
    """
    ack()
    context['mistakes_cleared'] = False
    context['calculate'] = True
    context['mistake_points'] = piece_pay_calc.mistake.get_mistake_points()
    block_input_values = {
        "block_package": view['state']['values']['block_package']['package_input']['value'].strip(' '),
        "block_weight": view['state']['values']['block_weight']['weight_input']['value'].strip(' '),
        "block_items": view['state']['values']['block_items']['item_input']['value'].strip(' '),
    }
    error_response_action = validate_input(block_input_values)
    if error_response_action:
        ack(error_response_action)
        return

    try:
        context['package_count'] = float(block_input_values['block_package'])
        context['weight_count'] = float(block_input_values['block_weight'])
        context['item_count'] = float(block_input_values['block_items'])
        context['tier'] = view['state']['values']['block_tier']['static_select-action']['selected_option']['text'][
            'text']
        context['tier_value'] = view['state']['values']['block_tier']['static_select-action']['selected_option'][
            'value']
        try:
            context['payout'] = get_payout(context['package_count'],
                                           context['weight_count'],
                                           context['item_count'],
                                           context['tier_value'],
                                           mistake_points=context['mistake_points'])
        except KeyError:
            context['payout'] = get_payout(context['package_count'],
                                           context['weight_count'],
                                           context['item_count'],
                                           context['tier_value'])
    except (SlackApiError, ValueError) as e:
        print(e)
        logger.info(e)

    # pick age emoji :)
    if context['tier_value'] == 'tier_1':
        context['tier_emoji'] = ':baby:'
    elif context['tier_value'] == 'tier_2':
        context['tier_emoji'] = ':child:'
    elif context['tier_value'] == 'tier_3':
        context['tier_emoji'] = ':older_man:'
    else:
        context['tier_emoji'] = ''

    piece_pay_calc_root_view(ack, body, context, logger, view)


# #########################################Appeal Mistake Modal#########################################################
@app.action("appeal_mistake_button_click")
def appeal_mistake_button_click(ack, body, logger):
    """
    Open appeal mistake modal when "Appeal Mistake" is clicked
    :param ack: slack obj
    :param body: slack obj
    :return: None
    """
    ack()
    trigger_id = body['trigger_id']
    try:
        app.client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "appeal_mistake_modal",
                "title": {
                    "type": "plain_text",
                    "text": "Mistake Appeal"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit"
                },
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "plain_text_input-action",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "02-415-0338"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Package Id",
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "plain_text_input-action",
                            "max_length": 250,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter a brief description..."
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Brief Description",
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "block_mistake",
                        "label": {
                            "type": "plain_text",
                            "text": "Mistake code",
                        },
                        "element": {
                            "action_id": "text1234",
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select mistake code..."
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "DE"
                                    },
                                    "value": "value-1"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "DE2"
                                    },
                                    "value": "value-2"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "QD"
                                    },
                                    "value": "value-3"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "PH2"
                                    },
                                    "value": "value-4"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "MI"
                                    },
                                    "value": "value-5"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "MI2"
                                    },
                                    "value": "value-6"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "WA"
                                    },
                                    "value": "value-6"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "CM"
                                    },
                                    "value": "value-7"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "DG MAJ"
                                    },
                                    "value": "value-8"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "UTL"
                                    },
                                    "value": "value-9"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "LABEL"
                                    },
                                    "value": "value-10"
                                }
                            ]
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "block_supervisor",
                        "label": {
                            "type": "plain_text",
                            "text": "Shift",
                        },
                        "element": {
                            "action_id": "text1234",
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select shift..."
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "1st Shift"
                                    },
                                    "value": "first_shift"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "2nd Shift"
                                    },
                                    "value": "second_shift"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "3rd Shift"
                                    },
                                    "value": "third_shift"
                                },
                            ]
                        }
                    },
                ]
            }
        )
    except SlackApiError as e:
        logger.info(e)
        print(e)


@app.view("appeal_mistake_modal")
def appeal_mistake_modal(ack, view, body):
    """
        Updated appeal mistake modal
        :param ack: slack obj
        :param view: slack obj
        :param body: slack obj
        :return: None
        """
    ack()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Message Reacts@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.message(re.compile("(hi|hello|hey|yo)"))
def say_hello(message, say):
    greeting_lst = ['hello', 'hi', 'whats up', 'yo']
    greeting = random.choice(greeting_lst)
    user = message['user']
    say(f'{greeting} <@{user}>!✌')


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Slash Commands@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.command('/bonus')
def bonus(ack, respond, command):
    """
    Slash command that calculates logger bonus.
    :input int, 4, each int is a statistic
    :output str, formatted bonus report
    :param ack: Something something server acknowledge thingy
    :param respond: slack respond func
    :param command: dict, payload
    :return: None
    """

    ack()
    command_name = 'bonus'
    user = command['user_id']

    try:
        text = command['text']
    except KeyError:  # if the user enters whitespace
        respond(get_error_msg_str(command_name))
        return

    # if a user needs help using the slack command
    if text.strip(' ') == 'help':
        respond(
            'Enter stats in this format (with spaces in between each stat): `/bonus [pkgs] [lbs] [items] [hours]`\n example: `/bonus 100 200 175 5`')
        return

    # print out stat report
    stat_dict = find_stats(text)
    if stat_dict:
        logger_bonus_score = bonus_score(stat_dict)
        pkg_per_hour = stat_dict['packages'] / stat_dict['hours']
        lbs_per_pkg = stat_dict['lbs'] / stat_dict['packages']
        items_per_pkg = stat_dict['items'] / stat_dict['packages']
        respond(
            f'<@{user}>\n- Packages :package:: `{stat_dict["packages"]}`\n- Lbs :weight_lifter:: `{stat_dict["lbs"]}`\n- Items :shopping_trolley:: `{stat_dict["items"]}`\n- Hours :clock1:: `{stat_dict["hours"]}`\n\n- Pkg/Hour: `{pkg_per_hour}`\n- Lbs/Pkg: `{lbs_per_pkg}`\n- Items/Pkg: `{items_per_pkg}`\n\n- Estimated Productivity Score: `{logger_bonus_score:.2f}` :dash:')
    else:
        respond(get_error_msg_str(command_name))


if __name__ == '__main__':
    # create_db()
    app.start(port=3000)
