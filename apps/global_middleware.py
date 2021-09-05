
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
