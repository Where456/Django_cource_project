from main.models import Mailing, Client


def get_count_mailing():
    return Mailing.objects.count()


def get_active_mailing():
    return Mailing.objects.filter(status='START').count()


def get_unique_clients():
    return Client.objects.values('email').distinct().count()
