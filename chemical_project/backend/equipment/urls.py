from django.urls import path
from .views import upload_csv, upload_history

urlpatterns = [
    path("upload/", upload_csv),
    path("history/", upload_history),
]
from .views import upload_csv, upload_history, download_report_pdf

urlpatterns = [
    path("upload/", upload_csv),
    path("history/", upload_history),
    path("report/pdf/", download_report_pdf),
]
