from django import forms
from django.utils.safestring import mark_safe
from .Models import *

class InputForm(forms.Form):
	#first_name = forms.CharField(max_length = 200) 
	#last_name = forms.CharField(max_length = 200) 
	#roll_number = forms.IntegerField(help_text = "Enter 6 digit roll number") 
	#password = forms.CharField(widget = forms.PasswordInput())
	nickname = forms.CharField(max_length = 45)
	subboard = forms.CharField(max_length = 1, widget=forms.HiddenInput())
	title = forms.CharField(max_length = 45)
	content = forms.CharField(max_length = 1024, widget=forms.Textarea)
	img = forms.ImageField(required=False, label="Optional Picture")
class CommentForm(forms.Form):
	nickname = forms.CharField(max_length = 45)
	content = forms.CharField(max_length = 256, widget=forms.Textarea)
	postId = forms.IntegerField(widget=forms.HiddenInput())
	img = forms.ImageField(required=False, label="Optional Picture")