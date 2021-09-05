from app import app

from apps.global_middleware import fetch_user_id


def parse_args(context, command, next):
    """
    Split text, convert to floats, and add each float to a stat in dict.
    :param next:
    :param context:
    :param command:
    :return:
    """
    if 'text' in command:
        text = command['text']

        # make sure the exact num of args == 4
        len_split_text = len(text.split(' '))
        if len_split_text == 4:
            try:
                text_lst = [float(i) for i in text.split(' ')]
                stats = {
                    'packages': text_lst[0],
                    'lbs': text_lst[1],
                    'items': text_lst[2],
                    'hours': text_lst[3],
                    'pkg_per_hour': text_lst[0] / text_lst[3],
                    'lbs_per_pkg': text_lst[1] / text_lst[0],
                    'items_per_pkg': text_lst[2] / text_lst[0]
                }
                context['stats'] = stats
                next()
            except ValueError:
                next()
        else:
            text = text.strip(' ')
            context['text'] = text
            next()
    else:
        context['text'] = ''
        next()


def calculate_bonus_score(context, next):
    """
    Calculate logger score
    :return: float, logger score
    """
    # set the points that each stat is worth
    if 'stats' in context:
        pkg_points = 14.7
        item_points = 2.03
        lbs_points = 0.99

        stats = context['stats']
        score = ((pkg_points * stats['packages']) + (item_points * stats['items']) + (lbs_points * stats['lbs'])) / \
                stats[
                    'hours']
        context['score'] = score
        next()
    else:
        next()


def generate_response(context, next):
    if 'stats' in context:
        # calculated stats str
        stats = context['stats']
        score = context['score']
        user = context['user']
        blocks = [
            {
                "type": "section",
                "text": {
                    "text": f"<@{user}> Production Score",
                    "type": "mrkdwn"
                },
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"* Packages :package:: `{stats['packages']:.0f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Lbs :weight_lifter:: `{stats['lbs']:.0f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Items :shopping_trolley:: `{stats['items']:.0f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Hours :clock1:: `{stats['hours']:.2f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Pkg/Hour: `{stats['pkg_per_hour']:.2f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Lbs/Pkg: `{stats['lbs_per_pkg']:.2f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Items/Pkg: `{stats['items_per_pkg']:.2f}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"* Productivity Score: `{score:.2f}` :dash:",
                    }
                ]
            }
        ]
        context['response_blocks'] = blocks
        next()
    elif context['text'] == 'help':
        # help str
        help_str = 'Enter stats in this format (with spaces in between each stat): `/bonus [pkgs] [lbs] [items] [hours]`\n' \
                   '*e.g:* `/bonus 100 200 175 5`'

        context['response'] = help_str
        next()
    else:
        # error str
        error_msg_str = f'*Error:* `Stats not entered correctly.`\n' \
                        f'*Enter:* `"/bonus help"` for help'
        context['response'] = error_msg_str
        next()


@app.command('/bonus', middleware=[fetch_user_id, parse_args, calculate_bonus_score, generate_response])
def bonus(ack, respond, context):
    """
    Slash command that calculates logger bonus.
    :param context:
    :input int, 4, each int is a statistic
    :output str, formatted bonus report
    :param ack: Something something server acknowledge thingy
    :param respond: slack respond func
    :param command: dict, payload
    :return: None
    """
    ack()
    if 'response_blocks' in context:
        blocks = context['response_blocks']
        respond(blocks=blocks)
    else:
        response = context['response']
        respond(response)
