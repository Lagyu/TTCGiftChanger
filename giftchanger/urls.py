from django.urls import path
from . import views

from django.views.generic import TemplateView


app_name = "giftchanger"
urlpatterns = [
    path("", TemplateView.as_view(template_name="giftchanger/main.html"), name="top"),

    path("event_register", views.admin_register_view, name="event_register_view"),
    path("event_register_post/", views.admin_register_post, name="event_register_post"),
    path("register_completed/<uuid:pk>", views.RegisterCompletedView.as_view(), name="register_completed"),

    path("user_login/", TemplateView.as_view(template_name="giftchanger/user_login.html"), name="user_login"),
    path("user_login_post/", views.user_login_post, name="user_login_post"),
    path("<uuid:pk>/edit/", views.AdminEditView.as_view(), name="admin_edit"),

    path("<uuid:pk>/match_with_ttc/", views.ttc_result_post, name="matching_result_post"),
    path("<uuid:pk>/event_result/", views.EventResultView.as_view(), name="event_result"),

    path("user_login/<uuid:pk>/", views.user_login_confirm, name="user_login_confirm"),

    path("<uuid:event_id>/create_user_post/", views.create_user_post, name="create_user_post"),
    path("<uuid:event_id>/<int:pk>/edit_gift/", views.GiftEditView.as_view(), name="edit_gift"),
    path("<uuid:event_id>/<int:pk>/edit_gift_post/", views.edit_gift_post, name="edit_gift_post"),

    path("<uuid:event_id>/<int:pk>/preferences_check/", views.preference_edit_check, name="edit_preferences_check"),
    path("<uuid:event_id>/<int:pk>/edit_preferences/", views.preference_edit, name="edit_preferences"),
    path("<uuid:event_id>/<int:pk>/post_preferences/", views.preference_post, name="post_preferences"),
    path("<uuid:event_id>/<int:pk>/preference_saved/", views.PreferenceSavedView.as_view(), name="preference_saved"),

    path("view_event/<str:event_id>/", views.view_event, name="view_event"),


]

