from tools.fetch_options import fetch_options


def piece_pay_calc_view(app, slackapierror, context, logger, ack=None):
    """
    Open piece pay calculator when "Piece Pay Calculator" is clicked
    :param context:
    :param app:
    :param slackapierror:
    :param ack: slack obj
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
            "type": "input",
            "block_id": "block_tier",
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select a tier",
                },
                "action_id": "static_tier_select",
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
            },
            "label": {
                "type": "plain_text",
                "text": "Pick a tier from the dropdown list",
            },
        },
        {
            "type": "section",
            "block_id": "block_mistake_static_select",
            "text": {
                "type": "mrkdwn",
                "text": "Pick a mistake _(optional)_:"
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select mistake",
                },
                "options": fetch_options(),
                "action_id": "mistake_selection"
            }
        },
        {
            "type": "section",
            "block_id": "block_points_and_clear",
            "text": {
                "type": "mrkdwn",
                "text": f"Mistake Points: {str(context['points'])}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Clear Points",
                },
                "action_id": "clear_points"
            }
        }
    ]

    view = {
        "type": "modal",
        "callback_id": "piece_pay_calc_calculate",
        "title": {
            "type": "plain_text",
            "text": "Piece Pay Calculator"
        },
        "submit": {
            "type": "plain_text",
            "text": "Calculate"
        },
        "blocks": blocks
    }
    if 'error_response' in context:
        # validation error view
        error_response_action = context['error_response']
        try:
            ack(error_response_action)
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
    elif 'payout' in context:
        # update view and modal with payout and points
        score_block = {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Packages* :package:: `{context['package_count']}`",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Weight* :weight_lifter:: `{context['weight_count']}`"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Items* :shopping_trolley:: `{context['item_count']}`"
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
        view['private_metadata'] = context['points']
        blocks.append(score_block)
        response_action = {
            "response_action": "update",
            "view": view
        }
        ack = context['ack']
        ack(response_action)
    elif int(context['points']) > 0:
        # update private_metadata
        view["private_metadata"] = context['points']

        # update view
        app.client.views_update(
            view_id=context['root_view_id'],
            view=view
        )
    elif 'points_cleared' in context:
        # update private metadata
        view["private_metadata"] = context['points']

        # update view
        app.client.views_update(
            view_id=context['root_view_id'],
            view=view
        )
    else:
        try:
            # open root view
            trigger_id = context['trigger_id']
            app.client.views_open(
                trigger_id=trigger_id,
                view=view,
            )
        except slackapierror as e:
            logger.error(f'Error creating view: {e}')
        except KeyError:
            # if a user selects a mistake with a value of 0
            try:
                app.client.views_update(
                    view_id=context['root_view_id'],
                    view=view
                )
            except slackapierror as e:
                logger.error(f'Error creating view: {e}')


def send_mistakes_view(app, slackapierror, context, logger, ack=None):
    if 'mistake_report_dict' in context:
        # build mistake section blocks and add approve/deny buttons
        for employee, mistake_lst in context['mistake_report_dict'].items():
            mistake_block = [
                {
                    "type": "header",
                    "block_id": "header_block",
                    "text": {
                        "type": "plain_text",
                        "text": f"{employee} Mistake Report [[DATE-DATE] PLACEHOLDER]",
                    }
                },
                {
                    "type": "divider"
                }
            ]
            for index, mistake in enumerate(mistake_lst):
                section_with_mistakes_block = {
                    "type": "section",
                    "block_id": f"block_mistake_body_{index}",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Entered Date:*\n{mistake['entered_date']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Incident Date:*\n{mistake['incident_date']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Suite:*\n_<http://backoffice.myus.com/Warehouse/CustAccount.aspx?id={mistake['suite']}|{mistake['suite']}>_"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Package ID:*\n_<http://backoffice.myus.com/Warehouse/PackageMaint.aspx?packageId={mistake['pkg_id']}|{mistake['pkg_id']}>_"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Mistake Code:*\n{mistake['mistake_type']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Incident Notes:*\n{mistake['incident_notes']}"
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
                users=context['user_id']
            )['channel']['id']
            try:
                app.client.chat_postMessage(
                    channel=channel_id,
                    blocks=mistake_block,
                    text='Mistake Report',
                )
            except slackapierror as e:
                print(e)
