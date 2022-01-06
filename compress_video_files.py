#!/usr/bin/env python3 

import os

from absl import app
from absl import flags
import ffmpeg


FLAGS = flags.FLAGS
flags.DEFINE_bool('dry_run', True, 'Run the script in dry run mode.')
flags.DEFINE_bool('skip_remove', True, 'Skip removing the compressed videos.')
flags.DEFINE_string('videos_directory', None, 'The directory that directly contains videos to compress.')

flags.mark_flag_as_required("videos_directory")

COMPRESSED_DIRECTORY_NAME = 'compressed'
MP4_SUFFIX = '.mp4'


def GetAvailableCompressedPath(directory_path, file_base_name, suffix):
  candidate_path = os.path.join(directory_path, f'{file_base_name}{suffix}')
  counter = 0
  while os.path.exists(candidate_path):
    counter += 1
    candidate_path = os.path.join(directory_path, f'{file_base_name} ({counter}){suffix}')
  return candidate_path


def Main(argv):
  print(f'Running the script with dry_run = {FLAGS.dry_run}, '
        f'directory = {FLAGS.videos_directory}, '
        f'skip_remove = {FLAGS.skip_remove}.')
  absolute_videos_directory = os.path.abspath(FLAGS.videos_directory)
  if not os.path.exists(absolute_videos_directory):
    raise Exception(f'Video directory {absolute_videos_directory} does not exist.')
  compressed_videos_directory = os.path.join(absolute_videos_directory, COMPRESSED_DIRECTORY_NAME)
  if os.path.exists(compressed_videos_directory) and not os.path.isdir(compressed_videos_directory):
    raise Exception(f'The compressed directory path exists, but it is not a directory!')
  if not os.path.exists(compressed_videos_directory) and not FLAGS.dry_run:
    os.mkdir(compressed_videos_directory)
  contents = os.listdir(absolute_videos_directory)
  for content_name in contents:
    abs_content_path = os.path.join(absolute_videos_directory, content_name)
    if not os.path.isfile(abs_content_path):
      print(f'Skipping non-file {abs_content_path}')
      continue
    if not content_name.endswith(MP4_SUFFIX):
      print(f'Skipping non-mp4 file {abs_content_path}')
      continue
    compressed_path_base_name = content_name[:-len(MP4_SUFFIX)]
    compressed_path = GetAvailableCompressedPath(compressed_videos_directory, compressed_path_base_name, MP4_SUFFIX)
    print(f'Compressing input {abs_content_path} to output {compressed_path}')
    if not FLAGS.dry_run:
      ffmpeg.input(abs_content_path).output(compressed_path, vcodec='libx265', crf='28').run()
      if not FLAGS.skip_remove:
        os.remove(abs_content_path)

if __name__ == '__main__':
  app.run(Main)
