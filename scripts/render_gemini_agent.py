#!/usr/bin/env python3
"""Render six ChatGPT-authored SVG slides into final Instagram JPGs.

Cover: genuine Wikimedia Commons photo with explicit CC BY / CC0 / public
domain license; transparent editorial SVG text/gradient composited over it.
"""
import io,json,re
from pathlib import Path
import requests,cairosvg
from PIL import Image,ImageOps

ROOT=Path("incoming/gemini-agent-20261011")
OUT=Path("published-assets/gemini-agent-20261011")
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
    caption="""구글이 10월 8일 기업 업무용 범용 AI 에이전트 'Gemini agent'를 발표했습니다.

이제 AI는 질문에 답하는 수준을 넘어, 업무 계획부터 문서 작성과 코딩까지 실제 작업을 수행하는 방향으로 발전하고 있습니다.

함께 볼 미국주식:
GOOGL — 발표 주체, Google Cloud와 Workspace
MSFT — Copilot·기업용 소프트웨어 경쟁
AMZN — AWS 기업용 AI·클라우드
CRM — Salesforce Agentforce
NOW — ServiceNow 기업 업무 자동화

위 기업들이 모두 이번 발표의 직접 수혜를 받는다는 뜻은 아닙니다. 기업 도입률, 유료 고객, 보안, AI 운영비용을 함께 확인해야 합니다.

다음에 비교할 AI 관련주는? 댓글로 알려주세요.

@wallga.morning
#미국주식 #구글 #GOOGL #MSFT #AMZN #CRM #NOW #AI에이전트
※ 투자 권유가 아닌 정보 제공 목적입니다.
원문: https://cloud.google.com/blog/products/ai-machine-learning/welcome-to-gemini-at-work-2026
발표: 2026.10.08
표지 자료사진: Wikimedia Commons, """+title+""", """+artist+""", """+lic+""". 사진 크롭·그라데이션 편집. 구글 공식 행사 사진 아님.
https://commons.wikimedia.org/wiki/"""+title.replace(" ","_")
    (OUT/"caption.txt").write_text(caption,encoding="utf-8")
    (OUT/"photo_license.json").write_text(json.dumps({"title":title,"artist":artist,"license":lic,
      "url":"https://commons.wikimedia.org/wiki/"+title.replace(" ","_")},ensure_ascii=False,indent=2),encoding="utf-8")
    print("RENDERED",len(list(OUT.glob("*.jpg"))),"1080x1350 JPGs with licensed photo")
if __name__=="__main__":main()
