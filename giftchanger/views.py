from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.mail import send_mail, EmailMessage
# Create your views here.
from .models import Event, Gift
from django.utils import timezone
import uuid

import json

from django.urls import reverse, resolve
from django.views import generic


def admin_register_view(request):
    return render(request, "giftchanger/admin_register.html")


def admin_register_post(request):
    event = Event.objects.create(
        creation_date=timezone.now(),
        show_name_before_match=True if request.POST["show_name_before"] == "true" else False,
        show_name_after_match=True if request.POST["show_name_after"] == "true" else False,
        email=request.POST["email"],
        password=request.POST["password"],
        event_name=request.POST["event_name"],
        event_date=request.POST["event_date"],
        number_of_gifts=request.POST["number_of_gifts"],
        event_id=str(uuid.uuid4()),
        allow_picture=False if request.POST["allow_picture"] == "false" else True,
        force_picture=True if request.POST["allow_picture"] == "always" else False
    )
    subject = "TTCプレゼント交換 イベント登録完了"
    message = "参加者ログイン用URLとか送る。"
    from_email = "piyopiyo@example.com"
    to = [request.POST["email"]]
    bcc = ["piyopiyopiyo@example.com"]
    email = EmailMessage(subject, message, from_email, to, bcc)
    email.send()
    return HttpResponseRedirect(reverse("giftchanger:register_completed", args=(event.event_id,)))


class AdminEditView(generic.DetailView):
    model = Event
    template_name = "giftchanger/admin_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gifts_queryset = Gift.objects.filter(parent_event=context["event"])
        if len(gifts_queryset) == context["event"].number_of_gifts:
            available_bool = True
            for gift in gifts_queryset:
                available_bool = available_bool and gift.preference_list_str
            context['match_available'] = available_bool
        else:
            context["match_available"] = False

        return context


class RegisterCompletedView(generic.DetailView):
    model = Event
    template_name = "giftchanger/admin_register_completed.html"


class ResultCheckView(generic.DetailView):
    model = Event
    template_name = "giftchanger/event_result.html"


def user_login_post(request):
    event = Event.objects.get(
        event_date=request.POST.get["event_date"],
        event_name=request.POST.get["event_name"]
    )
    return HttpResponseRedirect(reverse("giftchanger:user_login_confirm", args=(event.event_id,)))


class UserLoginConfirmView(generic.DetailView):
    model = Event
    template_name = "giftchanger/user_login_confirm.html"


def create_user_post(request, event_id):
    gift = Gift.objects.get_or_create(
        parent_event=Event.objects.get(event_id=event_id),
        user_name=request.POST["user_name"],
    )[0]
    return HttpResponseRedirect(reverse("giftchanger:edit_gift", args=(event_id, gift.id)))


def edit_gift_post(request, event_id, pk):
    gift = Gift.objects.get(
        parent_event=Event.objects.get(event_id=event_id),
        id=pk,
    )
    gift.gift_title = request.POST["gift_title"]
    gift.gift_description = request.POST["gift_description"]
    gift.save()

    return HttpResponseRedirect(reverse("giftchanger:edit_preferences", args=(event_id, gift.id)))


class GiftEditView(generic.DetailView):
    model = Gift
    template_name = "giftchanger/gift_edit.html"


def preference_edit(request, event_id, pk):
    parent_event = Event.objects.get(event_id=event_id)
    gifts_list = Gift.objects.filter(parent_event=parent_event)

    # create json to send and store in the LocalStorage.
    gifts_json = json.dumps([{'key': gift.id,
                              'value': {"title": gift.gift_title, "name": gift.user_name,
                                        "description": gift.gift_description}}
                             for gift in gifts_list], separators=(',', ':'))
    context = {"gifts_json": gifts_json, "event_id": event_id, "gift_name": pk, "show_name": parent_event.show_name_before_match, "number_of_gifts": parent_event.number_of_gifts}
    response = render(request, "giftchanger/preference_edit.html", context)

    selected_cookie_key_name = "selected_preference_list_" + str(event_id)
    not_selected_cookie_key_name = "not_selected_preference_list_" + str(event_id)

    if selected_cookie_key_name in request.COOKIES and request.COOKIES.get(selected_cookie_key_name):
        selected_list = json.loads(request.COOKIES.get(selected_cookie_key_name))
        not_selected_str = [gift.id for gift in gifts_list if gift.id not in selected_list]

    else:
        gift = Gift.objects.get(
            parent_event=Event.objects.get(event_id=event_id),
            id=pk
        )
        if gift.preference_list_str:
            try:
                selected_list = json.loads(gift.preference_list_str)
                selected_str = gift.preference_list_str
                not_selected_str = [gift.id for gift in gifts_list if gift.id not in selected_list]

            except json.JSONDecodeError as error_msg:
                selected_str = "[]"
                not_selected_str = str([gift.id for gift in gifts_list])

        else:
            selected_str = "[]"
            not_selected_str = str([gift.id for gift in gifts_list])

        response.set_cookie(selected_cookie_key_name, selected_str)
    response.set_cookie(not_selected_cookie_key_name, not_selected_str)

    return response


def preference_post(request, event_id, pk):
    gift = Gift.objects.get(
        parent_event=Event.objects.get(event_id=event_id),
        id=pk
    )
    selected_cookie_key_name = "selected_preference_list_" + str(event_id)
    not_selected_cookie_key_name = "not_selected_preference_list_" + str(event_id)
    print(request.COOKIES)

    if selected_cookie_key_name in request.COOKIES:
        preference_list = json.loads(request.COOKIES[selected_cookie_key_name])
        not_selected_list = json.loads(request.COOKIES[not_selected_cookie_key_name])
        print(preference_list)
        print(not_selected_list)

        if len(preference_list) == gift.parent_event.number_of_gifts:
            gift.preference_list_str = str(preference_list)
            gift.not_selected_list_str = str(not_selected_list)
            gift.save()

    return HttpResponseRedirect(reverse("giftchanger:preference_saved", args=(event_id, gift.id)))


class PreferenceSavedView(generic.DetailView):
    model = Gift
    template_name = "giftchanger/preference_saved.html"


# class PreferenceEditView(generic.ListView):
#     template_name = "giftchanger/preference_edit.html"
#     context_object_name = "gifts_list"
#
#     def get_queryset(self):
#         """returns all gifts registered for the event_id"""
#         return Gift.objects.filter(parent_event=Event.objects.get(event_id=self.kwargs.get("event_id")))


def view_event(request):
    pass
