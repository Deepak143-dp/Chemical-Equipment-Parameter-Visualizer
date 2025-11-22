from django.urls import path
from . import views
urlpatterns = [
    path('upload/', views.UploadCSVView.as_view(), name='upload-csv'),
    path('datasets/', views.DatasetListView.as_view(), name='dataset-list'),
    path('datasets/<int:pk>/rows/', views.DatasetRowsView.as_view(), name='dataset-rows'),
    path('datasets/<int:pk>/summary/', views.DatasetSummaryView.as_view(), name='dataset-summary'),
    path('datasets/<int:pk>/download/', views.DatasetDownloadView.as_view(), name='dataset-download'),
    path('datasets/<int:pk>/', views.DatasetDetailView.as_view(), name='dataset-detail'),
]
