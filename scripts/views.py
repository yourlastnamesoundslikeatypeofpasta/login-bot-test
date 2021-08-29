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
        {"type": "divider"},
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
        {"type": "divider"},
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": ":warning:*Prototype Slack Bot*:warning:\n Link to code: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test|link>",
                }
            ],
        },

    ]
    view = {
        "type": "home",
        "blocks": blocks
    }
    try:
        app.client.views_publish(
            user_id=user,
            view=view
        )
    except slackapierror as e:
        logger.error(f"Error publishing home tab: {e}")


def show_productivity_calc_view(app, slackapierror, context, logger, ack=None):
    blocks = [
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
        }
    ]
    view = {
        "type": "modal",
        "callback_id": "productivity_score_calculator_view_submission",
        "title": {
            "type": "plain_text",
            "text": "Production Calculator"
        },
        "submit": {
            "type": "plain_text",
            "text": "Calculate"
        },
        "blocks": blocks
    }
    try:
        # validation error view
        if context['error_response']:
            error_response_action = context['error_response']
            ack(error_response_action)
    except KeyError:
        try:
            # calculate packages view
            if context['package_count']:
                production_score_blocks = [
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Packages* :package:: `{context['package_count']:.2f}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Weight* :weight_lifter:: `{context['weight_count']:.2f}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Items* :shopping_trolley:: `{context['item_count']:.2f}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Hours* :clock1:: `{context['hour_count']:.2f}`"
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
                                "text": f"*Packages/Hour*: `{context['pkg_per_hour']:.2f}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Weight/Package*: `{context['weight_per_package']:.2f}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Items/Package*: `{context['items_per_pkg']:.2f}`"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Productivity Score:* `{context['production_score']:.2f}` :dash:"
                            },
                        ]
                    }
                ]
                for block in production_score_blocks:
                    blocks.append(block)
                response_action_update = {
                    "response_action": "update",
                    "view": view
                    }
                ack(response_action_update)
        except KeyError:
            try:
                # open root form view
                trigger_id = context['trigger_id']
                app.client.views_open(
                    trigger_id=trigger_id,
                    view=view
                )
            except slackapierror as e:
                logger.info(f'Error creating view: {e}')
