

def fetch_user(payload, context, next):
    user = payload["user"]
    context['user'] = user
    next()
