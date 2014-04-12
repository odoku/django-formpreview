from django import forms

from models import Poll


class PollModelForm(forms.ModelForm):
    class Meta:
        model = Poll


class PollForm(forms.Form):
    question = forms.CharField(max_length=200)
    main_image = forms.ImageField()
    sub_image = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(PollForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['question'].initial = self.instance.question
            self.fields['image'].initial = self.instance.image

    def save(self, commit=True):
        poll = self.instance if self.instance else Poll()

        poll.question = self.cleaned_data['question']

        if self.cleaned_data['main_image'] is False:
            poll.main_image = None
        else:
            poll.main_image = self.cleaned_data['main_image']

        if self.cleaned_data['sub_image'] is False:
            poll.sub_image = None
        else:
            poll.sub_image = self.cleaned_data['sub_image']

        if commit:
            poll.save()

        return poll
