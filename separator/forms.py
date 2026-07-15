from pathlib import Path
from django import forms


class AudioUploadForm(forms.Form):
    audio_file = forms.FileField(
        label='Choose audio file',
        widget=forms.ClearableFileInput(attrs={'accept': '.mp3,.wav,audio/mpeg,audio/wav'})
    )

    allowed_extensions = {'.mp3', '.wav'}

    def clean_audio_file(self):
        audio_file = self.cleaned_data['audio_file']
        suffix = Path(audio_file.name).suffix.lower()
        if suffix not in self.allowed_extensions:
            raise forms.ValidationError('Only MP3 and WAV files are allowed.')
        return audio_file
