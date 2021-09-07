from app import app

from slack_sdk.errors import SlackApiError

from apps.modal_production_calc.modal_production_calc_helpers import fetch_base_view
from apps.modal_production_calc.modal_production_calc_helpers import get_input_values
from apps.modal_production_calc.modal_production_calc_helpers import create_score_blocks
from apps.modal_production_calc.modal_production_calc_helpers import update_base_view

from apps.middleware import fetch_trigger_id
from apps.middleware import validate_input
from apps.middleware import calculate_production_score


# root view
@app.action('production_calc_button_click', middleware=[fetch_trigger_id,
                                                        fetch_base_view,
                                                        ])
def show_root_view(ack, context, logger):
    ack()
    trigger_id = context['trigger_id']
    view = context['base_view']

    try:
        app.client.views_open(
            trigger_id=trigger_id,
            view=view
        )
    except SlackApiError as e:
        logger.error(e)


# updated view
@app.view("production_calc_submission", middleware=[fetch_base_view,
                                                    get_input_values,
                                                    validate_input,
                                                    calculate_production_score,
                                                    create_score_blocks,
                                                    update_base_view,
                                                    ])
def show_updated_view(ack, context, logger):
    ack()
    if 'response_action' in context:
        ack(context['response_action'])
    else:
        view = context['view']
        response_action = {
            "response_action": "update",
            "view": view
        }
        try:
            ack(response_action)
        except SlackApiError as e:
            logger.error(e)
