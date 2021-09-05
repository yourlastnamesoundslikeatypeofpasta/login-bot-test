def fetch_user_id(payload, context, next, logger):
    if 'user' in payload:
        user = payload['user']
        context['user'] = user
    elif 'user_id' in payload:
        user = payload['user_id']
        context['user'] = user
    else:
        logger.error('User not found in payload')
    next()


def fetch_trigger_id(body, context, next):
    trigger_id = body['trigger_id']
    context['trigger_id'] = trigger_id
    next()


def fetch_root_id(body, context, next):
    context['root_view_id'] = body['view']['root_view_id']
    next()


def calculate_production_score(context, next):
    # set the points that each stat is worth
    if 'stats' in context:
        pkg_points = 14.7
        item_points = 2.03
        weight_points = 0.99

        stats = context['stats']
        score = ((pkg_points * stats['packages']) + (item_points * stats['items']) + (weight_points * stats['weight'])) / stats['hours']
        context['score'] = score
        next()
    else:
        next()
