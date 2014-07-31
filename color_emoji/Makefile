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

EMOJI = NotoColorEmoji
EMOJI_PNG128 = ./png/128/emoji_u
EMOJI_PNG64 = ./png/64/emoji_u

EMOJI_BUILDER = ../third_party/color_emoji/emoji_builder.py
ADD_GLYPHS= ../third_party/color_emoji/add_glyphs.py
PUA_ADDER = ../nototools/map_pua_emoji.py

$(EMOJI_PNG64)%.png: $(EMOJI_PNG128)%.png
	convert -geometry 50% "$<" "$@"
	optipng -o7 "$@"

%.ttx: %.ttx.tmpl $(ADD_GLYPHS) $(UNI)
	python $(ADD_GLYPHS) "$<" "$@" "$(EMOJI_PNG128)"

%.ttf: %.ttx
	@rm -f "$@"
	ttx "$<"

$(EMOJI).ttf: $(EMOJI).tmpl.ttf $(EMOJI_BUILDER) $(PUA_ADDER) $(EMOJI_PNG128)*.png $(EMOJI_PNG64)*.png
	python $(EMOJI_BUILDER) -V $< "$@" $(EMOJI_PNG128) $(EMOJI_PNG64)
	python $(PUA_ADDER) "$@" "$@-with-pua"
	mv "$@-with-pua" "$@"

CFLAGS = -std=c99 -Wall -Wextra `pkg-config --cflags --libs cairo`
LDFLAGS = `pkg-config --libs cairo`

waveflag: waveflag.c
	$(CC) $< -o $@ $(CFLAGS) $(LDFLAGS)

clean:
	rm -f waveflag
	rm -f $(EMOJI).ttf $(EMOJI).tmpl.ttf $(EMOJI).tmpl.ttx
