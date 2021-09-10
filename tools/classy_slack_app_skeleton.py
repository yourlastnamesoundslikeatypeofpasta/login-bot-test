import logging

from app import app

from apps.middleware import fetch_user_id

from slack_sdk.errors import SlackApiError


logging.basicConfig(level=logging.DEBUG)


@app.middleware
def log_request(logger, body, next):
    logger.info(body)
    return next()


@app.error
def global_error_handler(error, body, logger):
    logger.exception(error)
    logger.info(body)


class Request:

    @staticmethod
    def initiate_class(ack,
                       action,
                       body,
                       client,
                       context,
                       command,
                       event,
                       message,
                       options,
                       payload,
                       respond,
                       req,
                       resp,
                       say,
                       shortcut,
                       view,
                       logger,
                       ):
        ack()
        event_type = event.get('type')

        # match event_type with a view_dict "pattern", similar to django url_patterns
        url_patterns = {
            "app_home_opened": ShowHomeView
        }
        for event_name, view in url_patterns.items():
            if event_name == event_type:
                # return the matching view class
                return view(**locals()).as_view()
            else:
                logger.error(f'\nWARNING: Unhandled Event: "{event_type}"\n\n'
                             f'[SUGGESTION]You can handle this event by adding "{event_type}" to views_dict\n')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ShowHomeView(Request):

    def __init__(self, **kwargs):
        # init kwargs passed in initiate_class/view(**locals()).as_view()
        super().__init__(**kwargs)
        self.user = self.context.get('user')
        self.welcome_home_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Welcome home, <@{self.user}> :house:*",
                },
            },
            {"type": "divider"},
        ]
        self.calculator_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "Calculators ⚠CLASSS BASED VIEW IS stillllllll WORKING⚠ :abacus:",
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
                        "action_id": "production_calc_button_click"
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
        ]
        self.context_blocks = [
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": ":warning:*Prototype Slack Bot*:warning:\n"
                                " Link to code: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test|link>\n"
                                "Latest Changes: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test#latest-changes|link>\n"
                                "Known Issues: <https://github.com/yourlastnamesoundslikeatypeofpasta/login-bot-test#known-issues|link>",
                    }
                ],
            },
        ]

        # self.blocks = context.get('blocks')
        self.blocks = self.welcome_home_blocks + self.calculator_blocks + self.context_blocks
        self.view = {
            "type": "home",
            "blocks": self.blocks
        }

    def as_view(self):
        try:
            app.client.views_publish(
                user_id=self.user,
                view=self.view
            )
        except SlackApiError as e:
            self.logger.error(f"Error publishing home tab: {e}")


app.event("app_home_opened", middleware=[fetch_user_id])(Request.initiate_class)
app.event('message')(Request.initiate_class)

app.start(port=3000)
