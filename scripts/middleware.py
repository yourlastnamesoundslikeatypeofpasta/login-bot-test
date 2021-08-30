import logging
import os

import requests

from scripts.production_score import get_production_score
from scripts.validate_input import validate_input
from scripts.mistakes import Mistakes
from pprint import pprint


def fetch_user(payload, context, next):
    user = payload["user"]
    context['user'] = user
    next()


def fetch_trigger_id(body, context, next):
    trigger_id = body['trigger_id']
    context['trigger_id'] = trigger_id
    next()


def check_if_input_empty(body, context, next):
    values_lst = []
    package_input = body['view']['state']['values']['block_package']['package_input']['value']
    item_input = body['view']['state']['values']['block_items']['item_input']['value']
    weight_input = body['view']['state']['values']['block_weight']['weight_input']['value']
    tier_input = body['view']['state']['values']['block_tier']['static_tier_selected_do_nothing_please'][
        'selected_option']
    values_lst.append(package_input)
    values_lst.append(item_input)
    values_lst.append(weight_input)
    values_lst.append(tier_input)
    for value in values_lst:
        if value is None:
            context['private_metadata'] = 'True'
            next()
            return
    next()


def calculate_production_score(view, context, next):
    # values entered
    input_block_values = {
        "block_package": view['state']['values']['block_package']['package_input']['value'].strip(' '),
        "block_weight": view['state']['values']['block_weight']['weight_input']['value'].strip(' '),
        "block_items": view['state']['values']['block_items']['item_input']['value'].strip(' '),
        "block_hours": view['state']['values']['block_hours']['hour_input']['value'].strip(' ')
    }

    # validate input block values
    error_response_action = validate_input(input_block_values)
    if error_response_action:
        # throw validation error if blocks don't meet input req
        context['error_response'] = error_response_action
        next()
        return

    # add stats to context
    context['package_count'] = float(input_block_values['block_package'])
    context['weight_count'] = float(input_block_values['block_weight'])
    context['item_count'] = float(input_block_values['block_items'])
    context['hour_count'] = float(input_block_values['block_hours'])
    context['pkg_per_hour'] = context['package_count'] / context['hour_count']
    context['weight_per_package'] = context['weight_count'] / context['package_count']
    context['items_per_pkg'] = context['item_count'] / context['package_count']
    context['production_score'] = get_production_score(context['package_count'],
                                                       context['weight_count'],
                                                       context['item_count'],
                                                       context['hour_count'])
    next()


def fetch_mistake_points(body, context, next):
    are_inputs_empty = body['view']['private_metadata']
    mistake_code = \
        body['view']['state']['values']['block_mistake_static_select']['action_static_mistake']['selected_option'][
            'value']

    context['root_view_id'] = body['view']['root_view_id']
    # check if a Mistakes instance exists
    if are_inputs_empty:  # todo: mistakes are not disappearing when modal is closed and reopened
        # create one
        mistakes = Mistakes()
        mistakes.add_mistake(mistake_code)
        context['mistake_points'] = mistakes.get_mistake_points()
        pprint(Mistakes.instances)
        next()
        return
    else:
        # use the last instance
        mistakes = Mistakes.instances[-1]
    mistakes.add_mistake(mistake_code)
    context['mistake_points'] = mistakes.get_mistake_points()
    next()


def fetch_root_id(body, context, next):
    context['root_view_id'] = body['view']['root_view_id']
    next()


def download_file_shared(body, context, next, logger):
    # import is here because if added at the top, it breaks other middleware funcs, not sure why
    # todo: find out why import app from main breaks other funcs
    from main import app

    # get file info
    file_id = body['event']['file_id']
    info = app.client.files_info(file=file_id)
    file_name = info['file']['name']
    file_download_link = info['file']['url_private_download']

    # download file to path
    token = os.environ['bot_token']
    headers = {
        'Authorization': f"Bearer {token}"
    }  # token in headers is needed to download private files from the workspace
    r = requests.get(url=file_download_link, headers=headers)
    file_download_path = os.path.join('resources', 'downloads', file_name)
    with open(file_download_path, 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)
    next()
