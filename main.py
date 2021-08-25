import os

from copy import deepcopy
from slack_bolt import App
from slack_sdk.errors import SlackApiError

from scripts.command_score import bonus_score
from scripts.command_score import find_stats
from scripts.values import mistake_values
from scripts.base_views import production_calc_base_view
from scripts.base_views import piece_pay_calc_base_view
from scripts.validate_input import validate_input
from scripts.get_payout import get_payout
from scripts.production_score import get_production_score
from scripts.get_error_msg_str import get_error_msg_str
from scripts.base_views import home_base_view
from scripts.base_views import build_options
from scripts.base_views import static_select_view_push

# start Slack app
app = App(token=os.environ['bot_token'], signing_secret=os.environ['signin_secret'])
BOT_ID = app.client.auth_test()['user_id']


# slack app home modals
@app.event("app_home_opened")
def app_home_opened(event, logger):
    """
    Listens to the app_home_opened Events API event to hear when a user opens your app from the sidebarAd
    :param event: dict, response from Events API when the home tab is opened https://api.slack.com/events/app_home_opened
    :param logger: console logger
    :return: None
    """

    @app.action('score_home_button')
    def score_home_button_click(ack, body):
        """
        Open production score calculator when "Production Calculator" is clicked
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
            logger.info(result)
        except SlackApiError as e:
            logger.info(f'Error creating view: {e}')

    @app.view("calc_score_modal")
    def get_stats_update_calc_score_modal(ack, view):
        """
        Updated production score calculator modal.
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

    @app.action("piece_pay_home_button")
    def piecepay_home_button_click(ack, body, logger):
        """
        Open piece pay calculator when "Piece Pay Calculator" is clicked
        :param ack: slack obj
        :param body: slack obj
        :param logger: slack obj
        :return: None
        """

        ack()
        trigger_id = body['trigger_id']

        # TODO: Add blocks to seperate dir, and files

        try:
            app.client.views_open(
                trigger_id=trigger_id,
                view=piece_pay_calc_base_view
            )
        except SlackApiError as e:
            logger.info(f'Error creating view: {e}')

    @app.action("mistake_selections")
    def mistake_selected(ack, body, logger):
        ack()
        logger.info(e)
        """try:
            selected_option_values = body['view']['state']['values']['block_mistakes']['mistake_selections'][
                'selected_options']
        except KeyError:
            return

        option_value_lst = []
        for option_value in selected_option_values:
            option_value_lst.append(option_value)
        return option_value_lst"""

    @app.action('add_mistakes_button_click')
    def open_mistake_view(ack, body):
        ack()
        options = build_options(mistake_values)
        trigger_id = body['trigger_id']

        try:
            app.client.views_push(
                trigger_id=trigger_id,
                view=static_select_view_push
            )
        except SlackApiError as e:
            print(e.response)

    @app.action("action_static_mistake")
    def mistake_selected(ack, body, logger):
        ack()
        logger.info(body)

    @app.action("add_mistake_button")
    def mistake_view_update(ack, body, logger):
        ack()
        print(body['view']['state']['values']['block_static_mistake']['action_static_mistake']['selected_option']['value'])
        logger.info(body)
        updated_view_blocks = 1


    @app.view("calc_piecepay_modal")
    def get_stats_update_calc_piecepay_modal(ack, view, body):
        """
        Updated piece pay calculator modal
        :param ack: slack obj
        :param view: slack obj
        :param body: slack obj
        :return: None
        """

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

        except (SlackApiError, ValueError) as e:
            print(e)
            logger.info(e)

        payout = get_payout(package_count,
                            weight_count,
                            item_count,
                            tier_value,
                            body)

        # pick age emoji :)
        if tier_value == 'tier_1':
            tier_emoji = ':baby:'
        elif tier_value == 'tier_2':
            tier_emoji = ':child:'
        elif tier_value == 'tier_3':
            tier_emoji = ':older_man:'
        else:
            tier_emoji = ''

        # copy base view and add section block
        view_update_blocks = {
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
                    "text": f"*Tier* {tier_emoji}: `{tier}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Payout:moneybag::* `{payout:.2f}`"
                },
            ],
        }
        view_update = deepcopy(piece_pay_calc_base_view)
        view_update['blocks'].append(view_update_blocks)

        ack({
            "response_action": "update",
            "view": view_update
        })

    @app.action("appeal_mistake_button_click")
    def appeal_mistake_button_click(ack, body):
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

    # app home view
    user = event["user"]
    view = home_base_view(event)
    try:
        result = app.client.views_publish(
            user_id=user,
            view=view
        )
        logger.info(result)
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
