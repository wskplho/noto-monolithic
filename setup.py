#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

#with open("README.rst", 'r') as readme_file:
#    readme = readme_file.read()
readme = """Noto font tools are a set of scripts useful for release
engineering of Noto and similar fonts"""

setup(name='nototools',
      version='0.0.1',
      description='Noto font tools',
      license="Apache",
      long_description=readme,
      author='Noto Authors',
      author_email='noto-font@googlegroups.com',
      url='https://code.google.com/p/noto/',
      # more examples here http://docs.python.org/distutils/examples.html#pure-python-distribution-by-package
      packages=['nototools'],
      install_requires=[
          'fontTools',
          # On Mac OS X these need to be installed with homebrew
          # 'cairo',
          # 'pango',
          # 'pygtk'
      ],
      dependency_links=['https://github.com/behdad/fontTools/tarball/master#egg=fontTools-2.5'],
      package_data={
          'nototools': [
              'nototools/*.sh',
          ]
      },
      # $ grep "def main(" nototools/* | cut -d: -f1
      scripts=['nototools/add_emoji_gsub.py',
               'nototools/autofix_for_release.py',
               'nototools/coverage.py',
               'nototools/create_image.py',
               'nototools/decompose_ttc.py',
               'nototools/drop_hints.py',
               'nototools/dump_otl.py',
               'nototools/fix_khmer_and_lao_coverage.py',
               'nototools/fix_noto_cjk_thin.py',
               'nototools/generate_sample_text.py',
               'nototools/generate_website_data.py',
               'nototools/map_pua_emoji.py',
               'nototools/merge_noto.py',
               'nototools/noto_lint.py',
               'nototools/scale.py',
               'nototools/subset.py',
               'nototools/subset_symbols.py',
               'nototools/test_vertical_extents.py'])
