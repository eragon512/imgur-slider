from django import forms

class AlbumUrlForm(forms.Form):
    album_url = forms.URLField(label='Enter the Imgur URL here', max_length=100)
