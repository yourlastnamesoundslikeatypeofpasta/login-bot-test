



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
