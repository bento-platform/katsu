from rest_framework.routers import DynamicRoute, Route, SimpleRouter


class BatchListRouter(SimpleRouter):
    """
    A router for APIs, where the POST method is the only allowed and is used
    to fetch a list of objects by mapping to the .list() method of the
    corresponding ViewSet. Also wires up any detail=False @action routes
    (e.g. export_fields) declared on the viewset.
    """

    routes = [
        Route(
            url=r"^{prefix}$",
            mapping={"post": "list"},
            name="{basename}",
            detail=False,
            initkwargs={"suffix": "List"},
        ),
        DynamicRoute(
            url=r"^{prefix}/{url_path}$",
            name="{basename}-{url_name}",
            detail=False,
            initkwargs={},
        ),
    ]
