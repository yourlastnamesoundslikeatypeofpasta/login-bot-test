from app import app

from apps.global_middleware import fetch_user_id
from apps.global_middleware import calculate_production_score


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
                str_to_float_lst = [float(i) for i in text.split(' ')]
                stats = {
                    'packages': str_to_float_lst[0],
                    'weight': str_to_float_lst[1],
                    'items': str_to_float_lst[2],
                    'hours': str_to_float_lst[3],
                    'pkg_per_hour': str_to_float_lst[0] / str_to_float_lst[3],
                    'weight_per_pkg': str_to_float_lst[1] / str_to_float_lst[0],
                    'items_per_pkg': str_to_float_lst[2] / str_to_float_lst[0]
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
                        "text": f"* Lbs :weight_lifter:: `{stats['weight']:.0f}`",
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
                        "text": f"* Lbs/Pkg: `{stats['weight_per_pkg']:.2f}`",
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


@app.command('/bonus', middleware=[fetch_user_id, parse_args, calculate_production_score, generate_response])
def bonus(ack, respond, context):
    """
    Slash command that calculates logger bonus.
    :param context:
    :input int, 4, each int is a statistic
    :output str, formatted bonus report
    :param ack: Something something server acknowledge thingy
    :param respond: slack respond func
    :return: None
    """
    ack()
    if 'response_blocks' in context:
        blocks = context['response_blocks']
        respond(blocks=blocks)
    else:
        response = context['response']
        respond(response)
