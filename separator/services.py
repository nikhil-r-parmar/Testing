import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

import soundfile as sf
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename


class SeparationError(Exception):
    pass


@dataclass
class SeparationResult:
    original_name: str
    upload_relative_path: str | None
    vocals_relative_path: str | None
    instrumental_relative_path: str | None
    success: bool
    message: str


class DemucsSeparatorService:
    allowed_suffixes = {".mp3", ".wav"}

    def process(self, uploaded_file):
        original_name = uploaded_file.name
        safe_name = get_valid_filename(Path(original_name).name)
        suffix = Path(safe_name).suffix.lower()

        if suffix not in self.allowed_suffixes:
            raise SeparationError("Invalid file type. Please upload an MP3 or WAV file.")

        self._ensure_dependencies()

        unique_id = uuid.uuid4().hex[:8]
        stored_filename = f"{Path(safe_name).stem}_{unique_id}{suffix}"

        upload_relative_path = Path("uploads") / stored_filename
        upload_absolute_path = Path(settings.MEDIA_ROOT) / upload_relative_path
        upload_absolute_path.parent.mkdir(parents=True, exist_ok=True)

        with default_storage.open(str(upload_relative_path), "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        output_root = Path(settings.MEDIA_ROOT) / "output"
        output_root.mkdir(parents=True, exist_ok=True)

        command = [
            "demucs",
            "-d",
            "cpu",
            "--two-stems",
            "vocals",
            "-o",
            str(output_root),
            str(upload_absolute_path),
        ]

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError as exc:
            raise SeparationError("Demucs is not installed or not available in PATH.") from exc
        except Exception as exc:
            raise SeparationError(f"Unexpected error while starting Demucs: {exc}") from exc

        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip()
            raise SeparationError(f"Demucs failed to process the file. Details: {stderr}")

        result_dir = self._find_result_directory(output_root, upload_absolute_path.stem)
        vocals_file = self._find_vocals_file(result_dir)
        instrumental_file = self._find_instrumental_file(result_dir, vocals_file)

        if not vocals_file or not vocals_file.exists():
            raise SeparationError("Vocals output file was not found after processing.")

        if not instrumental_file or not instrumental_file.exists():
            raise SeparationError("Instrumental output file was not found after processing.")

        return SeparationResult(
            original_name=original_name,
            upload_relative_path=(Path("media") / upload_relative_path).as_posix(),
            vocals_relative_path=self._relative_media_path(vocals_file),
            instrumental_relative_path=self._relative_media_path(instrumental_file),
            success=True,
            message="Audio separated successfully.",
        )

    def _ensure_dependencies(self):
        if shutil.which("ffmpeg") is None:
            raise SeparationError("ffmpeg is missing. Install ffmpeg and make sure it is available in PATH.")

        if shutil.which("demucs") is None:
            raise SeparationError("Demucs is missing. Install it with: python -m pip install -U demucs SoundFile")

    def _find_result_directory(self, output_root: Path, upload_stem: str) -> Path:
        matching_dirs = []

        for path in output_root.rglob("*"):
            if path.is_dir() and path.name.startswith(upload_stem):
                matching_dirs.append(path)

        if not matching_dirs:
            raise SeparationError("Could not find the Demucs output directory.")

        matching_dirs.sort(key=lambda p: len(p.parts), reverse=True)
        return matching_dirs[0]

    def _find_vocals_file(self, result_dir: Path) -> Path | None:
        candidates = list(result_dir.rglob("*"))

        for path in candidates:
            if path.is_file() and path.suffix.lower() in {".wav", ".mp3"} and "vocal" in path.stem.lower():
                return path

        return None

    def _find_instrumental_file(self, result_dir: Path, vocals_file: Path | None) -> Path | None:
        candidates = [
            p for p in result_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in {".wav", ".mp3"}
        ]

        preferred_terms = ["no_vocals", "instrumental", "accompaniment"]
        for term in preferred_terms:
            for path in candidates:
                if term in path.stem.lower():
                    return path

        stem_map = {}
        for path in candidates:
            name = path.stem.lower()
            for key in ["drums", "bass", "other"]:
                if key in name:
                    stem_map[key] = path

        if {"drums", "bass", "other"}.issubset(stem_map.keys()):
            return self._mix_to_instrumental(result_dir, stem_map)

        remaining = [
            p for p in candidates
            if vocals_file is None or p.resolve() != vocals_file.resolve()
        ]

        if remaining:
            return remaining[0]

        return None

    def _mix_to_instrumental(self, result_dir: Path, stem_map: dict) -> Path:
        drums, sr1 = sf.read(stem_map["drums"])
        bass, sr2 = sf.read(stem_map["bass"])
        other, sr3 = sf.read(stem_map["other"])

        if not (sr1 == sr2 == sr3):
            raise SeparationError("Could not build instrumental because stem sample rates do not match.")

        min_len = min(len(drums), len(bass), len(other))
        instrumental = drums[:min_len] + bass[:min_len] + other[:min_len]

        output_path = result_dir / "instrumental.wav"
        sf.write(output_path, instrumental, sr1)
        return output_path

    def _relative_media_path(self, absolute_path: Path) -> str:
        relative = absolute_path.relative_to(settings.MEDIA_ROOT)
        return (Path("media") / relative).as_posix()