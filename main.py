import os
import sqlite3
from pprint import pprint
import re
import random

from slack_bolt import App
from slack_sdk.errors import SlackApiError

from scripts.command_score import bonus_score
from scripts.command_score import find_stats
from scripts.get_payout import get_payout
from scripts.get_error_msg_str import get_error_msg_str
from scripts.db import *
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
# root view
@app.action('productivity_score_calculator_button_click', middleware=[fetch_trigger_id])
def productivity_score_calculator_root_view(ack, context, logger):
    """
    Open production score calculator when "Production Calculator" is clicked
    :param context:
    :param logger:
    :param ack: slack obj
    :param body: slack obj, https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html#slack_bolt.kwargs_injection.args.Args.action
    :return: None
    """
    ack()
    show_productivity_calc_view(app, SlackApiError, context, logger)


# updated view
@app.view("productivity_score_calculator_view_submission", middleware=[calculate_production_score])
def productivity_score_calculator_update_root_view(ack, context, logger):
    """
    Updated production score calculator modal.
    :param context:
    :param logger: logger obj
    :param ack: slack obj
    :param view: slack obj
    :return: None
    """
    ack()
    show_productivity_calc_view(app, SlackApiError, context, logger, ack=ack)


# #########################################Piece Pay Calculator Modal###################################################
# root view
@app.action("piece_pay_home_button", middleware=[fetch_trigger_id, fetch_root_id])
def piece_pay_calc_root_view(ack, context, logger):
    """
    Open piece pay calculator when "Piece Pay Calculator" is clicked
    :param view:
    :param context:
    :param ack: slack obj
    :param body: slack obj
    :param logger: slack obj
    :return: None
    """
    ack()
    piece_pay_calc_view(app, SlackApiError, context, logger)


# tier menu select action
# tier menu select requires a 200 response when an item is selected. idk y this is required
@app.action("static_tier_selected_do_nothing_please")
def shout_200_to_the_slack_gods(ack):
    ack()


# mistake selection view
@app.action('add_mistakes_button_click', middleware=[fetch_trigger_id, check_if_input_empty])
def open_mistake_view(ack, body, context, logger):
    ack()
    mistake_selection_view(app, SlackApiError, context, logger)


# update root view with mistake submission from mistake selection view
@app.view('root_view_plus_mistake_points_view', middleware=[fetch_trigger_id, fetch_mistake_points])
def root_with_mistakes_view(ack, body, context, logger):
    ack()
    piece_pay_calc_view(app, body, context, logger, ack=ack)


# update root view mistake point label
@app.action("clear_mistakes")
def clear_mistake_points_from_root_view(ack, body, context, logger, view, payload):
    ack()
    piece_pay_calc.mistake.remove_all_mistakes()
    context['mistake_points'] = piece_pay_calc.mistake.get_mistake_points()
    context['mistakes_cleared'] = True
    context['calculate'] = False
    piece_pay_calc_view(ack, body, context, logger, view)


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

    piece_pay_calc_view(ack, body, context, logger, view)


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


@app.event("message")
def handle(ack, body, logger):
    ack()
    print(body)


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
