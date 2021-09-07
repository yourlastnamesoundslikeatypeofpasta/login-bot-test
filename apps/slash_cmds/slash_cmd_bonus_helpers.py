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
        split_text = text.split(' ')
        if len(split_text) == 4:
            try:
                input_block_values = {
                    "block_packages": split_text[0].strip(' '),
                    "block_weight": split_text[1].strip(' '),
                    "block_items": split_text[2].strip(' '),
                    "block_hours": split_text[3].strip(' ')
                }
                context['input_block_values'] = input_block_values
                next()
            except ValueError:
                next()
        else:
            text = text.strip(' ')
            context['text'] = text
            next()
    else:
        next()


def generate_response(context):
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
        return blocks
    elif context.get('text') == 'help':
        # help str
        help_str = 'Enter stats in this format (with spaces in between each stat): `/bonus [pkgs] [lbs] [items] [hours]`\n' \
                   '*e.g:* `/bonus 100 200 175 5`'
        return help_str
    else:
        # error str
        error_msg_str = f'*Error:* `Stats not entered correctly.`\n' \
                        f'*Enter:* `"/bonus help"` for help'
        return error_msg_str
