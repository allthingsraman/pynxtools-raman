#!/bin/sh
# Rod
echo " !!! Converting Rod Data !!! "
find tests/data/rod -type f ! -name '*.nxs' ! -name '*output.txt' | xargs dataconverter --nxdl NXraman --reader raman --output rod.nxs #--skip-verify
find tests/data/rod f -name '*.nxs' | xargs mv rod.nxs

# # Witec
# echo " !!! Converting Witec Data !!! "
find tests/data/witec -type f ! -name '*.nxs' ! -name '*output.txt' | xargs dataconverter --nxdl NXraman --reader raman --output witec.nxs #--skip-verify
find tests/data/witec f -name '*.nxs' | xargs mv witec.nxs
