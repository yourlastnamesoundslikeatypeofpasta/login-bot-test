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
            "block_id": "block_mistakes",
            "text": {
                "type": "mrkdwn",
                "text": "Mistakes - *_optional_* (under development)"
            },
            "accessory": {
                "action_id": "mistake_selections",
                "type": "multi_static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select mistakes..."
                },
                "options": options
            }
        },
    ],
}
