from scripts.mistakes import Mistakes


def fetch_options():
    options_lst = []
    for mistake_code, point_value in Mistakes.mistake_values.items():
        options_lst.append({
            "text": {
                "type": "plain_text",
                "text": f"{mistake_code.upper()} ({point_value} points)"
            },
            "value": f"{mistake_code}"
        }
        )
    return options_lst
