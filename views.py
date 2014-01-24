# coding=utf8

from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from cache import get_post_cache_class


STAGE_INPUT = 'input'
STAGE_PREVIEW = 'preview'
STAGE_POST = 'post'
STAGES = {
    STAGE_INPUT: 'input',
    STAGE_PREVIEW: 'preview',
    STAGE_POST: 'post',
}

STAGE_FIELD = 'stage'


class FormPreview(FormView):
    post_cache_class = get_post_cache_class()
    stage_field = STAGE_FIELD
    form_template = None
    preview_template = None

    def dispatch(self, request, *args, **kwargs):
        self.stage = request.POST.get(self.stage_field, STAGE_INPUT)
        self.stage = self.stage if self.stage in STAGES else STAGE_INPUT

        key = self.get_post_cache_key()
        self.post_cache = self.post_cache_class(key)

        return super(FormPreview, self).dispatch(request, *args, **kwargs)

    def get_post_cache_key(self):
        session_key = self.request.session.session_key
        path = self.request.path
        return session_key + ':' + path

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.input(form)

    def post(self, request, *args, **kwargs):
        if self.stage == STAGE_PREVIEW:
            self.post_cache.save(request)
        return super(FormPreview, self).post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.post_cache.POST,
                'files': self.post_cache.FILES,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FormPreview, self).get_context_data(**kwargs)
        context['stage_field'] = self.stage_field
        context['stage'] = self.stage
        return context

    def form_valid(self, form):
        if self.stage == STAGE_INPUT:
            return self.input(form)
        if self.stage == STAGE_PREVIEW:
            return self.preview(form)
        if self.stage == STAGE_POST:
            return self.done(form)
        else:
            raise ValueError()

    def form_invalid(self, form):
        self.stage = STAGE_INPUT
        return self.input(form)

    def input(self, form):
        self.template_name = self.form_template
        return self.render_to_response(self.get_context_data(form=form))

    def preview(self, form):
        self.template_name = self.preview_template
        return self.render_to_response(self.get_context_data(form=form))

    def done(self, form):
        self.post_cache.clear()
        return HttpResponseRedirect(self.get_success_url())
