import logging
import os
import random
import re

from slack_bolt import App
from slack_sdk.errors import SlackApiError

from tools.get_error_msg_str import get_error_msg_str
from tools.middleware import add_points
from tools.middleware import calculate_payout
from tools.middleware import calculate_production_score
from tools.middleware import clear_points
from tools.middleware import download_file_shared
from tools.middleware import fetch_points
from tools.middleware import fetch_root_id
from tools.middleware import fetch_trigger_id
from tools.middleware import fetch_user
from tools.middleware import get_tier_emoji
from tools.middleware import parse_file_download
from tools.slsh_cmd_bonus_funcs import find_stats, bonus_score
from tools.views import piece_pay_calc_view
from tools.views import send_mistakes_view
from tools.views import show_home_buttons_view
from tools.views import show_productivity_calc_view

# start Slack app
app = App(token=os.environ['bot_token'], signing_secret=os.environ['signin_secret'])
BOT_ID = app.client.auth_test()['user_id']
logging.basicConfig(level=logging.DEBUG)


@app.middleware
def log_request(logger, body, next):
    logger.debug(body)
    return next()


@app.error
def global_error_handler(error, body, logger):
    logger.exception(error)
    logger.info(body)


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Slack App Modals and Views@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# ##############################################Home View###############################################################
@app.event("app_home_opened", middleware=[fetch_user])
def app_home_root_view(context, logger):
    """
    Show home buttons
    :param context:
    :param logger: logger
    :return: None
    """
    show_home_buttons_view(app, SlackApiError, context, logger)


# ######################################Productivity Score Calculator Modal#############################################
# root view
@app.action('productivity_score_calculator_button_click', middleware=[fetch_trigger_id])
def productivity_score_calculator_root_view(ack, context, logger):
    """
    Open production score calculator when "Production Calculator" is clicked
    :param context:
    :param logger:
    :param ack: slack obj
    :param body: slack obj, https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html#slack_bolt.kwargs_injection.args.Args.action
    :return: None
    """
    ack()
    show_productivity_calc_view(app, SlackApiError, context, logger)


# updated view
@app.view("productivity_score_calculator_view_submission", middleware=[calculate_production_score])
def productivity_score_calculator_update_root_view(ack, context, logger):
    """
    Updated production score calculator modal.
    :param context:
    :param logger: logger obj
    :param ack: slack obj
    :param view: slack obj
    :return: None
    """
    ack()
    show_productivity_calc_view(app, SlackApiError, context, logger, ack=ack)


# #########################################Piece Pay Calculator Modal###################################################
# root view
@app.action("piece_pay_home_button", middleware=[fetch_trigger_id, fetch_root_id, fetch_points])
def piece_pay_calc_root_view(ack, context, logger):
    """
    Open piece pay calculator when "Piece Pay Calculator" is clicked
    :param view:
    :param context:
    :param ack: slack obj
    :param body: slack obj
    :param logger: slack obj
    :return: None
    """
    ack()
    piece_pay_calc_view(app, SlackApiError, context, logger)


@app.action("mistake_selection", middleware=[fetch_root_id, fetch_points, add_points])
def piece_pay_calc_add_mistake_block(ack, context, logger):
    ack()
    piece_pay_calc_view(app, SlackApiError, context, logger, ack=ack)


@app.action("clear_points", middleware=[fetch_root_id, fetch_points, clear_points])
def remove_mistake_block(ack, context, logger):
    ack()
    piece_pay_calc_view(app, SlackApiError, context, logger)


@app.view("piece_pay_calc_calculate", middleware=[fetch_points, calculate_payout, get_tier_emoji])
def piece_pay_calc_show_results_view(ack, context, logger):
    ack()
    piece_pay_calc_view(app, SlackApiError, context, logger)


# #########################################Appeal Mistake Modal#########################################################
@app.action("appeal_mistake_button_click")
def appeal_mistake_button_click(ack, body, logger):
    """
    Open appeal mistake modal when "Appeal Mistake" is clicked
    :param ack: slack obj
    :param body: slack obj
    :return: None
    """
    ack()
    trigger_id = body['trigger_id']
    try:
        app.client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "appeal_mistake_modal",
                "title": {
                    "type": "plain_text",
                    "text": "Mistake Appeal"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit"
                },
                "blocks": [
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "plain_text_input-action",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "02-415-0338"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Package Id",
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "plain_text_input-action",
                            "max_length": 250,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Enter a brief description..."
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Brief Description",
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "block_mistake",
                        "label": {
                            "type": "plain_text",
                            "text": "Mistake code",
                        },
                        "element": {
                            "action_id": "text1234",
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select mistake code..."
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "DE"
                                    },
                                    "value": "value-1"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "DE2"
                                    },
                                    "value": "value-2"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "QD"
                                    },
                                    "value": "value-3"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "PH2"
                                    },
                                    "value": "value-4"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "MI"
                                    },
                                    "value": "value-5"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "MI2"
                                    },
                                    "value": "value-6"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "WA"
                                    },
                                    "value": "value-6"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "CM"
                                    },
                                    "value": "value-7"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "DG MAJ"
                                    },
                                    "value": "value-8"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "UTL"
                                    },
                                    "value": "value-9"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "LABEL"
                                    },
                                    "value": "value-10"
                                }
                            ]
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "block_supervisor",
                        "label": {
                            "type": "plain_text",
                            "text": "Shift",
                        },
                        "element": {
                            "action_id": "text1234",
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select shift..."
                            },
                            "options": [
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "1st Shift"
                                    },
                                    "value": "first_shift"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "2nd Shift"
                                    },
                                    "value": "second_shift"
                                },
                                {
                                    "text": {
                                        "type": "plain_text",
                                        "text": "3rd Shift"
                                    },
                                    "value": "third_shift"
                                },
                            ]
                        }
                    },
                ]
            }
        )
    except SlackApiError as e:
        logger.info(e)
        print(e)


@app.view("appeal_mistake_modal")
def appeal_mistake_modal(ack, view, body):
    """
        Updated appeal mistake modal
        :param ack: slack obj
        :param view: slack obj
        :param body: slack obj
        :return: None
        """
    ack()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Message Reacts@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.message(re.compile("\b(hi|hello|hey|yo)\b"))
def say_hello(message, say):
    greeting_lst = ['hello', 'hi', 'whats up', 'yo']
    greeting = random.choice(greeting_lst)
    user = message['user']
    say(f'{greeting} <@{user}>!✌')


# only acknowledge strings
@app.event("message",
           matchers=[lambda message: message.get('text') != ''])
def handle_message(ack, body, event, message, logger):
    ack()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Send Mistake Reports Listeners@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.event('file_shared')
def acknowledge_file_shared(ack, body, context, logger):
    ack()


# acknowledge file_shared subtype
@app.event('message',
           matchers=[
               lambda message: message['files'][0]['filetype'] == 'xlsx',  # only match xlsx file types
               lambda message: message.get("subtype") != "bot_message"],  # ignore bot messages
           middleware=[download_file_shared])
def acknowledge_file_shared(ack, event, message, logger):
    ack()
    channel = event['channel']
    user = event['user']
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Mistake Report Date Range:*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "datepicker",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Start",
                    },
                    "action_id": "start_date_selected"
                },
                {
                    "type": "datepicker",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "End",
                    },
                    "action_id": "end_date_selected"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "⚠Caution: Pressing send will send all mistake reports to you ⚠\nThe final version will send mistakes to individual employees"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Send",
                    },
                    "style": "primary",
                    "value": "send_mistakes",
                    "action_id": "send_mistakes"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Cancel",
                    },
                    "style": "danger",
                    "value": "cancel_mistakes",
                    "action_id": "cancel_mistakes"
                }
            ]
        },
    ]
    ts = message['ts']

    if user != BOT_ID:
        try:
            result = app.client.chat_postMessage(channel=channel,
                                                 user=user,
                                                 blocks=blocks,
                                                 text='Send Mistake Report?',
                                                 thread_ts=ts
                                                 )
        except SlackApiError as e:
            logger.error()


@app.action('send_mistakes', middleware=[parse_file_download])
def send_mistakes(ack, context, respond, logger):
    ack()
    respond(':inbox_tray: Sending mistakes')
    send_mistakes_view(app, SlackApiError, context, logger)
    respond(':white_check_mark: All done!')


# appeal mistake view
@app.action("mistake_overflow_action")
def show_dispute_mistake_submission_view(ack, body, context, event, view, payload, logger):
    ack()
    overflow_selection_value = payload['selected_option']['value']
    if 'help' in overflow_selection_value:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Package details not loading after clicking links or menu options? *\n• Connection to MyUs' network is required to view package details. Try clicking the links from your station."
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Slack not installed on your station?*\n• Click <https://www.microsoft.com/store/productId/9WZDNCRDK3WP|here> to install it through the Microsoft Store."
                }
            }
        ]
        view = {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "Help :sos:"
            },
            "blocks": blocks
        }
        app.client.views_open(
            trigger_id=body['trigger_id'],
            view=view
        )
        return
    # find the mistake the user would like to appeal and show appeal view with mistake section and multiline section
    mistake_dispute_index = body['actions'][0]['selected_option']['value']
    message_blocks = body['message']['blocks']

    # get the correct mistake message section, and remove overflow from original mistake report
    mistake_message_section = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "`Mistake not found. Please report this error to Christian`"
        }
    }
    for block in message_blocks:
        if block['block_id'] == f'block_mistake_body_{mistake_dispute_index}':
            # remove dispute and help from the overflow menu
            mistake_message_section = block
            mistake_message_section['accessory']['options'] = mistake_message_section['accessory']['options'][0:3]
            break

    # get logger backoffice from mistake report header and add to mistake_message_section fields
    logger_backoffice_name = body['message']['blocks'][0]['text']['text'].split(' Mistake Report')[0]

    blocks = [
        mistake_message_section,
        {
            "type": "input",
            "block_id": 'block_shift_selection',
            "element": {
                "type": "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select your shift",
                },
                "options": [
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "1st Shift"
                        },
                        "value": '1st-shift-inbox'
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "2nd Shift",
                        },
                        "value": '2nd-shift-inbox'
                    },
                    {
                        "text": {
                            "type": "plain_text",
                            "text": "3rd Shift"
                        },
                        "value": '3rd-shift-inbox'
                    }
                ],
                "action_id": "static_select-action"
            },
            "label": {
                "type": "plain_text",
                "text": "Shift",
            }
        },
        {
            "type": "input",
            "block_id": "block_description",
            "element": {
                "type": "plain_text_input",
                "multiline": True,
                "action_id": "plain_text_input-action",
                "max_length": 250,
            },
            "label": {
                "type": "plain_text",
                "text": "Brief Description",
            }
        }
    ]
    view = {
        "type": "modal",
        "callback_id": "dispute_mistake_submitted",
        "private_metadata": logger_backoffice_name,
        "title": {
            "type": "plain_text",
            "text": "Dispute Mistake",
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit",
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel",
        },
        "blocks": blocks
    }
    app.client.views_open(
        trigger_id=body['trigger_id'],
        view=view
    )


@app.view('dispute_mistake_submitted')
def send_mistake_to_triage(ack, body, view, context, logger):
    ack()
    mistake_section_body_block = view['blocks'][0]

    # get values
    selected_shift_inbox = view['state']['values']['block_shift_selection']['static_select-action']['selected_option'][
        'value']
    brief_description = view['state']['values']['block_description']['plain_text_input-action']['value']
    user = body['user']['id']
    backoffice_name = view['private_metadata']

    # get over flow menu and delete it so it can be attached to another block
    over_flow_menu = view['blocks'][0]['accessory']
    del view['blocks'][0]['accessory']

    # confirm approval or denial

    mistake_section_body_block["accessory"] = over_flow_menu

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Mistake Dispute Request",
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Backoffice Name:*\n```{backoffice_name}```"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Slack Profile:*\n```<@{user}>```"
                },
            ],
        },
        mistake_section_body_block,
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Dispute Reason:",
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f'```{brief_description}```',
            },
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
                        "text": "Claim"
                    },
                    "action_id": "claim_dispute",
                    "value": "claim_dispute",
                }
            ]
        },
    ]
    channel_id_lst = app.client.conversations_list(
        types='private_channel'
    )
    for channel in channel_id_lst['channels']:
        if selected_shift_inbox == channel['name']:
            channel_id = channel['id']
            app.client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text='Mistake Appeal Submitted'
            )


@app.action("claim_dispute")
def show_claimer_and_approve_deny_buttons(ack, body, respond, payload, event, view, context, logger):
    ack()
    # remove claim button block
    blocks = body['message']['blocks']
    del blocks[-1]

    # add claimer text block
    user = body['user']['id']
    claimer_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":writing_hand:<@{user}> is researching this mistake",
        }
    }

    # add approve, deny buttons
    blocks.append(claimer_block)
    confirm_approve_dialog_obj = {
        "title": {
            "type": "plain_text",
            "text": "Are you sure?"
        },
        "text": {
            "type": "mrkdwn",
            "text": "This action cannot be undone"
        },
        "confirm": {
            "type": "plain_text",
            "text": "Approve",
        },
        "deny": {
            "type": "plain_text",
            "text": "I've changed my mind!"
        }
    }
    confirm_deny_dialog_obj = {
        "title": {
            "type": "plain_text",
            "text": "Are you sure?"
        },
        "text": {
            "type": "mrkdwn",
            "text": "This action cannot be undone"
        },
        "confirm": {
            "type": "plain_text",
            "text": "Deny",
        },
        "deny": {
            "type": "plain_text",
            "text": "I've changed my mind!"
        },
        "style": "danger"
    }
    approve_deny_button_blocks = {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Approve"
                },
                "action_id": "approve_dispute",
                "style": "primary",
                "value": "approve_dispute",
                "confirm": confirm_approve_dialog_obj
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Deny"
                },
                "action_id": "deny_dispute",
                "style": "danger",
                "value": "deny_dispute",
                "confirm": confirm_deny_dialog_obj
            }
        ]
    }
    blocks.append(approve_deny_button_blocks)

    # update message
    channel = body['channel']['id']
    ts = body['message']['ts']
    app.client.chat_update(
        channel=channel,
        ts=ts,
        blocks=blocks,
        text='Mistake Claimed'
    )


@app.action("approve_dispute")
def edit_message_and_notify_employee_of_approval(ack, body, respond, payload, event, view, context, logger):
    ack()
    blocks = body['message']['blocks']
    del blocks[-1]

    user = body['user']['id']
    channel = body['channel']['id']

    approval_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":thumbsup: <@{user}> approved this mistake",
        }
    }
    blocks.append(approval_block)

    ts = body['message']['ts']

    app.client.chat_update(
        channel=channel,
        ts=ts,
        blocks=blocks,
        text='Mistake Approved'
    )


@app.action("deny_dispute")
def edit_message_and_notify_employee_of_denial(ack, body, context, respond, logger):
    ack()
    blocks = body['message']['blocks']
    del blocks[-1]

    user = body['user']['id']
    channel = body['channel']['id']

    approval_block = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f":thumbsdown: <@{user}> denied this mistake",
        }
    }
    blocks.append(approval_block)

    ts = body['message']['ts']

    app.client.chat_update(
        channel=channel,
        ts=ts,
        blocks=blocks,
        text='Mistake Denied'
    )


# acknowledge file created
@app.event("file_created")
def acknowledge_file_created(ack, event, logger):
    ack()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@Slash Commands@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@app.command('/bonus')
def bonus(ack, respond, command):
    """
    Slash command that calculates logger bonus.
    :input int, 4, each int is a statistic
    :output str, formatted bonus report
    :param ack: Something something server acknowledge thingy
    :param respond: slack respond func
    :param command: dict, payload
    :return: None
    """

    ack()
    command_name = 'bonus'
    user = command['user_id']

    try:
        text = command['text']
    except KeyError:  # if the user enters whitespace
        respond(get_error_msg_str(command_name))
        return

    # if a user needs help using the slack command
    if text.strip(' ') == 'help':
        respond(
            'Enter stats in this format (with spaces in between each stat): `/bonus [pkgs] [lbs] [items] [hours]`\n example: `/bonus 100 200 175 5`')
        return

    # print out stat report
    stat_dict = find_stats(text)
    if stat_dict:
        logger_bonus_score = bonus_score(stat_dict)
        pkg_per_hour = stat_dict['packages'] / stat_dict['hours']
        lbs_per_pkg = stat_dict['lbs'] / stat_dict['packages']
        items_per_pkg = stat_dict['items'] / stat_dict['packages']
        respond(
            f'<@{user}>\n- Packages :package:: `{stat_dict["packages"]}`\n- Lbs :weight_lifter:: `{stat_dict["lbs"]}`\n- Items :shopping_trolley:: `{stat_dict["items"]}`\n- Hours :clock1:: `{stat_dict["hours"]}`\n\n- Pkg/Hour: `{pkg_per_hour}`\n- Lbs/Pkg: `{lbs_per_pkg}`\n- Items/Pkg: `{items_per_pkg}`\n\n- Estimated Productivity Score: `{logger_bonus_score:.2f}` :dash:')
    else:
        respond(get_error_msg_str(command_name))


if __name__ == '__main__':
    app.start(port=3000)
