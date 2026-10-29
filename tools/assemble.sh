#!/bin/bash
# Build production site into repo/site, keep big PDFs out (they go to the GitHub release).
set -e
REPO=/home/claude/repo
export MAP_EMBED="https://maps.google.com/maps?q=Korazin%20St%2022%2C%20Jerusalem%2C%20Israel&z=16&output=embed"
MODE=prod python3 /home/claude/tools/build.py /home/claude/build_prod | grep written
rm -rf $REPO/site $REPO/functions $REPO/tools
mkdir -p $REPO/functions $REPO/tools /home/claude/bigpdfs
cp -r /home/claude/build_prod $REPO/site
rm -rf $REPO/site/functions
cp /home/claude/tools/_middleware.js $REPO/functions/_middleware.js
find $REPO/site/_files -type f -size +24M -exec mv {} /home/claude/bigpdfs/ \;
mkdir -p $REPO/site/_chunks
python3 - <<'PY'
import os
src='/home/claude/bigpdfs'; dst='/home/claude/repo/site/_chunks'; C=24_000_000
for f in sorted(os.listdir(src)):
    d=open(os.path.join(src,f),'rb').read()
    for n,i in enumerate(range(0,len(d),C)): open(os.path.join(dst,f"{f}.{n:03d}"),'wb').write(d[i:i+C])
PY
# inline download names for the PDFs Cloudflare serves directly (same as Wix)
: > $REPO/site/_headers
while IFS='|' read f d; do
  [ -f "$REPO/site/_files/ugd/$f" ] && [ -n "$d" ] && printf '/_files/ugd/%s\n  Content-Disposition: %s\n' "$f" "$d" >> $REPO/site/_headers
done < /home/claude/tools/pdf_names.txt
cp /home/claude/tools/{build.py,site.js,site.css,donate.html,_middleware.js,assemble.sh,pdf_names.txt,chunks.json} $REPO/tools/
du -sh $REPO/site; find $REPO/site -type f | wc -l; ls /home/claude/bigpdfs | wc -l; cat $REPO/site/_headers | head -4
