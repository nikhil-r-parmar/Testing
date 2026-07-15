from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from .forms import AudioUploadForm


class AudioUploadFormTests(TestCase):
    def test_rejects_invalid_extension(self):
        file = SimpleUploadedFile('demo.txt', b'hello', content_type='text/plain')
        form = AudioUploadForm(files={'audio_file': file})
        self.assertFalse(form.is_valid())
