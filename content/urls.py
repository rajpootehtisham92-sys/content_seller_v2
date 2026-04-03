from django.urls import path
from . import views

urlpatterns = [
    path('', views.content_list, name='content_list'),
    path('add/', views.add_content, name='add_content'),
    path('buy/<int:content_id>/', views.buy_content, name='buy_content'),
    path('payout-info/', views.creator_payout_info, name='creator_payout_info'),
    path('buyer/dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('creator/dashboard/', views.creator_dashboard, name='creator_dashboard'),
    path('review/<int:order_id>/', views.add_review, name='add_review'),
    path('report/<int:content_id>/', views.report_content, name='report_content'),
    path('detail/<int:content_id>/', views.content_detail, name='content_detail'),
    path('withdraw/', views.request_withdrawal, name='request_withdrawal'),
    path('withdrawals/', views.withdrawal_history, name='withdrawal_history'),
    path('videos/<int:content_id>/', views.view_content_videos, name='view_content_videos'),
    path('download/<int:content_id>/', views.download_zip, name='download_zip'),
]