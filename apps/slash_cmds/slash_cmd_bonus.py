from app import app

from slash_cmd_bonus_helpers import parse_args
from slash_cmd_bonus_helpers import generate_response
from apps.middleware import fetch_user_id
from apps.middleware import calculate_production_score
from apps.middleware import validate_input


@app.command('/bonus', middleware=[fetch_user_id,
                                   parse_args,
                                   validate_input,
                                   calculate_production_score,
                                   ])
def bonus(ack, respond, context):
    """
    Slash command that calculates logger bonus.
    :param context:
    :input int, 4, each int is a statistic
    :output str, formatted bonus report
    :param ack: Something something server acknowledge thingy
    :param respond: slack respond func
    :return: None
    """
    ack()
    response = generate_response(context)
    if type(response) == list:
        respond(blocks=response)
    else:
        respond(response)
