# musicmirror
Because I didn't like beets' Convert plugin

## About
musicmirror creates a mirrored directory structure of your music library, transcoded to a lossy format (currently hardcoded to ogg vorbis). It will also, by default, copy any cover art files found in the directories containing your source music.

musicmirror relies on accurate modification times of your files in order to not redo work that has already been done. If the modification time of an existing destination file is earlier than the modification time of the corresponding source file, the file will be re-transcoded or re-copied.

musicmirror will automatically delete files and folders that exist in your destination directory if they do not exist in your source directory. Be very careful of this!

## Dependencies
musicmirror does not require Python libraries from outside of the standard library, but it does require that you have SoX installed and visible in your PATH

## Usage
```
usage: musicmirror.py [-h] [-v] [--threads THREADS] [--no-cover-art] source_dir dest_dir

positional arguments:
  source_dir         Source music library path
  dest_dir           Dest music library path

optional arguments:
  -h, --help         show this help message and exit
  -v                 Verbosity
  --threads THREADS  Number of threads to transcode and copy with. Defaults to your cpu count
  --no-cover-art     Disables copying of cover art. This does not delete existing cover art
```

## TODO
* Remove files/directories in destination that are not in source
* Allow encoding libary to either OGG or OPUS
* Allow configuration of selected encoder with command arguments

## License
musicmirror is licences under the GNU Public License version 3 (GPLv3). See LICENSE for more details.
