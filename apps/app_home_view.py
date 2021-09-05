from app import app
from slack_sdk.errors import SlackApiError
from apps.global_middleware import fetch_user


def welcome_home_blocks(context, next):
    user = context['user']
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Welcome home, <@{user}> :house:*",
            },
        },
        {"type": "divider"},
    ]
    context['welcome_home_blocks'] = blocks
    next()


def calculator_blocks(context, next):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Calculators :abacus:",
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
                    "action_id": "productivity_score_calculator_button_click"
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
        },
    ]
    context['calculator_blocks'] = blocks
    next()


def context_blocks(context, next):
    blocks = [
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":warning:*Prototype Slack Bot*:warning:\n"
                            " Link to code: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test|link>\n"
                            "Latest Changes: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test#latest-changes|link>\n"
                            "Known Issues: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test#known-issues|link>",
                }
            ],
        },
    ]
    context['context_blocks'] = blocks
    next()


def create_blocks(context, next):
    home_blocks = []
    block_lst = [
        context['welcome_home_blocks'],
        context['calculator_blocks'],
        context['context_blocks']
    ]
    for blocks in block_lst:
        for block in blocks:
            home_blocks.append(block)
    context['blocks'] = home_blocks
    next()


@app.event("app_home_opened", middleware=[fetch_user, welcome_home_blocks,
                                          calculator_blocks, context_blocks,
                                          create_blocks])
def app_home_root_view(context, logger):
    """
    Show home view
    :param context:
    :param logger: logger
    :return: None
    """

    blocks = context['blocks']
    view = {
        "type": "home",
        "blocks": blocks
    }
    try:
        app.client.views_publish(
            user_id=context['user'],
            view=view
        )
    except SlackApiError as e:
        logger.error(f"Error publishing home tab: {e}")
