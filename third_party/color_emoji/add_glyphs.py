#!/usr/bin/python

"""Tool to update GSUB, HTMX, and CMAP tables with image glyphs.

The original version of this file assumes image glyphs are .png files
in a directory/prefix.  This version takes an optional type
parameter, if 'png' it assumes files with extension .png, and if 'svg'
it assumes files with extension .svg.  Horizontal advance for svg is based on
the extent, which is assumed to be in a viewBox attribute of the svg
element."""

import argparse, glob, os, re, sys
from fontTools import ttx
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables import _g_l_y_f as glyf
from png import PNG

sys.path.append('../../nototools')
from nototools import add_emoji_gsub

import svg_builder

usage = """This will search for files that have strike-prefix followed by one or more
    hex numbers (separated by underscore if more than one), and end in ".png" or ".svg".
    For example, if strike-prefix is "icons/u", then files with names like
    "icons/u1F4A9.png" or "icons/u1F1EF_1F1F5.png" will be loaded.  The script
    then adds cmap, htmx, and potentially GSUB entries for the Unicode
    characters found.  The advance width will be chosen based on image aspect
    ratio.  If Unicode values outside the BMP are desired, the existing cmap
    table should be of the appropriate (format 12) type.  Only the first cmap
    table and the first GSUB lookup (if existing) are modified."""

parser = argparse.ArgumentParser(
    description="Update GSUB, hmtx, and cmap tables from image glyphs.", epilog=usage)
parser.add_argument('in_file', help="Input ttx file name. Will modify existing tables.")
parser.add_argument('out_file', help="Output ttx file name.")
parser.add_argument('image_prefix', help="Location and prefix of image files.")
parser.add_argument('--flavor', dest='image_flavor', help="Image file flavor (default 'png').",
                    default='png', choices=['png', 'svg'])
parser.add_argument('--quiet', '-q', help="quiet operation.", action='store_true')
args = parser.parse_args()

# stub, it doesn't do much but let us work with .png the way we work with
# .svg
class PngBuilder(object):
  def add_from_filename(self, filename, glyph_id, name=None):
    extent = PNG(filename).get_size()
    return PngItem(extent)

  def add_to_font(self, ttfont):
    pass

class PngItem(object):
  def __init__(self, extent):
    self.extent = extent

  def get_extent(self):
    return self.extent

def glyph_name(string):
	return "_".join (["u%04X" % ord (char) for char in string])

def add_ligature (font, string):
	if 'GSUB' not in font:
		ligature_subst = otTables.LigatureSubst()
		ligature_subst.ligatures = {}

		lookup = otTables.Lookup()
		lookup.LookupType = 4
		lookup.LookupFlag = 0
		lookup.SubTableCount = 1
		lookup.SubTable = [ligature_subst]

		font['GSUB'] = add_emoji_gsub.create_simple_gsub([lookup])
	else:
		lookup = font['GSUB'].table.LookupList.Lookup[0]
		assert lookup.LookupType == 4
		assert lookup.LookupFlag == 0

	ligatures = lookup.SubTable[0].ligatures

	lig = otTables.Ligature()
	lig.CompCount = len(string)
	lig.Component = [glyph_name(ch) for ch in string[1:]]
	lig.LigGlyph = glyph_name(string)

	first = glyph_name(string[0])
	try:
		ligatures[first].append(lig)
	except KeyError:
		ligatures[first] = [lig]

in_file = args.in_file
out_file = args.out_file
img_prefix = args.image_prefix
img_flavor = args.image_flavor

font = ttx.TTFont()
font.importXML (in_file)

img_files = {}
glb = "%s*.%s" % (img_prefix, img_flavor)
ext_len = len(img_flavor) + 1;
print "Looking for images matching '%s'." % glb
for img_file in glob.glob (glb):
	codes = img_file[len (img_prefix):-ext_len]
	if "_" in codes:
		pieces = codes.split ("_")
		u = "".join ([unichr (int (code, 16)) for code in pieces])
	else:
		u = unichr (int (codes, 16))
	img_files[u] = img_file
if not img_files:
	raise Exception ("No image files found in '%s'." % glb)

ascent = font['hhea'].ascent
descent = -font['hhea'].descent

g = font['GlyphOrder'].glyphOrder
c = font['cmap'].tables[0].cmap
h = font['hmtx'].metrics

builder = svg_builder.SvgBuilder() if img_flavor == 'svg' else PngBuilder()

# Sort the characters by length, then codepoint, to keep the order stable
# and avoid adding empty glyphs for multi-character glyphs if any piece is
# also included.
img_pairs = img_files.items ()
img_pairs.sort (key=lambda pair: (len (pair[0]), pair[0]))

for (u, filename) in img_pairs:
        if not args.quiet:
                print "Adding glyph for U+%s" % ",".join (["%04X" % ord (char) for char in u])
	for char in u:
		if ord(char) not in c:
			name = glyph_name (char)
			c[ord (char)] = name
			if len (u) > 1:
				h[name] = [0, 0]
                                g.append(name)

	name = glyph_name(u)
        img_item = builder.add_from_filename(filename, len(g), name)
	g.append(name)
	img_width, img_height = img_item.get_extent()
	advance = int (round ((float (ascent+descent) * img_width / img_height)))
	h[name] = [advance, 0]
	if len (u) > 1:
		add_ligature (font, u)

builder.add_to_font(font)

# SVG requires that there be a glyf table or some other fallback for engines
# that don't understand SVG. We'll ensure that such a table exists and that there
# is a glyf entry for each glyph listed in the glyph order table
if img_flavor == 'svg':
  if not 'glyf' in font:
    print "font has no glyf table"
    glyf_table = glyf.table__g_l_y_f()
    glyf_table.glyphs = {}
    glyf_table.glyphOrder = font.getGlyphOrder()
    font['glyf'] = glyf_table
  glyphs = font['glyf'].glyphs

  for name in g:
    null_glyf = glyf.Glyph()
    if not name in glyphs:
      glyphs[name] = null_glyf

font.saveXML (out_file)
