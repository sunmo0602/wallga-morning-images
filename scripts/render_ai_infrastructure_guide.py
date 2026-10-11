#!/usr/bin/env python3
"""Render six ChatGPT-authored SVG slides into final Instagram JPGs.

Cover: genuine Wikimedia Commons photo with explicit CC BY / CC0 / public
domain license; transparent editorial SVG text/gradient composited over it.
"""
import io,json,re
from pathlib import Path
import requests,cairosvg
from PIL import Image,ImageOps

ROOT=Path("incoming/ai-infrastructure-guide-20261011")
OUT=Path("published-assets/ai-infrastructure-guide-20261011")
W,H=1080,1350
def get_licensed_photo():
    api="https://commons.wikimedia.org/w/api.php"
    headers={"User-Agent":"WallgaMorningEditorial/1.0 (editorial licensed photo)"}
    for term in ("data center server racks interior", "server room rack data center"):
        r=requests.get(api,params={"action":"query","generator":"search",
          "gsrsearch":"filetype:bitmap "+term,"gsrnamespace":6,"gsrlimit":35,
          "prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":1600,
          "format":"json"},headers=headers,timeout=30)
        r.raise_for_status()
        for page in r.json().get("query",{}).get("pages",{}).values():
            try:
                info=page["imageinfo"][0];meta=info["extmetadata"]
                license_name=meta.get("LicenseShortName",{}).get("value","").lower()
                if not any(x in license_name for x in ("cc by","cc0","public domain")):
                    continue
                url=info.get("thumburl") or info["url"]
                raw=requests.get(url,headers=headers,timeout=35);raw.raise_for_status()
                with Image.open(io.BytesIO(raw.content)) as img:
                    img.load()
                    if img.width<1000 or img.height<700:continue
                    artist=re.sub(r"<[^>]*>"," ",meta.get("Artist",{}).get("value","Unknown")).strip()
                    return img.convert("RGB"),page["title"],license_name,artist
            except (requests.RequestException,KeyError,OSError,ValueError):continue
    raise RuntimeError("No adequately licensed cover photograph. Fail closed.")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    photo,title,lic,artist=get_licensed_photo()
    photo=ImageOps.fit(photo,(W,H),Image.Resampling.LANCZOS,centering=(.5,.48)).convert("RGBA")
    for n in range(1,7):
        src=ROOT/f"{n:02}.svg"
        if not src.exists():raise RuntimeError(f"Missing authored SVG: {src}")
        png=cairosvg.svg2png(bytestring=src.read_bytes(),output_width=W,output_height=H)
        overlay=Image.open(io.BytesIO(png)).convert("RGBA")
        if n==1:result=Image.alpha_composite(photo,overlay).convert("RGB")
        else:result=overlay.convert("RGB")
        result.save(OUT/f"{n:02}.jpg",format="JPEG",quality=90,optimize=True,subsampling=0)
        with Image.open(OUT/f"{n:02}.jpg") as verify:
            if verify.size!=(W,H):raise RuntimeError("Unexpected JPEG dimensions")
    caption="""AI 데이터센터가 늘면 엔비디아 말고 누가 돈을 벌까요?

AI 인프라 투자에는 GPU뿐 아니라 전력·냉각·네트워크·데이터센터 운영이 함께 필요합니다.

관련 미국 상장주 5개:
NVDA — AI 가속기·컴퓨팅
VRT — 전력·냉각 설비
ETN — 배전·전력 관리
ANET — 고속 데이터센터 네트워크
EQIX — 데이터센터 운영·코로케이션

같은 산업에 속해도 직접 수혜와 실제 실적은 다릅니다. 수주, 마진, 자본지출, 전력 병목을 확인하세요.

다음에 비교할 산업은 무엇인가요? 댓글로 남겨주세요.

@wallga.morning
#미국주식 #AI인프라 #NVDA #VRT #ETN #ANET #EQIX
※ 투자 권유가 아닌 정보 제공 목적입니다.
※ 이 콘텐츠는 산업 구조 설명이며 오늘의 신규 속보가 아닙니다.
표지 자료사진: Wikimedia Commons, """+title+""", """+artist+""", """+lic+""", 사진 크롭·그라데이션 편집.
https://commons.wikimedia.org/wiki/"""+title.replace(" ","_")
    (OUT/"caption.txt").write_text(caption,encoding="utf-8")
    (OUT/"photo_license.json").write_text(json.dumps({"title":title,"artist":artist,"license":lic,
      "url":"https://commons.wikimedia.org/wiki/"+title.replace(" ","_")},ensure_ascii=False,indent=2),encoding="utf-8")
    print("RENDERED",len(list(OUT.glob("*.jpg"))),"NEW 1080x1350 JPGs with licensed photo")
if __name__=="__main__":main()
