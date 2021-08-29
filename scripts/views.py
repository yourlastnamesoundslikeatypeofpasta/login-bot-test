def show_home_buttons_view(app, slackapierror, context, logger):
    user = context["user"]
    blocks = [
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
                        "text": "Link to login-bot-test code: Github <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test|link>",
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
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Appeal Mistake (under dev)",
                            "emoji": True
                        },
                        "action_id": "appeal_mistake_button_click"
                    }
                ]
            },
        ]
    view = {
        "type": "home",
        "blocks": blocks
    }
    try:
        result = app.client.views_publish(
            user_id=user,
            view=view
        )
    except slackapierror as e:
        logger.error(f"Error publishing home tab: {e}")
