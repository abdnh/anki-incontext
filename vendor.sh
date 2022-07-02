#!/usr/bin/env bash

curl https://raw.githubusercontent.com/abdnh/tdk/master/tdk.py -o src/providers/vendor/tdk.py
curl https://raw.githubusercontent.com/abdnh/skell-downloader/master/skell_downloader.py -o src/providers/vendor/skell_downloader.py
cp -r submodules/pycountry/src/pycountry src/providers/vendor/.
rm -rf src/providers/vendor/pycountry/locales src/providers/vendor/pycountry/tests