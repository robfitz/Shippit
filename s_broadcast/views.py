from django.http import HttpResponse

from s_broadcast.models import Subscription


def subscribe(request, subscription_title):

    if request.method != "POST":
        return HttpResponse("Error: access newsletter via post w/ request.POST.get('email')")

    email = request.POST.get("email", None)

    subscription, created = Subscription.objects.get_or_create(title=subscription_title)

    subscription.subscribe(email)

    return HttpResponse("ok")


