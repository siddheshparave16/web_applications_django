from django.contrib.auth.models import Group
from django.core.cache import cache

def feature_flags(request):
    user = request.user

    flags = {
        "is_priority_feature_enabled": False
    }

    # ensure the user is authenticated before checking groups
    if user.is_authenticated:
        flags["is_priority_feature_enabled"] = user.groups.filter(name="Task Prioritization Beta Testers").exists()

    return flags

# same processor but act different way

# this prevents two users accessing the context processor simultaneously, from retrieving each others caches data
def feature_flags(request):
    user = request.user

    flags = {
        "is_priority_feature_enabled": False    # default value
    }

    # Initialize the variable with a default value
    is_priority_feature = False

    # ensure the user is authenticated before checking groups
    if user.is_authenticated:
        # Using the user's id to create a unique cache key
        cache_key = f"user_{user.id}_is_priority_feature"

        # Try to get the value from the cache
        is_priority_feature = cache.get(cache_key)

        if is_priority_feature is None:
            # Calculate the value if not in cache
            is_priority_feature = user.groups.filter(name="Task Prioritization Beta Testers").exists()

            # store the result in the cache for, say 5 minutes (300 seconds)
            cache.set(cache_key, is_priority_feature, 300)
    
    # Set the feature flag
    flags["is_priority_feature_enabled"] = is_priority_feature
    
    return flags

