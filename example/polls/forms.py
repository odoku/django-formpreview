from django import forms

from models import Poll


class PollModelForm(forms.ModelForm):
    class Meta:
        model = Poll


class PollForm(forms.Form):
    question = forms.CharField(max_length=200)
    image = forms.ImageField(required=False)

    def save(self):
        poll = Poll(**self.cleaned_data)
        poll.save()
        return poll
