from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Dataset
from .schemas import PHENOPACKET_SCHEMA

DATASET_DATA_TYPE_ID = "dataset"


@api_view(["GET"])
def data_type_list(_request):
    return Response([{"id": DATASET_DATA_TYPE_ID, "schema": PHENOPACKET_SCHEMA}])


@api_view(["GET"])
def dataset_list(request):
    if DATASET_DATA_TYPE_ID not in request.query_params.getlist("data-type"):
        # TODO: Better error
        return Response(status=404)

    return Response([{
        "id": d.dataset_id,
        "name": d.name,
        "metadata": {
            "description": d.description,
            "project_id": d.project_id,
            "created": d.created.isoformat(),
            "updated": d.updated.isoformat()
        },
        "schema": PHENOPACKET_SCHEMA
    } for d in Dataset.objects.all()])


@api_view(["DELETE"])
def dataset_detail(request, dataset_id):
    # TODO: Implement GET, POST
    try:
        dataset = Dataset.objects.get(dataset_id=dataset_id)
    except Dataset.DoesNotExist:
        # TODO: Better error
        return Response(status=404)

    if request.method == "DELETE":
        dataset.delete()
        return Response(status=204)
