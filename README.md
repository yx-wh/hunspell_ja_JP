# hunspell_ja_JP
Author: Gary

Description: Hunspell morphology dictionary for Japanese.

In addition to de-inflection, this Hunspell morphological dictionary now also supports restoring many mazegaki (mixed kanji-kana) entries to their kanji forms. For example, querying 「着ぐるみ」 can display the entry for 「着包み」, and querying 「思いつき」 can display the entry for 「思い付く」 when Two-Pass Lookup is enabled.

Updated: 2026/09/14


## Old forms and traditional characters (ICONV)

The `ICONV` table in `ja_JP.aff` rewrites the query **before** lookup and
word-form analysis. Half-width katakana have always gone through it; old forms
(and the traditional Chinese characters that coincide with them) do too:

```text
ICONV 圖 図
```

So `圖らず` is folded to `図らず` first, and the existing `5A`/`f2` rules
deinflect it to `図る` — for every word containing the character, without a
`st:` row per word.

This comes with one maintenance rule: **the source spellings in `.dic` must
match the `ICONV` table.** Once `圖` is rewritten to `図`, a row such as
`圖/Zz st:図` can never be reached, and the loss is silent (`spell()` still
returns true). Whenever the table changes, run:

```bash
python3 apply_iconv_to_dic.py ja_JP.aff ja_JP.dic --apply
python3 ../mazegaki-dic/add_homonym_flag.py ja_JP.dic --aff ja_JP.aff --apply
```

It rewrites the heads and folds `st:` rows that have become self-referential;
it is idempotent. Apply it with `--plain` to `ja_JP.part.txt` in mazegaki-dic
as well, or the next rebuild will write the old forms back.

Do not add reverse rows (`図 -> 圖`): they would double the variants of every
query containing the character, and only proper nouns and old-spelling phrases
would benefit.

## How to use
### GoldenDict-ng
https://github.com/xiaoyifang/goldendict-ng/releases
1. Download both ja_JP.aff and ja_JP.dic and save to your designated folder for GoldenDict morphology.
2. Quit GoldenDict and reopen it to let it automatically detect the added Japanese morphology.
3. Go to the Dictionary setting in the app, and enable the added morphology. Also add it to your Dict groups if you want.
4. It should be working now :)

### GoldenDict Mobile for Android
http://goldendict.mobi/
1. Download both ja_JP.aff and ja_JP.dic and save them to /storage/emulated/0/GoldenDict, or a folder under it.
2. Quit GoldenDict Mobile and reopen it to let it automatically detect the added Japanese morphology.
3. It should be working now :)

### Cíyuè(词悦)
https://github.com/mumu-lhl/Ciyue/releases/
1. Download both ja_JP.aff and ja_JP.dic and save to your designated folder for Cíyuè(词悦) morphology.
2. Click Settings - Hunspell - Enable word-form lookup, then click Import Hunspell dictionaries, and select your designated folder.
3. Enable it and its Two-pass lookup, then close the app and start it again.
4. It should be working now :)

##
Feel free to drop a comment for questions and communications.

Please indicate the origin when using.
转载请注明出处。

https://github.com/MrCorn0-0/hunspell_ja_JP/
