import logging
import os
import datetime

import requests
import openpyxl

from tools.production_score import get_production_score
from tools.validate_input import validate_input
from tools.get_payout import get_payout
from tools.send_mistake_report import MistakeReport





def fetch_trigger_id(body, context, event, next):
    trigger_id = body['trigger_id']
    context['trigger_id'] = trigger_id
    next()


def fetch_root_id(body, context, next):
    context['root_view_id'] = body['view']['root_view_id']
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


def fetch_points(body, context, next):
    points = body['view']['private_metadata']
    if points == '':
        context['points'] = '0'
    else:
        context['points'] = points
    next()


def clear_points(body, context, next):
    context["points"] = "0"
    context['points_cleared'] = True
    next()


def add_points(body, context, next):
    selected_mistake = \
        body['view']['state']['values']['block_mistake_static_select']['mistake_selection']['selected_option']['value']
    selected_mistake_point_value = int(selected_mistake.split("_")[1])
    current_points = int(context['points'])
    context['points'] = str(current_points + selected_mistake_point_value)
    next()


def calculate_payout(body, context, next):
    # get stats
    package_count = body['view']['state']['values']['block_package']['package_input']['value']
    weight_count = body['view']['state']['values']['block_weight']['weight_input']['value']
    item_count = body['view']['state']['values']['block_items']['item_input']['value']
    tier = body['view']['state']['values']['block_tier']['static_tier_select']['selected_option']['text']['text']
    tier_value = body['view']['state']['values']['block_tier']['static_tier_select']['selected_option']['value']

    # add stats to context
    context['package_count'] = package_count
    context['weight_count'] = weight_count
    context['item_count'] = item_count
    context['item_count'] = item_count
    context['tier'] = tier
    context['tier_value'] = tier_value

    # calculate payout and add to context
    package_count = float(package_count)
    weight_count = float(weight_count)
    item_count = float(item_count)
    points = int(context['points'])
    payout = get_payout(package_count, weight_count, item_count, tier_value, points)
    context["payout"] = payout
    next()


def get_tier_emoji(context, next):
    # choose emoji according to tier
    if context['tier_value'] == 'tier_1':
        context['tier_emoji'] = ':baby:'
    elif context['tier_value'] == 'tier_2':
        context['tier_emoji'] = ':child:'
    elif context['tier_value'] == 'tier_3':
        context['tier_emoji'] = ':older_man:'
    else:
        context['tier_emoji'] = ''
    next()


def download_file_shared(body, context, event, message, next, logger):
    # get file info
    client = context['client']
    file_id = body['event']['files'][0]['id']
    info = client.files_info(file=file_id)
    file_name = info['file']['name']
    file_download_link = info['file']['url_private_download']

    # download file to path
    token = os.environ['bot_token']
    headers = {
        'Authorization': f"Bearer {token}"}  # token in headers is needed to download private files from the workspace
    r = requests.get(url=file_download_link, headers=headers)
    file_downloads_dir = os.path.join('data')
    file_download_path = os.path.join('data', file_name)
    if not os.path.exists(file_downloads_dir):
        os.makedirs(file_download_path)

    try:
        with open(file_download_path, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)
    except PermissionError:
        logger.error('Permissions Error: File is most likely open in Excel. Please close Excel and restart')
    mistakes = MistakeReport(file_download_path)
    next()


def parse_file_download(body, context, next, logger):
    # open workbook, assign sheets, close wb
    mistake_report_obj = MistakeReport.instances[-1]
    file_download_path = mistake_report_obj.file_download_path
    mistake_report_file = file_download_path
    wb = openpyxl.load_workbook(mistake_report_file)
    wb_sheet_lst = wb.sheetnames
    sheet = wb[wb_sheet_lst[1]]
    wb.close()

    # create a list of dicts with lists for each column associated  with the employee
    num_rows_w_mistakes = sheet.max_row
    mistake_report = {}
    for row in list(sheet.iter_rows(3, num_rows_w_mistakes)):
        mistake = {}
        employee = None
        for cell in row:
            if cell.column_letter == 'A':
                employee = cell.value
            elif cell.column_letter == 'B':
                entered_date = cell.value.strftime('%m/%d/%y')
                mistake['entered_date'] = entered_date
            elif cell.column_letter == 'C':
                incident_date = cell.value.strftime('%m/%d/%y')
                mistake['incident_date'] = incident_date
            elif cell.column_letter == 'D':
                mistake_type = cell.value
                mistake['mistake_type'] = mistake_type
            elif cell.column_letter == 'E':
                suite = cell.value
                mistake['suite'] = suite
            elif cell.column_letter == 'F':
                pkg_id = cell.value
                mistake['pkg_id'] = pkg_id
            elif cell.column_letter == 'H':
                incident_notes = cell.value
                mistake['incident_notes'] = incident_notes
            else:
                continue

        if employee in mistake_report:
            mistake_report[employee].append(mistake)
        else:
            mistake_report[employee] = [mistake]
        context['mistake_report_dict'] = mistake_report
    next()
