from fastapi import Query


def pagination_params(
    page: int = Query(1, ge=1, description="page number"),
    size: int = Query(20, ge=1, le=100, description="page size"),
):
    return {"page": page, "size": size}
