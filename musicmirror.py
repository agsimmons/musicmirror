import argparse
from collections import namedtuple
import logging
import multiprocessing
import os.path
from pathlib import Path
import shutil
import subprocess


SOX_BIN = Path(shutil.which("sox"))
SOURCE_EXTENSIONS = [
    "flac",
    "mp3",
    "ogg",
    "opus",
]
COVER_ART_FILENAMES = [
    "Cover.jpg",
    "cover.jpg",
    "Cover.png",
    "cover.png",
    "Folder.jpg",
    "folder.jpg",
    "Folder.png",
    "folder.png",
]
OUTPUT_EXTENSION = ".ogg"
OGG_QUALITY = "2"


def transcode_audio(transcode_job):
    source_dir, dest_dir, audio_file = transcode_job
    
    # Determine the path of the output file
    audio_file_dest = (dest_dir / audio_file.relative_to(source_dir)).with_suffix(OUTPUT_EXTENSION)

    # Create any necessary directories
    audio_file_dest.parent.mkdir(parents=True, exist_ok=True)

    # Transcode file if needed
    if audio_file_dest.exists():
        if os.path.getmtime(audio_file_dest) < os.path.getmtime(audio_file):
            logging.debug(f"Transcoding: {audio_file} -> {audio_file_dest}")
            subprocess.run([str(SOX_BIN), str(audio_file), "-C", OGG_QUALITY, str(audio_file_dest)])
        else:
            logging.debug(f"Skipping {audio_file_dest} because it has not been modified")
    else:
        logging.debug(f"Transcoding: {audio_file} -> {audio_file_dest}")
        subprocess.run([str(SOX_BIN), str(audio_file), "-C", OGG_QUALITY, str(audio_file_dest)])


def copy_cover_art(cover_art_job):
    source_dir, dest_dir, cover_art_file = cover_art_job

    cover_art_dest = (dest_dir / cover_art_file.relative_to(source_dir))

    if cover_art_dest.parent.exists():
        if cover_art_dest.exists():
            if os.path.getmtime(cover_art_dest) < os.path.getmtime(cover_art_file):
                logging.debug(f"Copying: {cover_art_file} -> {cover_art_dest}")
                shutil.copy(cover_art_file, cover_art_dest)
            else:
                logging.debug(f"Skipping {cover_art_dest} because it has not been modified")
        else:
            logging.debug(f"Copying: {cover_art_file} -> {cover_art_dest}")
            shutil.copy(cover_art_file, cover_art_dest)


def discover_audio_files(source_dir):
    logging.info("Discovering audio files in source_dir...")

    audio_files = set()
    for ext in SOURCE_EXTENSIONS:
        audio_files.update(
            source_dir.glob(f"**/*.{ext}")
        )

    return audio_files


def discover_cover_art_files(source_dir):
    logging.info("Discovering cover art files in source_dir...")

    cover_art_files = set()
    for file_name in COVER_ART_FILENAMES:
        cover_art_files.update(
            source_dir.glob(f"**/{file_name}")
        )
    
    return cover_art_files


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", action="store_true", help="Verbosity")
    parser.add_argument("--threads", type=int, default=multiprocessing.cpu_count(), help="Number of threads to transcode and copy with. Defaults to your cpu count")
    parser.add_argument("--no-cover-art", action="store_true", help="Disables copying of cover art. This does not delete existing cover art")
    parser.add_argument("source_dir", help="Source music library path")
    parser.add_argument("dest_dir", help="Dest music library path")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.v:
        logging.basicConfig(level=logging.DEBUG)
    num_threads = args.threads

    source_dir = Path(args.source_dir)
    dest_dir = Path(args.dest_dir)

    audio_files = discover_audio_files(source_dir)

    transcode_jobs = [
        (source_dir, dest_dir, audio_file) for audio_file in audio_files
    ]

    logging.info("Transcoding audio...")
    with multiprocessing.Pool(num_threads) as p:
        p.map(transcode_audio, transcode_jobs)

    # Remove files in dest_dir that aren't in source_dir
    # TODO
    # dest_audio_files = discover_audio_files(dest_dir)

    
    if not args.no_cover_art:
        cover_art_files = discover_cover_art_files(source_dir)
        cover_art_jobs = [
            (source_dir, dest_dir, cover_art_file) for cover_art_file in cover_art_files
        ]
        logging.info("Copying album art...")
        with multiprocessing.Pool(num_threads) as p:
            p.map(copy_cover_art, cover_art_jobs)


if __name__ == "__main__":
    main()
