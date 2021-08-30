from pprint import pprint

from scripts.fetch_options import fetch_options


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
                logger.error(f'Error creating view: {e}')


def piece_pay_calc_view(app, slackapierror, context, logger, ack=None):
    """
    Open piece pay calculator when "Piece Pay Calculator" is clicked
    :param context:
    :param app:
    :param slackapierror:
    :param mistake:
    :param ack: slack obj
    :param body: slack obj
    :param logger: slack obj
    :return: None
    """
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
            "type": "section",
            "block_id": "block_tier",
            "text": {
                "type": "mrkdwn",
                "text": "Pick a tier from the dropdown list"
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a tier",
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 1",
                        },
                        "value": "tier_1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 2",
                        },
                        "value": "tier_2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 3",
                        },
                        "value": "tier_3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "P.S.",
                        },
                        "value": "personal_shopper"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "S.H.",
                        },
                        "value": "special_handling"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Heavies",
                        },
                        "value": "heavies"
                    }
                ],
                "action_id": "static_tier_selected_do_nothing_please",
            }
        },
        {
            "type": "section",
            "block_id": "block_section_w_add_mistake_button",
            "text": {
                "type": "mrkdwn",
                "text": f"*Add a mistake* _(optional)_:"
            },
            "accessory": {
                "type": "button",
                "action_id": "add_mistakes_button_click",
                "text": {
                    "type": "plain_text",
                    "text": "Add Mistake",
                },
                "style": "danger"
            }
        }
    ]
    view = {
        "type": "modal",
        "callback_id": "calc_piecepay_modal",
        "title": {
            "type": "plain_text",
            "text": "Piece Pay Calculator"
        },
        "submit": {
            "type": "plain_text",
            "text": "Calculate"
        },
        "clear_on_close": True,
        "blocks": blocks
    }
    if 'error_response' in context:
        # validation error view
        error_response_action = context['error_response']
        try:
            ack(error_response_action)
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
    elif 'calculate' in context and 'mistake_points' in context:
        # calculate with clear button view
        clear_mistake_block = {
            "block_id": "block_clear_mistake_button",
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": " "
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": f"Mistake Points: {context['mistake_points']}",
                },
                "action_id": "clear_mistakes",
            }
        }
        score_blocks = {
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
                    "text": f"*Tier* {context['tier_emoji']}: `{context['tier']}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Payout:moneybag::* `{context['payout']:.2f}`"
                },
            ],
        }
        view['blocks'].append(clear_mistake_block)
        view['blocks'].append(score_blocks)
        try:
            ack({
                "response_action": "update",
                "view": view
            })
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
    elif 'calculate' in context:
        # calculate without clear button view
        score_blocks = {
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
                    "text": f"*Tier* {context['tier_emoji']}: `{context['tier']}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Payout:moneybag::* `{context['payout']:.2f}`"
                },
            ],
        }
        view['blocks'].append(score_blocks)
        try:
            ack({
                "response_action": "update",
                "view": view
            })
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
    elif 'mistakes_cleared' in context:
        # clear mistake points from root view
        try:
            app.client.views_update(
                view_id=context['root_view_id'],
                view=view,
            )
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
    elif 'mistake_points' in context:
        # add mistakes, and clear button to root view
        clear_mistake_block = {
            "block_id": "block_clear_mistake_button",
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Mistake Points: {context['mistake_points']}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Clear Mistakes",
                },
                "action_id": "clear_mistakes",
            }
        }
        view['blocks'].append(clear_mistake_block)
        try:
            app.client.views_update(
                view_id=context['root_view_id'],
                view=view,
            )
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
    else:
        try:
            # open root view
            print('home')
            trigger_id = context['trigger_id']
            app.client.views_open(
                trigger_id=trigger_id,
                view=view,
            )
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')


def mistake_selection_view(app, slackapierror, context, logger, ack=None):
    blocks = [{
        "type": "input",
        "block_id": "block_mistake_static_select",
        "label": {
            "type": "plain_text",
            "text": "Select Mistake",
        },
        "element": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select Mistake..."
            },
            "action_id": "action_static_mistake",
            "options": fetch_options()
        }
    }]
    view = {
        "type": "modal",
        "callback_id": "root_view_plus_mistake_points_view",
        "title": {
            "type": "plain_text",
            "text": "Select Mistakes"
        },
        "submit": {
            "type": "plain_text",
            "text": "Add Mistakes",
        },
        "close": {
            "type": "plain_text",
            "text": "Close",
        },
        "blocks": blocks
    }
    if 'private_metadata' in context:
        view['private_metadata'] = context['private_metadata']
    try:
        app.client.views_push(
            trigger_id=context['trigger_id'],
            view=view
        )
    except slackapierror as e:
        logger.error(e)
