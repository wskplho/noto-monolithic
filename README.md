# noto-monolithic

This repository mirrors the original Noto repository that used to be hosted on Google Code,
at https://code.google.com/p/noto.  The Noto project was moved to github on Friday, June 5,
2015.  During this move, it was necessary to compress third_party/noto_cjk/NotoSansCJK.ttc,
because github does not allow files larger than 100MB.  As such, the git history was rewritten
and does not match existing clones.

Moreover, we found that combining the CJK fonts and all the rest of Noto in one repository
makes it quite cumbersome to clone the repo.  At the same time of the move, we decided to
break the repository into the following four pieces:

  * [noto-fonts](https://github.com/googlei18n/noto-fonts): Noto fonts, except for CJK and emoji,
  * [noto-cjk](https://github.com/googlei18n/noto-cjk): Noto CJK fonts,
  * [noto-emoji](https://github.com/googlei18n/noto-emoji): Color and B&W emoji fonts,
  * [nototools](https://github.com/googlei18n/nototools): Tools and scripts for supporting Noto fonts.

This repository is frozen and will not change.  Please use the repositories listed above for
new development.
