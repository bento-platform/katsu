from rest_framework.routers import Route, SimpleRouter


class BatchListRouter(SimpleRouter):
    """
    A router for APIs, where the POST method is the only allowed and is used
    to fetch a list of objects by mapping to the .list() method of the
    corresponding ViewSet
    """
    routes = [
        Route(
            url=r'^{prefix}$',
            mapping={'post': 'list'},
            name='{basename}',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
    ]
