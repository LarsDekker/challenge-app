from django import forms


class JoinForm(forms.Form):
    email = forms.EmailField(label='email')


class ChallengeForm(forms.Form):
    opponent = forms.IntegerField(min_value=0, label='opponent')
    datetime = forms.DateTimeField(label='datetime')


class RegisterForm(forms.Form):
    email = forms.EmailField(label='email')
    display_name = forms.CharField(min_length=4, label="Display name")
    password = forms.CharField(widget=forms.PasswordInput(), min_length=6, max_length=120)
    repeat_password = forms.CharField(widget=forms.PasswordInput(), min_length=6, max_length=120)

