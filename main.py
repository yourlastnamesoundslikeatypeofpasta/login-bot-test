import os
import json

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
                        "text": "Enter Production Stats"
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
                                "action_id": "sl_input",
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
                                "action_id": "sl_input",
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
                                "action_id": "sl_input",
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
                                "action_id": "sl_input",
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
    def get_stats_update_modal(ack, body, view):
        errors = {}
        ack()
        print(view)
        package_count = view['state']['values']['block_package']['sl_input']['value']
        weight_count = view['state']['values']['block_weight']['sl_input']['value']
        item_count = view['state']['values']['block_items']['sl_input']['value']
        hour_count = view['state']['values']['block_hours']['sl_input']['value']
        print(package_count, weight_count, item_count, hour_count)

        view_id = body['view']['id']
        view_hash = body['view']['hash']
        trigger_id = body['trigger_id']

        try:
            app.client.views_open(
                # Pass the view_id
                view_id=body["view"]["id"],
                # String that represents view state to protect against race conditions
                hash=body["view"]["hash"],
                trigger_id=trigger_id,
                # View payload with updated blocks
                view={
                    "type": "modal",
                    # View identifier
                    "callback_id": "calc_score_modal",
                    "title": {"type": "plain_text", "text": "Updated modal"},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {"type": "plain_text", "text": "You updated the modal!"}
                        },
                        {
                            "type": "image",
                            "image_url": "https://media.giphy.com/media/SVZGEcYt7brkFUyU90/giphy.gif",
                            "alt_text": "Yay! The modal was updated"
                        }
                    ]
                }
            )
        except SlackApiError as e:
            print(e.response)

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
                    }
                ],
            },
        )
        logger.info(result)
        home_view_id = result['view']['id']
        home_view_hash = result['view']['hash']
        print(home_view_id)
        print(home_view_hash)
    except SlackApiError as e:
        logger.error(f"Error fetching conversations: {e}")


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
