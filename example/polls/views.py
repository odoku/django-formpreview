from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView
from formpreview.views import CreateView, FormView, UpdateView

from forms import PollForm, PollModelForm
from models import Poll


class IndexView(ListView):
    queryset = Poll.objects.order_by('-pk')
    template_name = 'index.html'

index = IndexView.as_view()


class PollFormView(FormView):
    form_class = PollForm
    form_template = 'input.html'
    preview_template = 'preview.html'
    success_url = reverse_lazy('index')

    def done(self, form):
        form.save()
        return super(PollFormView, self).done(form)

form = PollFormView.as_view()


class PollCreateView(CreateView):
    form_class = PollModelForm
    form_template = 'input.html'
    preview_template = 'preview.html'
    success_url = reverse_lazy('index')

create = PollCreateView.as_view()


class PollUpdateView(UpdateView):
    queryset = Poll.objects.all()
    form_class = PollModelForm
    form_template = 'input.html'
    preview_template = 'preview.html'
    success_url = reverse_lazy('index')

update = PollUpdateView.as_view()
