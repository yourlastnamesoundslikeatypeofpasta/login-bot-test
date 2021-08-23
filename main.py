import os
import string

from slack_bolt import App
from slack_sdk.errors import SlackApiError

from scripts.command_score import bonus_score
from scripts.command_score import find_stats

app = App(token=os.environ['bot_token'], signing_secret=os.environ['signin_secret'])
BOT_ID = app.client.auth_test()['user_id']


def get_error_msg_str(command_name):
    """
    Error Message str with command name
    :param command_name: str, command name
    :return: str
    """
    return f'`Error: Stats not entered correctly. Enter: "/{command_name} help" for help`'


def get_production_score(pkgs, weight, items, hours):
    pkg_points = 14.7
    item_points = 2.03
    lbs_points = 0.99
    score = ((pkg_points * pkgs) + (item_points * items) + (lbs_points * weight)) / hours
    return score


def validate_input(b_input_value_dict):
    # check if input is only numbers
    error_block_id_list = []
    numbers = string.digits
    error_str = 'This entry can only contain numbers'
    for block_id, block_stat in b_input_value_dict.items():
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


# Listen to the app_home_opened Events API event to hear when a user opens your app from the sidebarAd
@app.event("app_home_opened")
def app_home_opened(event, logger):

    @app.action('score_home_button')
    def score_home_button_click(ack, body):
        ack()
        trigger_id = body['trigger_id']
        try:
            # open score input field view
            score_view_result = app.client.views_open(
                trigger_id=trigger_id,
                view={
                    "type": "modal",
                    "callback_id": "calc_score_modal",
                    "title": {
                        "type": "plain_text",
                        "text": "Production Calculator"
                    },
                    "submit": {
                        "type": "plain_text",
                        "text": "Calculate"
                    },
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
                        },
                    ],
                    "type": "modal"
                }
            )
            logger.info(result)
            score_view_id = score_view_result['view']['id']
            score_view_hash = body['view']['hash']
        except SlackApiError as e:
            logger.info(f'Error creating view: {e}')

    @app.view("calc_score_modal")
    def get_stats_update_calc_score_modal(ack, body, view):
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

            ack({
                "response_action": "update",
                "view": {
                    "type": "modal",
                    # View identifier
                    "callback_id": "calc_score_modal_update",
                    "title": {"type": "plain_text", "text": "Productivity Score"},
                    "blocks": [
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Packages* :package::\n`{package_count}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Weight* :weight_lifter::\n`{weight_count}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Items* :shopping_trolley::\n`{item_count}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Hours* :clock1::\n`{hour_count}`"
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
                                    "text": f"*Packages/Hour*:\n`{pkg_per_hour}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Weight/Package*:\n`{weight_per_package}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Items/Package*:\n`{items_per_pkg}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Productivity Score:*\n`{production_score:.2f}` :dash:"
                                },
                            ]
                        }
                    ]
                }
            })
        except (SlackApiError, ValueError) as e:
            print(e)
            logger.info(e)

    @app.action("piece_pay_home_button")
    def piecepay_home_button_click(ack, body, logger):
        ack()
        trigger_id = body['trigger_id']
        # TODO: Add blocks to seperate dir, and files
        try:
            piecepay_view_result = app.client.views_open(
                trigger_id=trigger_id,
                view={
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
                                    "text": "Select a tier",
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
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "Tier is based off of tenure",
                                }
                            ],
                        },
                    ]
                }
            )
        except SlackApiError as e:
            logger.info(f'Error creating view: {e}')

    @app.view("calc_piecepay_modal")
    def get_stats_update_calc_piecepay_modal(ack, view, body):
        def get_payout(package_count, weight_count, item_count, tier):
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
            return payout_value
        ack()

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
            package_count = float(block_input_values['block_package'])
            weight_count = float(block_input_values['block_weight'])
            item_count = float(block_input_values['block_items'])
            tier = view['state']['values']['block_tier']['static_select-action']['selected_option']['text']['text']
            tier_value = view['state']['values']['block_tier']['static_select-action']['selected_option']['value']
            payout = get_payout(package_count,
                                weight_count,
                                item_count,
                                tier_value)

            # pick age emoji :)
            if tier_value == 'tier_1':
                tier_emoji = ':baby:'
            elif tier_value == 'tier_2':
                tier_emoji = ':child:'
            elif tier_value == 'tier_3':
                tier_emoji = ':older_man:'
            else:
                tier_emoji = ''

            ack({
                "response_action": "update",
                "view": {
                    "type": "modal",
                    # View identifier
                    "callback_id": "piecepay_calc_modal_update",
                    "title": {"type": "plain_text", "text": "Piece Pay Report"},
                    "blocks": [
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Packages* :package::\n`{package_count}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Weight* :weight_lifter::\n`{weight_count}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Items* :shopping_trolley::\n`{item_count}`"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": f"*Tier* {tier_emoji}:\n`{tier}`"
                                },
                            ],
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Payout:moneybag::* `{payout}` "
                            }
                        }

                    ]
                }
            })

        except (SlackApiError, ValueError) as e:
            print(e)
            logger.info(e)

    # app home view
    user = event["user"]
    try:
        # app home view
        result = app.client.views_publish(
            user_id=user,
            view={
                # Home tabs must be enabled in your app configuration page under "App Home"
                # and your app must be subscribed to the app_home_opened event
                "type": "home",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Welcome home, <@{user}> :house:*",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Learn how home tabs can be more useful and interactive <https://api.slack.com/surfaces/tabs/using|*in the documentation*>.",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": "Psssst this home tab was designed using <https://api.slack.com/tools/block-kit-builder|*Block Kit Builder*>",
                            }
                        ],
                    },
                    {"type": "divider"},
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "Calculators",
                            "emoji": True
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Productivity Score Calculator"
                                },
                                "action_id": "score_home_button"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Piece Pay Calculator"
                                },
                                "action_id": "piece_pay_home_button"
                            }
                        ]
                    },
                    {
                        "type": "divider"
                    }
                ],
            }
        )
        logger.info(result)
        home_view_id = result['view']['id']
        home_view_hash = result['view']['hash']
    except SlackApiError as e:
        logger.error(f"Error fetching conversations: {e}")


# slack commands
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
    app.start(port=3000)
