from scripts.values import mistake_values


def build_options(mistake_dict):
    options_lst = []
    for mistake_code, point_value in mistake_dict.items():
        options_lst.append({
            "text": {
                "type": "plain_text",
                "text": f"{mistake_code.upper()}"
            },
            "value": f"{mistake_code}"
        }
        )
    return options_lst


def home_base_view(event):
    user = event['user']
    view = {
        "type": "home",
        "blocks": [
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
                        "action_id": "score_home_button"
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
        ],
    }
    return view


options = build_options(mistake_values)

production_calc_base_view = {
    "type": "modal",
    "callback_id": "calc_score_modal",
    "title": {
        "type": "plain_text",
        "text": "Production Calculator"
    },
    "submit": {
        "type": "plain_text",
        "text": "Calculate"
    },
    "blocks": [
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
    ],
}

piece_pay_calc_base_view = {
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
    "blocks": [
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
                    "text": "Select a tier...",
                    "emoji": True
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 1",
                            "emoji": True
                        },
                        "value": "tier_1"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 2",
                            "emoji": True
                        },
                        "value": "tier_2"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Tier 3",
                            "emoji": True
                        },
                        "value": "tier_3"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Personal Shopper",
                            "emoji": True
                        },
                        "value": "personal_shopper"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Special Handling",
                            "emoji": True
                        },
                        "value": "special_handling"
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "Heavies",
                            "emoji": True
                        },
                        "value": "heavies"
                    }
                ],
                "action_id": "static_select-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Tier",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Add mistakes - _*(optional)*_"
            },
            "accessory": {
                "type": "button",
                "action_id": "add_mistakes_button_click",
                "text": {
                    "type": "plain_text",
                    "text": "Add",
                },
                "style": "danger"
            }
        },
    ],
}

static_select_view_push = {
    "type": "modal",
    "callback_id": "static_select_modal",
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
    "blocks": [
        {
            "type": "actions",
            "block_id": "block_static_mistake",
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select Mistake..."
                    },
                    "action_id": "action_static_mistake",
                    "options": options
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add"
                    },
                    "action_id": "add_mistake_button",
                    "style": "danger"
                }
            ]
        },
    ]
}

