from django import forms


class JoinForm(forms.Form):
    email = forms.EmailField(label='email')


class ChallengeForm(forms.Form):
    opponent = forms.IntegerField(min_value=0, label='opponent')
    datetime = forms.DateTimeField(label='datetime')
