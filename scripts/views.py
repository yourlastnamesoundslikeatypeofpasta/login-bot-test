import time
from pprint import pprint
import os

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
    # validation error view
    if "error_response" in context:
        error_response_action = context['error_response']
        ack(error_response_action)
    elif "package_count" in context:
        # calculate packages view
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
    else:
        # open root form view
        trigger_id = context['trigger_id']
        app.client.views_open(
            trigger_id=trigger_id,
            view=view
        )


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
    if context['is_points_clear_block']:
        view['private_metadata'] = context['points']
    try:
        app.client.views_push(
            trigger_id=context['trigger_id'],
            view=view
        )
    except slackapierror as e:
        logger.error(e)


def send_mistakes_view(app, slackapierror, context, logger, ack=None):
    if 'employee_mistake_dict' in context:
        # build mistake section blocks and add approve/deny buttons
        for mistake_report in context['employee_mistake_dict']:  # todo: dont forgot to remove slice
            mistake_block = [
                {
                    "type": "header",
                    "block_id": "header_block",
                    "text": {
                        "type": "plain_text",
                        "text": f"{mistake_report['employee_name']} Mistake Report [[DATE-DATE] PLACEHOLDER]",
                    }
                },
                {
                    "type": "divider"
                }
            ]
            for index, mistake in enumerate(mistake_report['employee_mistakes']):
                section_with_mistakes_block = {
                    "type": "section",
                    "block_id": f"block_mistake_body_{index}",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Entered Date:*\n```{mistake['entered_date']}```"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Incident Date:*\n```{mistake['incident_date']}```"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Suite:*\n_<http://backoffice.myus.com/Warehouse/CustAccount.aspx?id={mistake['suite']}|```{mistake['suite']}```>_"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Package ID:*\n_<http://backoffice.myus.com/Warehouse/PackageMaint.aspx?packageId={mistake['pkg_id']}|```{mistake['pkg_id']}```>_"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Mistake Code:*\n```{mistake['mistake_type']}```"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Incident Notes:*\n```{mistake['incident_notes']}```"
                        },
                    ],
                    "accessory": {
                        "type": "overflow",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Package :package:",
                                },
                                "url": f"http://backoffice.myus.com/Warehouse/PackageMaint.aspx?packageId={mistake['pkg_id']}"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Package Photos :camera:",
                                },
                                "url": f"http://backoffice.myus.com/Shared/AllPhotos.aspx?PackageID={mistake['pkg_id']}"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Package MI :page_facing_up:",
                                },
                                "url": f"http://backoffice.myus.com/Shared/Controls/PackageDocument.aspx?pkgid={mistake['pkg_id']}"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Dispute :speaking_head_in_silhouette:",
                                },
                                "value": f'{index}'
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Help :sos:",
                                },
                                "value": "help"
                            },
                        ],
                        "action_id": "mistake_overflow_action"
                    }
                }
                mistake_block.append(section_with_mistakes_block)

                # mistake number context block
                mistake_num_context_block = {
                    "type": "context",
                    "elements": [
                        {
                            "type": "plain_text",
                            "text": f"{index + 1}",
                        }
                    ]
                }
                mistake_block.append(mistake_num_context_block)
                mistake_block.append({"type": "divider"})

            channel_id = app.client.conversations_open(
                users=context['selected_user']
            )['channel']['id']
            try:
                app.client.chat_postMessage(
                    channel=channel_id,
                    blocks=mistake_block,
                    text='Mistake Report',
                )
            except slackapierror as e:
                print(e)
