from django.urls import re_path
from . import views

app_name = 'crons'

urlpatterns = [
    re_path(r'^purge_old_messages$', views.PurgeOldMessages.as_view()),
    re_path(r'^apply_chat_updates$', views.ApplyChatUpdates.as_view()),
    re_path(r'^sync_member_ids$', views.SyncMemberIDs.as_view()),
    re_path(r'^prune_biz_chat$', views.PruneBusinessChat.as_view()),
    re_path(r'^owner_to_admin$', views.OwnerToAdmin.as_view()),
    re_path(r'^business_accounts$', views.BusinessAccounts.as_view()),
    re_path(r'^end_trials/(?P<days>[0-9]+)/$', views.EndTrialsCron.as_view()),
    re_path(r'^payout_partners/$', views.PayoutPartnersCron.as_view()),
]
