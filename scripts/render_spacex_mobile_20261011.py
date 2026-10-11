from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps
import cairosvg, requests, json
ALBUM='spacex-mobile-spectrum-20261011'
SOURCE=Path('incoming')/ALBUM
DEST=Path('published-assets')/ALBUM
URL='https://upload.wikimedia.org/wikipedia/commons/a/a7/CellTower.jpg'
RIGHTS={'license':'CC0 1.0','author':'Nikolai Twin','page':'https://commons.wikimedia.org/wiki/File:CellTower.jpg','note':'symbolic generic photo, not SpaceX'}
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    headers={'User-Agent':'WallgaMorningEditorial/1.0 (photo source cited in caption)'}
    response=requests.get(URL,headers=headers,timeout=50)
    response.raise_for_status()
    with Image.open(BytesIO(response.content)) as i:
        photo=ImageOps.fit(ImageOps.exif_transpose(i).convert('RGB'),(1080,1350)).convert('RGBA')
    for n in range(1,7):
        svg=(SOURCE/f'{n:02}.svg').read_bytes()
        if b'wallga.morning' not in svg: raise RuntimeError('missing brand')
        overlay=Image.open(BytesIO(cairosvg.svg2png(bytestring=svg,output_width=1080,output_height=1350))).convert('RGBA')
        out=Image.alpha_composite(photo,overlay) if n==1 else overlay
        dst=DEST/f'{n:02}.jpg'
        out.convert('RGB').save(dst,format='JPEG',quality=92,optimize=True)
        with Image.open(dst) as ck:
            assert ck.size==(1080,1350) and ck.format=='JPEG'
    for name in ['caption.txt','editorial_manifest.json']:
        (DEST/name).write_bytes((SOURCE/name).read_bytes())
    (DEST/'photo_license.json').write_text(json.dumps(RIGHTS),encoding='utf-8')
    print('RENDER SUCCESS: six licensed-cover 1080x1350 original JPEGs')
if __name__=='__main__': main()
