from app import app
from slack_sdk.errors import SlackApiError
from apps.global_middleware import fetch_user_id


def create_blocks(context, next):
    context['blocks'] = []
    next()


def create_welcome_home_blocks(context, next):
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
    for block in blocks:
        context['blocks'].append(block)
    next()


def create_calculator_blocks(context, next):
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
    for block in blocks:
        context['blocks'].append(block)
    next()


def create_context_blocks(context, next):
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
    for block in blocks:
        context['blocks'].append(block)
    next()


@app.event("app_home_opened", middleware=[fetch_user_id, create_blocks, create_welcome_home_blocks,
                                          create_calculator_blocks, create_context_blocks])
def open_app_home_view(context, logger):
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
