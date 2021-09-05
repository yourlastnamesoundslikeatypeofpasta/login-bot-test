from app import app


# only acknowledge strings
@app.event("message",
           matchers=[lambda message: message.get('text') != ''])
def ack_message(ack, body, logger):
    """
    Respond 200 to messages that aren't filtered to a specific listener
    :param ack: slack acknowledge request func
    :param body: slack json payload
    :param logger: logger
    :return: None
    """
    ack()
