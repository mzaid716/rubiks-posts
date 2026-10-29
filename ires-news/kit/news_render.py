"""IRES daily news carousel renderer.
Usage: python3 news_render.py spec.json out_dir
spec.json = {
 "photo": "path/to/cover_photo.png",           # text-free photo, any time of day
 "cover": {"label": "LAS VEGAS NEWS", "line1": "VEGAS HOME SALES", "line2": "DROP 22.7%",
           "sub": "Pending sales vs. a year ago", "source": "Source: Redfin, ..."},
 "details": [ {"label": "THE DETAILS", "white": "FEWER BUYERS", "red": "SIGNING CONTRACTS",
               "bullets": ["text with <b>bold</b> allowed", ...], "source": "Source: ..."} ],  # 1 or 2
 "cta": {"white": "NOT SELLING?", "red": "RENT IT OUT.", "sub": "..."}
}
"""
import json, sys, pathlib, html as H
from playwright.sync_api import sync_playwright

K = pathlib.Path(__file__).parent.resolve()
CSS = f"""
@font-face{{font-family:Anton;src:url('file://{K}/anton.woff2')}}
:root{{--red:#E31B23}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:Inter,'Poppins',sans-serif;background:#000}}
.s{{position:relative;width:1080px;height:1350px;overflow:hidden}}
.anton{{font-family:Anton;text-transform:uppercase;line-height:.92;letter-spacing:.5px}}
.fit{{white-space:nowrap;display:block}}
.red{{color:var(--red)}}
.label{{display:inline-block;background:var(--red);color:#fff;font:700 26px Inter;letter-spacing:5px;padding:10px 22px;text-transform:uppercase}}
.count{{position:absolute;top:44px;right:48px;color:#fff;font:700 24px Inter;background:rgba(0,0,0,.55);padding:8px 18px;border-radius:30px}}
.swipe{{background:var(--red);color:#fff;font:800 26px Inter;letter-spacing:2px;padding:16px 30px;border-radius:40px}}
.src{{color:#9a9a9a;font:500 20px Inter}}
.dark{{background:radial-gradient(120% 80% at 50% 0%,#1d1d20,#0b0b0c 60%)}}
li{{display:flex;gap:22px;margin-bottom:34px}}
"""
FIT = "<script>document.fonts.ready.then(()=>{document.querySelectorAll('.fit').forEach(e=>{let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth&&f>20){f-=2;e.style.fontSize=f+'px'}});document.body.dataset.ready=1})</script>"

def page(body): return f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}{FIT}</body></html>"
def logo(w): return f"<img src='file://{K}/logo_white.png' style='width:{w}px;filter:drop-shadow(0 2px 6px rgba(0,0,0,.5))'>"
e = H.escape

def cover(c, photo, n):
    return page(f"""<div class=s><div style="position:absolute;inset:0;background:url('file://{photo}') center/cover"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,0) 18%,rgba(0,0,0,0) 38%,rgba(0,0,0,.92) 58%,#000 66%)"></div>
<div style="position:absolute;top:44px;left:48px">{logo(250)}</div><div class=count>01/0{n}</div>
<div style="position:absolute;left:48px;right:48px;bottom:70px;text-align:center">
 <div class=label>{e(c['label'])}</div>
 <div class="anton fit" style="color:#fff;font-size:150px;margin-top:26px">{e(c['line1'])}</div>
 <div class="anton red fit" style="font-size:260px">{e(c['line2'])}</div>
 <div style="color:#fff;font:600 36px Inter;margin-top:18px">{e(c['sub'])}</div>
 <div style="display:flex;justify-content:space-between;align-items:center;margin-top:38px;text-align:left">
  <div class=src>{e(c['source'])}</div><div class=swipe>SWIPE →</div></div></div></div>""")

def details(d, i, n):
    lis = "".join(f"<li><span class=red>■</span><span>{b}</span></li>" for b in d['bullets'])
    return page(f"""<div class="s dark"><div style="position:absolute;top:48px;left:64px">{logo(190)}</div><div class=count>0{i}/0{n}</div>
<div style="position:absolute;top:220px;left:64px;right:64px">
 <div class=label>{e(d['label'])}</div>
 <div class="anton fit" style="color:#fff;font-size:120px;margin-top:26px">{e(d['white'])}</div>
 <div class="anton red fit" style="font-size:120px">{e(d['red'])}</div>
 <ul style="list-style:none;margin-top:56px;color:#fff;font:600 40px/1.35 Inter">{lis}</ul></div>
<div class=src style="position:absolute;left:64px;bottom:56px">{e(d['source'])}</div></div>""")

def cta(c, n):
    return page(f"""<div class="s dark"><div class=count>0{n}/0{n}</div>
<div style="position:absolute;top:240px;left:64px;right:64px;text-align:center">
 <div class=label>Your Next Move</div>
 <div class="anton fit" style="color:#fff;font-size:170px;margin-top:30px">{e(c['white'])}</div>
 <div class="anton red fit" style="font-size:170px">{e(c['red'])}</div>
 <div style="color:#fff;font:600 40px/1.4 Inter;margin:40px auto 0;max-width:860px">{e(c['sub'])}</div></div>
<div style="position:absolute;left:64px;right:64px;top:930px;background:#fff;border-radius:28px;padding:34px 30px;text-align:center">
 <div style="font:800 36px Inter;color:#111;white-space:nowrap"><span class=red>☎</span> CALL OR TEXT 702.858.4211 <span style="color:#ccc">|</span> IRESVEGAS.COM</div>
 <div style="font:600 26px Inter;color:#555;margin-top:12px">Brandy White Elk, Broker/Owner · Lic. B.9698</div></div>
<div style="position:absolute;left:64px;right:64px;bottom:60px;display:flex;justify-content:space-between;align-items:center">
 {logo(230)}<div class=swipe style="background:#D4A537;color:#111">SAVE + SHARE</div></div></div>""")

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])); out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    photo = pathlib.Path(spec['photo']).resolve()
    n = 2 + len(spec['details'])
    pages = [cover(spec['cover'], photo, n)] + [details(d, i + 2, n) for i, d in enumerate(spec['details'])] + [cta(spec['cta'], n)]
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, h in enumerate(pages, 1):
            hp = out / f"slide-{i}.html"; hp.write_text(h); pg.goto("file://" + str(hp))
            pg.wait_for_selector("body[data-ready]"); pg.wait_for_timeout(200)
            pg.screenshot(path=str(out / f"slide-{i}.png")); hp.unlink(); print("ok", i)
        b.close()
