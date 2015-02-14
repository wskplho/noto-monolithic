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

import svg_cleaner

class SvgBuilder(object):

  def __init__(self, font_builder):
    font_builder.init_svg()

    self.font_builder = font_builder
    self.cleaner = svg_cleaner.SvgCleaner()

    font = font_builder.font
    self.font_height = font['hhea'].ascent - font['hhea'].descent
    self.font_upem = font['head'].unitsPerEm

  def add_from_filename(self, ustr, filename):
    with open(filename, "r") as fp:
      return self.add_from_doc(ustr, fp.read())

  def _get_int_px(self, val):
    if not val.lower().endswith('px'):
      raise "expected width or height ending in 'px' but got: %s" % val
    return int(val[:-2])

  def add_from_doc(self, ustr, svgdoc):
    """Cleans the svg doc, tweaks the root svg element's
    attributes, then updates the font.  ustr is the character or ligature
    string, svgdoc is the svg document xml.  The doc must have a single
    svg root element."""

    # Adding a glyph can generate additional default glyphs for components of
    # a ligature that are not already present.
    #
    # It is possible to add SVG images to a font that already has corresponding
    # glyphs.  If a glyph exists already, then its hmtx advance is assumed
    # valid.  Otherwise we will generate an advance based on the image's width
    # and scale factor.  Callers should ensure that glyphs for components of
    # ligatures are added before the ligatures themselves, otherwise glyphs
    # generated for missing ligature components will be assigned zero metrics
    # metrics that will not be overridden later.
    #
    # The svg element must have an id attribute of the form 'glyphNNN' where NNN
    # is the glyph id.  We capture the index of the glyph we're adding and write
    # it into the svg.
    #
    # We need to specify a transform attribute on the svg element to ensure it
    # is properly scaled and translated.  We expect the image has a width and
    # height specified by 'width' and 'height' attributes on the svg element,
    # and a top left at the origin. We generate a transform that places the
    # origin at the top left of the EM square and uniformly scales it to fit
    # both the font height (ascent - descent) and glyph advance if it is already
    # present.  The width and height attributes are not used by rendering, so
    # they are removed from the element once we're done with them.

    cleaner = self.cleaner
    fbuilder = self.font_builder

    tree = cleaner.tree_from_text(svgdoc)
    cleaner.clean_tree(tree)

    name, index, exists = fbuilder.add_components_and_ligature(ustr)

    tree.attrs['id'] = 'glyph%s' % index

    image_width = self._get_int_px(tree.attrs.pop('width'))
    image_height = self._get_int_px(tree.attrs.pop('height'))
    scale = float(self.font_height) / image_height;
    if exists:
      width = fbuilder.hmtx[name][0]
      # Special case for preexisting zero advance, we scale to height.
      if width > 0:
        hscale = float(width) / image_width;
        if hscale < scale:
          scale = hscale

    transform = 'translate(0, -%s) scale(%s)' % (self.font_upem, scale)
    tree.attrs['transform'] = transform

    svgdoc = cleaner.tree_to_text(tree)

    hmetrics = None
    if not exists:
      # horiz advance and lsb
      hmetrics = [int(round(image_width * scale)), 0]
    fbuilder.add_svg(svgdoc, hmetrics, name, index)
