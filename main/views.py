from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from main.forms import ClientForm, MailingForm
from main.models import *
from main.services.services import MessageService, delete_task, send_mailing

from random import sample
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView, DeleteView
from blog.models import Post
from main.services.services2 import get_count_mailing, get_active_mailing, get_unique_clients


class IndexView(TemplateView):
    template_name = 'index.html'
    extra_context = {
        'title': 'HONDATA'
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_posts = list(Post.objects.all())
        context['random_post'] = sample(all_posts, min(3, len(all_posts)))
        context['count_mailing'] = get_count_mailing()
        context['active_mailing'] = get_active_mailing()
        context['unique_clients'] = get_unique_clients()

        return context


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    extra_context = {'title': 'Рассылки'}
    template_name = 'mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            queryset = Mailing.objects.all()
        else:
            queryset = Mailing.objects.filter(user=user)

        queryset = queryset.filter(is_published=True)
        return queryset


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing_form.html'
    success_url = reverse_lazy('main:mailing_list')

    def get_queryset(self):
        user = self.request.user
        mailing = Mailing.objects.all()
        if user.is_staff or user.is_superuser:
            queryset = mailing
        else:
            queryset = mailing.client.filter(user=user)
        return queryset

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.user = self.request.user
        mailing.status = 'CREATE'
        mailing.save()

        message_service = MessageService(mailing)
        send_mailing(mailing)
        message_service.create_task()
        mailing.status = 'START'
        mailing.save()

        return super(MailingCreateView, self).form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('main:mailing_list')


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing_confirm_delete.html'
    success_url = reverse_lazy('main:mailing_list')


def toggle_status(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    message_service = MessageService(mailing)
    if mailing.status == 'START' or mailing.status == 'CREATE':
        delete_task(mailing)
        mailing.status = 'FINISH'
    else:
        message_service.create_task()
        mailing.status = 'START'

    mailing.save()

    return redirect(reverse('main:mailing_list'))


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    extra_context = {'title': 'Клиенты'}
    template_name = 'client_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            queryset = Client.objects.all()
        else:
            queryset = Client.objects.filter(user=user)

        queryset = queryset.filter(is_active=True)
        return queryset


class ClientDetailView(LoginRequiredMixin, DetailView):
    template_name = 'client_detail.html'
    model = Client


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('main:client_list')
    template_name = 'client_form.html'

    def form_valid(self, form):
        client = form.save(commit=False)
        client.user = self.request.user
        client.save()
        return super(ClientCreateView, self).form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('main:client_list')
    template_name = 'client_form.html'


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('main:client_list')
    permission_required = 'mailing.delete_client'


class MailingLogListView(LoginRequiredMixin, ListView):
    model = MailingLogs
    template_name = 'mailinglogs_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Попытки рассылки"
        context['log_list'] = MailingLogs.objects.all()
        return context
