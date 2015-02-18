#!/usr/bin/python
# Copyright 2015 Google, Inc. All Rights Reserved.
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
#
# Google Author(s): Doug Felt

import argparse
import os
import sys

import add_svg_glyphs

def do_generate_test_html(fontname, htmlname, pairs, verbose):
  header = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style type="text/css">
@font-face { font-family: foo; src: url("%s") }
body { font-family: sans-serif; font-size: 24px }
th { text-align:right; font-family:monospace }
td { font-family: foo, sans-serif }
</style>
</head>"""

  body_head = r"""<body>
<p>Test for SVG glyphs in %s.
<p>This page is for Firefox&nbsp;26 and later; it uses the "unified"
<a href="http://lists.w3.org/Archives/Public/public-svgopentype/2013Jul/0003.html">SVG-in-OpenType format</a>.
<table>"""

  table_line = r'<tr><th>%s<td>%s'

  body_tail = r"""</table>
</body>
</html>
"""

  lines = [header % fontname]
  lines.append(body_head % fontname)
  for glyphstr, _ in pairs:
    name_parts = []
    text_parts = []
    for cp in glyphstr:
      hex_str = hex(ord(cp))
      name_parts.append(hex_str)
      text_parts.append('&#x%s;' % hex_str[2:])
    name = ' '.join(name_parts)
    text = ''.join(text_parts)
    lines.append(table_line % (name, text))
  lines.append(body_tail)
  output = '\n'.join(lines)
  with open(htmlname, 'w') as fp:
    fp.write(output)
  if verbose > 0:
    print 'wrote %s for font %s' % (htmlname, fontname)

def main(argv):
  usage = """This will search for files that have image_prefix followed by one or more
      hex numbers (separated by underscore if more than one), and end in ".svg".
      For example, if image_prefix is "icons/u", then files with names like
      "icons/u1F4A9.svg" or "icons/u1F1EF_1F1F5.svg" will be found.
      It assumes these form the character repertoire of svg glyphs in the provided file,
      and generates an html file to display these glyphs."""

  parser = argparse.ArgumentParser(
      description='Generate html test file for font.', epilog=usage)
  parser.add_argument('font_file', help='font file name with extension.')
  parser.add_argument('html_file', help='Output html file name.')
  parser.add_argument('image_prefix', help='Location and prefix of image files.')
  parser.add_argument('-q', '--quiet', dest='v', help='quiet operation.',
                      action='store_const', const=0)
  parser.add_argument('-v', '--verbose', dest='v', help='verbose operation.', default=1,
                      action='store_const', const=2)
  args = parser.parse_args(argv)

  # find out the right way to do this
  if args.v == None:
    args.v = 1

  pairs = add_svg_glyphs.collect_glyphstr_file_pairs(args.image_prefix, 'svg', args.v)
  add_svg_glyphs.sort_glyphstr_tuples(pairs)
  do_generate_test_html(args.font_file, args.html_file, pairs, args.v)

if __name__ == '__main__':
  main(sys.argv[1:])
