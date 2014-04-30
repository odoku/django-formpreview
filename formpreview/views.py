# coding=utf8
from __future__ import unicode_literals

from types import MethodType
import uuid
import warnings

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.forms import models as model_forms
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormMixin
from django.utils.safestring import mark_safe

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
CACHE_KEY_FIELD = 'cache_key'


def _contribute_to_form(form):
    def preview_as_table(self):
        rows = []
        template = '<tr><th>{0}</th><td>{1}</td></tr>'
        for field in self:
            if isinstance(field, forms.FileField):
                rows.append(template.format(field.label, field.data))
            else:
                rows.append(template.format(field.label_tag(), field.value()))
        return mark_safe('\n'.join(rows))
    form.preview_as_table = MethodType(preview_as_table, form, form.__class__)


class FormPreviewMixin(FormMixin):
    post_cache_class = get_post_cache_class()
    stage_field = STAGE_FIELD
    cache_key_field = CACHE_KEY_FIELD
    input_template = None
    preview_template = None

    def dispatch(self, request, *args, **kwargs):
        self.stage = request.POST.get(self.stage_field, STAGE_INPUT)
        self.stage = self.stage if self.stage in STAGES else STAGE_INPUT

        self.cache_key = self.get_cache_key()
        self.post_cache = self.post_cache_class(self.cache_key)

        return super(FormPreviewMixin, self).dispatch(request, *args, **kwargs)

    def get_cache_key(self):
        return self.request.POST.get(self.cache_key_field, uuid.uuid4().hex)

    def get_form_kwargs(self):
        kwargs = super(FormPreviewMixin, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.post_cache.POST,
                'files': self.post_cache.FILES,
            })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FormPreviewMixin, self).get_context_data(**kwargs)
        context['stage_field'] = self.stage_field
        context['stage'] = self.stage
        context['cache_key_field'] = self.cache_key_field
        context['cache_key'] = mark_safe('<input type="hidden" name="{0}" value="{1}">'.format(
            self.cache_key_field,
            self.cache_key
        ))
        return context

    def form_valid(self, form):
        if self.stage == STAGE_INPUT:
            return self.input(form)
        if self.stage == STAGE_PREVIEW:
            _contribute_to_form(form)
            return self.preview(form)
        if self.stage == STAGE_POST:
            return self.done(form)
        else:
            raise ValueError()

    def form_invalid(self, form):
        self.stage = STAGE_INPUT
        return self.input(form)

    def input(self, form):
        self.template_name = self.input_template
        return self.render_to_response(self.get_context_data(form=form))

    def preview(self, form):
        self.template_name = self.preview_template
        return self.render_to_response(self.get_context_data(form=form))

    def done(self, form):
        self.post_cache.clear()
        return HttpResponseRedirect(self.get_success_url())


class ModelFormPreviewMixin(FormPreviewMixin, SingleObjectMixin):
    """
    A mixin that provides a way to show and handle a modelform in a request.
    """
    fields = None

    def get_form_class(self):
        """
        Returns the form class to use in this view.
        """
        if self.form_class:
            return self.form_class
        else:
            if self.model is not None:
                # If a model has been explicitly provided, use it
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                # If this view is operating on a single object, use
                # the class of that object
                model = self.object.__class__
            else:
                # Try to get a queryset and extract the model class
                # from that
                model = self.get_queryset().model

            if self.fields is None:
                warnings.warn("Using ModelFormPreviewMixin (base class of %s) without "
                              "the 'fields' attribute is deprecated." % self.__class__.__name__,
                              PendingDeprecationWarning)

            return model_forms.modelform_factory(model, fields=self.fields)

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ModelFormPreviewMixin, self).get_form_kwargs()
        kwargs.update({'instance': self.object})
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied URL.
        """
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to.  Either provide a url or define"
                    " a get_absolute_url method on the Model.")
        return url

    def done(self, form):
        self.object = form.save()
        return super(ModelFormPreviewMixin, self).done(form)


class ProcessFormView(View):
    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.input(form)

    def post(self, request, *args, **kwargs):
        if self.stage == STAGE_PREVIEW:
            self.post_cache.save(request)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BaseFormView(FormPreviewMixin, ProcessFormView):
    pass


class FormView(TemplateResponseMixin, BaseFormView):
    pass


class BaseCreateView(ModelFormPreviewMixin, ProcessFormView):
    def get(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(BaseCreateView, self).post(request, *args, **kwargs)


class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
    template_name_suffix = '_form'


class BaseUpdateView(ModelFormPreviewMixin, ProcessFormView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(BaseUpdateView, self).post(request, *args, **kwargs)


class UpdateView(SingleObjectTemplateResponseMixin, BaseUpdateView):
    template_name_suffix = '_form'
