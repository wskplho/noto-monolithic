#!/usr/bin/python
#
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Quick summary of ttf files in noto file tree"""

__author__ = "dougfelt@google.com (Doug Felt)"

import argparse
import os
import os.path
import re
import sys

from fontTools import ttLib

import noto_lint

def get_largest_cmap(font):
  cmap_table = font['cmap']
  cmap = None
  for table in cmap_table.tables:
    tup = (table.format, table.platformID, table.platEncID)
    if tup == (4, 3, 1):
      # Continue scan because we prefer the other cmap if it exists.
      cmap = table.cmap
    elif tup == (12, 3, 10):
      # Stop scan if we find this cmap. Should be strictly larger than the other.
      cmap = table.cmap
      break
  return cmap

def cmap_count(font):
  return len(get_largest_cmap(font))

def summarize_file(root, path):
  font = ttLib.TTFont(path)

  relpath = path[len(root) + 1:]
  size = os.path.getsize(path)
  version = noto_lint.printable_font_revision(font)
  num_glyphs = len(font.getGlyphOrder())
  full_name = noto_lint.name_records(font)[4]
  cmap = set(get_largest_cmap(font).keys()) # copy needed? what's the lifespan?
  num_chars = len(cmap)
  return (relpath, version, full_name, size, num_glyphs, num_chars, cmap)

def summarize(root):
  result = []
  for parent, _, files in os.walk(root):
    for f in sorted(files):
      if f.endswith('.ttf'):
        result.append(summarize_file(root, os.path.join(parent, f)))
  return result


def print_tup(tup, short):
  def to_str(idx, val):
    if type(val) == type(set()):
      result = noto_lint.printable_unicode_range(val)
    else:
      result = str(val)
    if ' ' in result:
      result = '"%s"' % result
    return result
  line = [to_str(idx, val) for idx, val in enumerate(tup)
                    if not (short and (idx == 3 or idx == 6))]
  print '\t'.join(line)

def print_summary(summary_list, short):
  labels = ('path', 'version', 'name', 'size', 'num_glyphs', 'num_chars', 'cmap')
  print_tup(labels, short)
  for tup in summary_list:
    print_tup(tup, short)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', help='root of directory tree')
    parser.add_argument('-s', '--short', help='shorter summary format',
                        action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.root):
      print '%s does not exist or is not a directory' % args.root
    else:
      root = os.path.abspath(args.root)
      print root
      print_summary(summarize(root), args.short)

if __name__ == "__main__":
    main()
