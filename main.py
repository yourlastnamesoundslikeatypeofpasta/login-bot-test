import os

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


# Listen to the app_home_opened Events API event to hear when a user opens your app from the sidebar
@app.event("app_home_opened")
def app_home_opened(event, client, logger):
    user = event["user"]

    try:
        # Call the views.publish method using the WebClient passed to listeners
        result = client.views_publish(
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
                                "action_id": "score_button"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Piece Pay Calculator"
                                },
                                "action_id": "pay_button"
                            }
                        ]
                    }
                ],
            },
        )
        logger.info(result)

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
