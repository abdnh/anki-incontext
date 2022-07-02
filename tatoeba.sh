#!/usr/bin/env bash

LANG_CODE="$1"
curl https://downloads.tatoeba.org/exports/per_language/"$LANG_CODE"/"$LANG_CODE"_sentences.tsv.bz2 -o src/user_files/tatoeba/"$LANG_CODE"_sentences.tsv.bz2
bzip2 -df src/user_files/tatoeba/"$LANG_CODE"_sentences.tsv.bz2
