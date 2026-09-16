from django.urls import path

from .views import (
    add_member,
    create_pool,
    dashboard,
    import_contributions_view,
    record_payment,
    settlements,
    switch_pool,
)


urlpatterns = [
    path(
        "",
        dashboard,
        name="dashboard",
    ),

    path(
        "pool/create/",
        create_pool,
        name="create_pool",
    ),

    path(
        "pool/switch/<int:pool_id>/",
        switch_pool,
        name="switch_pool",
    ),

    path(
        "member/add/",
        add_member,
        name="add_member",
    ),

    path(
        "payment/add/",
        record_payment,
        name="record_payment",
    ),

    path(
        "import/",
        import_contributions_view,
        name="import_contributions",
    ),

    path(
        "settlements/",
        settlements,
        name="settlements",
    ),
]