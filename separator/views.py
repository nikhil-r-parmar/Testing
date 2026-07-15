from django.shortcuts import render
from .forms import AudioUploadForm
from .services import DemucsSeparatorService, SeparationError


def home(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            service = DemucsSeparatorService()
            try:
                result = service.process(form.cleaned_data['audio_file'])
                return render(request, 'separator/result.html', {'result': result})
            except SeparationError as exc:
                return render(
                    request,
                    'separator/result.html',
                    {
                        'result': {
                            'original_name': request.FILES.get('audio_file').name if request.FILES.get('audio_file') else 'Unknown file',
                            'upload_relative_path': None,
                            'vocals_relative_path': None,
                            'instrumental_relative_path': None,
                            'success': False,
                            'message': str(exc),
                        }
                    }
                )
    else:
        form = AudioUploadForm()

    return render(request, 'separator/home.html', {'form': form})
