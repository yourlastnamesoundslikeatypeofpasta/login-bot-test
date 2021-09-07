from app import app

from slack_sdk.errors import SlackApiError

from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import fetch_points
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import add_points
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import clear_points
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import create_points_block
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import create_payout_block
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import fetch_base_view
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import update_base_view
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import get_input_values
from apps.modal_piecepay_calc.modal_piecepay_calc_helpers import calculate_payout

from apps.middleware import fetch_root_id
from apps.middleware import fetch_trigger_id
from apps.middleware import validate_input


# root view
@app.action("piece_pay_home_button", middleware=[fetch_trigger_id,
                                                 fetch_points,
                                                 create_points_block,
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


# update mistake points
@app.action("mistake_selection", middleware=[fetch_root_id,
                                             fetch_points,
                                             add_points,
                                             create_points_block,
                                             fetch_base_view,
                                             ])
def update_block_points(ack, context, logger):
    ack()
    root_view_id = context['root_view_id']
    view = context['base_view']
    try:
        app.client.views_update(
            view_id=root_view_id,
            view=view
        )
    except SlackApiError as e:
        logger.error(e)


# update mistake points to 0
@app.action("clear_points", middleware=[fetch_root_id,
                                        fetch_points,
                                        clear_points,
                                        create_points_block,
                                        fetch_base_view,
                                        ])
def remove_mistake_block(ack, context, logger):
    ack()
    root_view_id = context['root_view_id']
    view = context['base_view']
    try:
        app.client.views_update(
            view_id=root_view_id,
            view=view
        )
    except SlackApiError as e:
        logger.error(e)


# calculate piece pay with or without mistake points
@app.view("piece_pay_calc_calculate", middleware=[fetch_points,
                                                  get_input_values,
                                                  validate_input,
                                                  create_points_block,
                                                  calculate_payout,
                                                  create_payout_block,
                                                  fetch_base_view,
                                                  update_base_view, ])
def piece_pay_calc_show_results_view(ack, context, logger):
    ack()
    if 'response_action' in context:
        response_action = context.get('response_action')
        try:
            ack(response_action)
        except SlackApiError as e:
            logger.error(e)
    else:
        view = context.get('view')
        response_action = {
            'response_action': 'update',
            'view': view
        }
        try:
            ack(response_action)
        except SlackApiError as e:
            logger.error(e)
