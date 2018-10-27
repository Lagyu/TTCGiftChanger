from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.mail import send_mail, EmailMessage
# Create your views here.
from .models import Event, Gift
from django.utils import timezone
import uuid
from .ttc_cycle import ttc_algorithm
import os
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

    # subject = "TTCプレゼント交換 イベント登録完了"
    # message = "参加者ログイン用URLとか送る。"
    # from_email = "piyopiyo@example.com"
    # to = [request.POST["email"]]
    # bcc = ["piyopiyopiyo@example.com"]

    # if os.getenv('GAE_INSTANCE'):
    #     from google.appengine.api import mail
    #     mail.send_mail(sender="noreply@piyo-220609.appspot.com",
    #                    to=to,
    #                    subject=subject,
    #                    body=message,)
    #
    # else:
    #
    #     email = EmailMessage(subject, message, from_email, to, bcc)
    #     email.send()

    # for Google App Engine
    return HttpResponseRedirect(reverse("giftchanger:register_completed", args=(event.event_id,)))


class AdminEditView(generic.DetailView):
    model = Event
    template_name = "giftchanger/admin_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        gifts = Gift.objects.filter(parent_event=context["event"])

        gift_registered_num = len(gifts)
        gift_finished_num = len(gifts.exclude(gift_title__exact=""))

        if gift_registered_num == context["event"].number_of_gifts:
            available_bool = True
            for gift in gifts:
                available_bool = available_bool and gift.preference_list_str
            context['match_available'] = available_bool
        else:
            context["match_available"] = False

        context["gift_registered_num"] = gift_registered_num
        context["gift_finished_num"] = gift_finished_num


        return context


class RegisterCompletedView(generic.DetailView):
    model = Event
    template_name = "giftchanger/admin_register_completed.html"


def user_login_post(request):
    event = Event.objects.get(
        event_date=request.POST.get("event_date"),
        event_name=request.POST.get("event_name")
    )
    return HttpResponseRedirect(reverse("giftchanger:user_login_confirm", args=(event.event_id,)))


# class UserLoginConfirmView(generic.DetailView):
#     model = Event
#     template_name = "giftchanger/user_login_confirm.html"

def ttc_result_post(request, pk):
    event = Event.objects.get(event_id=str(pk))
    gifts_queryset = Gift.objects.filter(parent_event=event)
    if len(gifts_queryset) == event.number_of_gifts:
        preferences = {}
        for gift in gifts_queryset:
            if len(json.loads(gift.preference_list_str)) == event.number_of_gifts:
                preferences[gift.id] = json.loads(gift.preference_list_str)
        if len(preferences) == event.number_of_gifts:

            # print(preferences)
            # result_str = ""
            result_list = ttc_algorithm(preferences)

            for list1 in result_list:
                for list2 in list1:
                    for i in range(len(list2)):
                        list2[i] = gifts_queryset.get(id=list2[i]).user_name

            for list1 in result_list:
                for i in range(len(list1)):
                    list1[i] = str(list1[i]).replace(",", " → ")

            result_str = json.dumps(result_list[0], ensure_ascii=False).replace('"', "").replace("'", "")

            event.result = result_str
            event.save()

            return HttpResponseRedirect(reverse("giftchanger:event_result", args=(event.event_id, )))


class EventResultView(generic.DetailView):
    model = Event
    template_name = "giftchanger/event_result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        result_str = context["event"].result
        context["result"] = result_str

        return context


def user_login_confirm(request, pk):
    event = Event.objects.get(
        event_id=pk
    )
    num_gifts = len(Gift.objects.filter(parent_event=event))
    print(num_gifts)
    if num_gifts < event.number_of_gifts:
        return render(request, "giftchanger/user_login_confirm.html", context={"event": event, "current_num_gifts": str(num_gifts)})

    else:
        return render(request, "giftchanger/user_login_failure.html", context={"event": event, "current_num_gifts": str(num_gifts)})


def create_user_post(request, event_id):
    event = Event.objects.get(event_id=event_id)
    num_gifts = len(Gift.objects.filter(parent_event=event))
    if num_gifts < event.number_of_gifts:
        gift = Gift.objects.get_or_create(
            parent_event=event,
            user_name=request.POST["user_name"],
        )[0]
        return HttpResponseRedirect(reverse("giftchanger:edit_gift", args=(event_id, gift.id)))
    else:
        gift = get_object_or_404(Gift, parent_event=event, user_name=request.POST["user_name"])
        return HttpResponseRedirect(reverse("giftchanger:edit_gift", args=(event_id, gift.id)))


def edit_gift_post(request, event_id, pk):
    event = Event.objects.get(event_id=event_id)
    gift = Gift.objects.get(
        parent_event=event,
        id=pk,
    )
    gift.gift_title = request.POST["gift_title"]
    gift.gift_description = request.POST["gift_description"]
    gift.save()
    return HttpResponseRedirect(reverse("giftchanger:edit_preferences_check", args=(event_id, gift.id)))


class GiftEditView(generic.DetailView):
    model = Gift
    template_name = "giftchanger/gift_edit.html"


def preference_edit_check(request, event_id, pk):
    event = Event.objects.get(event_id=event_id)
    gifts = Gift.objects.filter(parent_event=event)
    gift_registered_num = len(gifts)
    gift_finished_num = len(gifts.exclude(gift_title__exact=""))
    if event.number_of_gifts == gift_registered_num:
        return HttpResponseRedirect(reverse("giftchanger:edit_preferences", args=(event_id, pk)))
    else:
        return render(request, "giftchanger/preference_check.html", context={"event": event, "gift_registered_num": gift_registered_num, "gift_finished_num": gift_finished_num})


def preference_edit(request, event_id, pk):
    parent_event = Event.objects.get(event_id=event_id)
    gifts_list = Gift.objects.filter(parent_event=parent_event)

    # create json to send and store in the LocalStorage.
    gifts_json = json.dumps([{'key': gift.id,
                              'value': {"title": gift.gift_title, "name": gift.user_name,
                                        "description": gift.gift_description}}
                             for gift in gifts_list], separators=(',', ':'))
    context = {"gifts_json": gifts_json, "event_id": event_id, "gift_id": pk, "show_name": parent_event.show_name_before_match, "number_of_gifts": parent_event.number_of_gifts}
    response = render(request, "giftchanger/preference_edit.html", context)

    selected_cookie_key_name = "selected_preference_list_" + str(event_id)+"_"+str(pk)
    not_selected_cookie_key_name = "not_selected_preference_list_" + str(event_id)+"_"+str(pk)

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
    selected_cookie_key_name = "selected_preference_list_" + str(event_id) + "_" + str(pk)
    not_selected_cookie_key_name = "not_selected_preference_list_" + str(event_id) + "_" + str(pk)

    if selected_cookie_key_name in request.COOKIES:
        preference_list = json.loads(request.COOKIES[selected_cookie_key_name])
        not_selected_list = json.loads(request.COOKIES[not_selected_cookie_key_name])

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
