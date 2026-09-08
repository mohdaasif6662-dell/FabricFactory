from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path(
        'fabrics/',
        views.fabric_list,
        name='fabric_list'
    ),

    path(
        'fabrics/add/',
        views.fabric_add,
        name='fabric_add'
    ),

    path(
        'fabrics/<int:pk>/edit/',
        views.fabric_edit,
        name='fabric_edit'
    ),

    path(
        'fabrics/<int:pk>/delete/',
        views.fabric_delete,
        name='fabric_delete'
    ),

    path(
    'usage/',
    views.usage_list,
    name='usage_list'
),

path(
    'usage/add/',
    views.usage_add,
    name='usage_add'
),

path(
    'usage/<int:pk>/edit/',
    views.usage_edit,
    name='usage_edit'
),

path(
    'usage/<int:pk>/delete/',
    views.usage_delete,
    name='usage_delete'
),
path(
    'download-pdf-report/',
    views.download_pdf_report,
    name='download_pdf_report'
),
]