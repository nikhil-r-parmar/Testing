# AI Vocal Separator Web App

A beginner-friendly Django project that lets a user upload one audio file, run Demucs on CPU, and download two outputs:
- vocals
- instrumental

This project is made for local learning, demos, and college-level use. It keeps the architecture small and readable: one Django project, one Django app, SQLite, server-rendered templates, and subprocess-based Demucs integration.

## How this project works

1. The user opens the homepage.
2. The user uploads one audio file (`.mp3` or `.wav`).
3. Django validates the file and saves it in `media/uploads/`.
4. The backend runs Demucs with a Python `subprocess` call.
5. Demucs writes separated stems into `media/output/`.
6. The app finds the vocals file and creates or picks an instrumental result.
7. The result page shows status, previews, and download links.

## Project structure

```text
ai-vocal-separator-web-app/
├── ai_vocal_separator/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── separator/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html
│   └── separator/
│       ├── home.html
│       └── result.html
├── static/
│   └── css/
│       └── style.css
├── media/
│   ├── output/
│   │   └── .gitkeep
│   └── uploads/
│       └── .gitkeep
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Requirements

- Python 3.10+
- ffmpeg installed and available in PATH
- Demucs installed in the same Python environment or accessible from the command line

Common setup commands:

```bash
conda install -c conda-forge ffmpeg
python -m pip install -U demucs SoundFile
```

Then install the Django app requirements:

```bash
python -m pip install -r requirements.txt
```

## Local setup

1. Create and activate a virtual environment.
2. Install the requirements from `requirements.txt`.
3. Install Demucs and SoundFile.
4. Install ffmpeg.
5. Copy `.env.example` values into your own environment if you want custom settings.
6. Run migrations.
7. Start the server.

Example:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scriptsctivate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install packages:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -U demucs SoundFile
```

Run database setup:

```bash
python manage.py migrate
```

Run the app:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Run instructions

Functional flow:

1. Open the homepage.
2. Upload one `.mp3` or `.wav` file.
3. Click **Separate Audio**.
4. Wait for Demucs to finish on CPU.
5. Preview and download `vocals` and `instrumental`.

## Demucs behavior

The app runs a command similar to:

```bash
demucs -d cpu --two-stems vocals -o media/output <your_audio_file>
```

Why this is useful:
- `--two-stems vocals` usually gives `vocals.wav` and `no_vocals.wav`.
- If naming varies, the code searches the output folder carefully.
- If a `no_vocals` file is not found but other stems exist, the service tries to build an instrumental mix from non-vocal stems.

## Error handling included

The app handles:
- invalid file type
- missing uploaded file
- missing ffmpeg
- missing Demucs installation
- Demucs subprocess failure
- output folder not found
- output files not found
- audio-mix fallback failure

## Windows notes

This project avoids Linux-only shell scripts. It uses Python `pathlib`, Django file handling, and `subprocess.run([...])`, so it is easier to run on Windows.

Important:
- Make sure `ffmpeg` works in Command Prompt or PowerShell.
- Make sure `demucs --help` works in the same environment where Django runs.
- Long processing time on CPU is normal for large audio files.

## Deployment notes

This version is intended for local development first.

For a simple deployment later:
- set `DEBUG=False`
- update `ALLOWED_HOSTS`
- serve static files properly
- use persistent file storage if needed
- keep file size limits reasonable
- understand that CPU-only separation may be slow on low-resource hosting

This is not meant for heavy public traffic or multi-user production workloads.

## Limitations

- CPU processing can be slow.
- Large audio files may take significant time.
- The request waits for Demucs to finish; there is no background queue in version 1.
- This is single-user/demo-friendly, not production-scale.

## Troubleshooting

### 1. `ffmpeg` not found
Make sure `ffmpeg` is installed and available in PATH.

Test:

```bash
ffmpeg -version
```

### 2. `demucs` not found
Install Demucs in your active environment.

Test:

```bash
demucs --help
```

If that fails, try:

```bash
python -m demucs --help
```

### 3. Upload works but result files are missing
Possible reasons:
- Demucs failed internally.
- The output path is different than expected.
- The file format could not be decoded.

Check the error shown on the result page and terminal logs.

### 4. MP3 file fails
Usually this means ffmpeg is missing or not configured correctly.

### 5. Slow processing
Demucs on CPU is slower than GPU. Start with short audio clips while testing.

## Future improvements

- Add optional background processing for longer files.
- Add waveform/progress UI.
- Add cleanup jobs for old media files.
- Add file size limits in settings and form validation.
- Add model selection later, such as different Demucs variants.

## How to rebuild this from scratch

A simple learning roadmap:

1. Learn basic Django project/app structure.
2. Build a plain file upload form with Django forms.
3. Save files into `MEDIA_ROOT`.
4. Learn `subprocess.run()` with a simple command.
5. Replace the simple command with Demucs.
6. Read output files from a folder and show them in a template.
7. Add error handling for missing tools and failed outputs.
8. Clean the UI with templates and static CSS.

## Version note

This is version 1, designed for demo, practice, and college project use.
