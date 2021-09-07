def fetch_base_view(context, next):
    base_blocks = [
        {
            "type": "input",
            "block_id": "block_packages",
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
    base_view = {
        "type": "modal",
        "callback_id": "production_calc_submission",
        "title": {
            "type": "plain_text",
            "text": "Production Calculator"
        },
        "submit": {
            "type": "plain_text",
            "text": "Calculate"
        },
        "blocks": base_blocks
    }
    context['base_blocks'] = base_blocks
    context['base_view'] = base_view
    next()


def get_input_values(context, body, next):
    input_block_values = {
        "block_packages": body['view']['state']['values']['block_packages']['package_input']['value'].strip(' '),
        "block_weight": body['view']['state']['values']['block_weight']['weight_input']['value'].strip(' '),
        "block_items": body['view']['state']['values']['block_items']['item_input']['value'].strip(' '),
        "block_hours": body['view']['state']['values']['block_hours']['hour_input']['value'].strip(' ')
    }
    context['input_block_values'] = input_block_values
    next()


def create_score_blocks(context, next):
    if 'stats' in context:
        stats = context['stats']
        score = context['score']
        score_block = [
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Packages/Hour:* `{stats['pkg_per_hour']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Weight/Package:* `{stats['weight_per_pkg']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Items/Package:* `{stats['items_per_pkg']:.2f}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Productivity Score:* `{score:.2f}` :dash:"
                    },
                ]
            }
        ]
        context['new_block'] = score_block
        next()
    else:
        next()


def update_base_view(context, next):
    if 'new_block' in context:

        # create new view key
        context['view'] = context['base_view']

        # create new blocks key with updated blocks lst
        context['blocks'] = context['base_blocks'] + context['new_block']

        # update new view key to point to new blocks key
        context['view']['blocks'] = context['blocks']
        next()
    else:
        next()
