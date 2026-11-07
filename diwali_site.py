#!/usr/bin/env python3
"""Diwali website, powered by Python (standard library only).

Run:   python diwali_site.py
Open:  http://localhost:8000     (opens automatically)
Other port:  PORT=9000 python diwali_site.py
"""
import html, json, os, random, threading, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# ───────────────────────── CONTENT (edit freely) ─────────────────────────
NAV = [("/", "Home"), ("/about", "What is Diwali"), ("/diyas", "Diyas & Rangoli"),
       ("/crackers", "Crackers"), ("/sweets", "Sweets"), ("/wishes", "Wishes"), ("/safety", "Safety")]

HOME_CARDS = [
    ("/about", "🎉", "What is Diwali?", "The story, the five days and the traditions."),
    ("/diyas", "🪔", "Diyas & Rangoli", "Decorate your home and colour a rangoli."),
    ("/crackers", "🎆", "Crackers & Fun", "Launch fireworks in the sky, safely."),
    ("/sweets", "🍬", "Sweets Sharing", "Meet the mithai every home shares."),
    ("/wishes", "💌", "Make a Wish", "Create a Diwali greeting for a friend."),
    ("/safety", "🛡️", "Stay Safe", "Simple rules for a happy Diwali."),
]

PAGES = {
    "about": dict(emoji="🎉", title="What is Diwali?",
        intro="Diwali is the festival of lights. It celebrates light over darkness, good over evil and knowledge over ignorance.",
        blocks=[("Traditions", [
            ("🪔", "Lighting diyas", "Small oil lamps glow at doors, windows and temples."),
            ("🎨", "Making rangoli", "Colourful patterns at the entrance welcome guests and good luck."),
            ("🙏", "Lakshmi Puja", "Families pray to Lakshmi and Ganesha for health, wealth and happiness."),
            ("🎁", "Gifts and family", "People visit relatives, exchange gifts and share a meal."),
        ]), ("The five days", [
            ("🧹", "Day 1 · Dhanteras", "Homes are cleaned. Families buy something new for good fortune."),
            ("🪔", "Day 2 · Choti Diwali", "Marks the defeat of Narakasura. Diyas are lit at dusk."),
            ("✨", "Day 3 · Lakshmi Puja", "The main night, with lamps, prayers, sweets and fireworks."),
            ("⛰️", "Day 4 · Govardhan Puja", "Remembers Krishna lifting Govardhan hill. New Year in some regions."),
            ("👫", "Day 5 · Bhai Dooj", "Sisters pray for their brothers, who give gifts in return."),
        ]), ("Why we celebrate", [
            ("🏹", "Rama returns", "People lit lamps to welcome Rama, Sita and Lakshmana home to Ayodhya."),
            ("🔱", "Kali Puja", "In Bengal, Odisha and Assam the night honours goddess Kali."),
            ("☸️", "Jain Diwali", "Jains remember Lord Mahavira attaining moksha."),
            ("🕊️", "Bandi Chhor Divas", "Sikhs celebrate Guru Hargobind’s release from Gwalior fort."),
        ])]),
    "diyas": dict(emoji="🪔", title="Diyas & Rangoli",
        intro="Diyas make homes bright and rangoli adds colour. Try the rangoli below.",
        blocks=[("Decorate your home", [
            ("🪔", "Light diyas", "Place them near doors, windows and balconies. Soak clay diyas first so they burn longer."),
            ("🌼", "Marigold torans", "Strings of marigold and mango leaves on the door welcome guests."),
            ("🏮", "Lanterns and lights", "Hang akash kandils and fairy lights on balconies."),
            ("🪷", "Floating flowers", "Petals and a floating candle in a bowl make a quick centrepiece."),
        ])], extra="rangoli"),
    "crackers": dict(emoji="🎆", title="Crackers & Fun",
        intro="Fireworks make Diwali exciting, but enjoy them with care. Launch some in the sky below.",
        blocks=[("Enjoy responsibly", [
            ("🎆", "Watch from a distance", "Enjoy the colours from a safe spot with family."),
            ("🧯", "Safety first", "Keep water or sand nearby and never light crackers indoors."),
            ("👕", "Wear fitted cotton", "Avoid loose dupattas, scarves and synthetic fabric."),
            ("🌍", "Be kind to nature", "Choose fewer, quieter, eco-friendly crackers, and keep pets calm."),
        ])], extra="sky"),
    "sweets": dict(emoji="🍬", title="Sweets Sharing",
        intro="Diwali is sweeter when shared. Tap a sweet to learn about it.", blocks=[], extra="sweets"),
    "wishes": dict(emoji="💌", title="Make a Diwali Wish",
        intro="Write a name and a message. Python writes the greeting for you.", blocks=[], extra="wish"),
    "safety": dict(emoji="🛡️", title="Stay Safe",
        intro="A happy Diwali is a safe Diwali.",
        blocks=[("Simple rules", [
            ("🌳", "Open spaces only", "Light crackers outdoors, away from vehicles and dry grass."),
            ("💧", "Water nearby", "Keep a bucket of water or sand ready."),
            ("👶", "Adult supervision", "Never let small children handle crackers alone."),
            ("🚫", "Don’t relight", "Leave a dud cracker alone and pour water on it."),
            ("🕯️", "Careful with diyas", "Keep lamps away from curtains and never leave them unattended."),
            ("🩹", "Burns", "Cool minor burns under running water for 10 minutes. Get medical help for serious ones."),
            ("📜", "Follow local rules", "Many cities restrict crackers or allow only green ones."),
        ])]),
}

SWEETS = [("🟡", "Besan ladoo", "Roasted gram flour, ghee and sugar rolled into golden balls.", "#ffc43d"),
          ("💎", "Kaju katli", "Diamond-shaped cashew fudge, often topped with silver leaf.", "#ffe29a"),
          ("🟫", "Barfi", "A dense milk or nut sweet, cut into squares.", "#e0a96d"),
          ("🍯", "Gulab jamun", "Soft milk dumplings soaked in rose and cardamom syrup.", "#ff8fb0"),
          ("🌀", "Jalebi", "Crisp spirals fried and dipped in saffron syrup. Best warm.", "#ff9f43"),
          ("🤍", "Rasgulla", "Spongy cheese balls in light sugar syrup, loved in Bengal and Odisha.", "#f4f1ea")]

BLESSINGS = ["May every diya bring light, hope and success into your life.",
             "May Lakshmi and Ganesha bless your home with peace and prosperity.",
             "May this festival of lights fill your year with sweetness and laughter.",
             "May the glow of the lamps chase away every worry."]
GREETINGS = {"hindi": "शुभ दीपावली!", "english": "Happy Diwali!", "tamil": "தீபாவளி வாழ்த்துக்கள்!",
             "bengali": "শুভ দীপাবলি!", "gujarati": "દિવાળીની શુભેચ્છાઓ!", "punjabi": "ਦੀਵਾਲੀ ਦੀਆਂ ਵਧਾਈਆਂ!"}


def make_wish(name, message, lang):
    name = (name or "").strip()[:40]
    message = (message or "").strip()[:300]
    if not name:
        return {"ok": False, "text": "Please write a name first. 🪔"}
    hello = GREETINGS.get(lang, GREETINGS["hindi"])
    parts = [f"Dear {name},", f"{hello} 🪔✨", "Wishing you a Diwali full of happiness, good health and lovely memories."]
    if message:
        parts.append(message)
    parts += [random.choice(BLESSINGS), "Happy Diwali!\nFrom your friend"]
    return {"ok": True, "text": "\n\n".join(parts)}


# ───────────────────────── STYLE + SCRIPT ─────────────────────────
CSS = """
:root{--n:#12062a;--n2:#1d0a3d;--gd:#ffc43d;--sf:#ff8a1f;--mag:#d81b78;--cr:#fff1d0;--mu:#cdb9e6;--tl:#27d3c0;--ln:#52307f;color-scheme:dark}
*{box-sizing:border-box;margin:0}html{scroll-behavior:smooth}
body{background:var(--n);color:var(--cr);font:18px/1.65 'Mukta','Segoe UI',system-ui,sans-serif;overflow-x:hidden;padding-top:env(safe-area-inset-top,0px)}
h1,h2,h3{font-family:'Yatra One',Georgia,serif;font-weight:400;line-height:1.12}
a{color:inherit}:focus-visible{outline:3px solid var(--tl);outline-offset:3px}
nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:30;display:flex;gap:4px 14px;justify-content:center;flex-wrap:wrap;padding:10px;background:#12062aee;backdrop-filter:blur(10px);border-bottom:2px solid var(--gd)}
nav a{text-decoration:none;font-weight:600;font-size:16px;padding:3px 10px;border-radius:999px}nav a:hover{color:var(--gd)}nav a.on{background:var(--gd);color:#2a0f3d}
.hero,.head{position:relative;text-align:center;overflow:hidden;background:radial-gradient(ellipse at 50% 35%,#6b1a7a,#3a0f66 40%,var(--n) 80%)}
.hero{min-height:92svh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:50px 18px 150px}
.head{padding:56px 18px 44px}.head .big{font-size:64px}.head h1{font-size:clamp(34px,7vw,64px);color:var(--gd)}.head p{max-width:56ch;margin:10px auto 0;color:var(--mu)}
.hero>.c,.head>.c{position:relative;z-index:2}
.bg{position:absolute;inset:0;pointer-events:none}.star{position:absolute;border-radius:50%;background:#fff;animation:tw 3s infinite alternate}
@keyframes tw{from{opacity:.15}to{opacity:1}}
#mand{position:absolute;left:50%;top:45%;width:min(120vw,880px);translate:-50% -50%;opacity:.25;animation:spin 140s linear infinite}@keyframes spin{to{rotate:360deg}}
.lan{position:absolute;bottom:-90px;width:30px;height:42px;border-radius:12px 12px 8px 8px;background:linear-gradient(#ffd36b,#ff7a1a);box-shadow:0 0 26px 8px #ff8a1f88;animation:rise linear infinite}
@keyframes rise{to{transform:translate(var(--dx),-115vh)}}
.hi{font:400 clamp(24px,4.5vw,38px) 'Yatra One',serif;color:var(--sf)}
.hero h1{font-size:clamp(58px,14vw,150px);background:linear-gradient(#fff3c4,#ffc43d 45%,#ff7a1a);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 28px #ff8a1f77);padding:4px 0}
.sub{max-width:44ch;margin:6px auto 20px;font-size:clamp(18px,2.4vw,22px)}
#city{position:absolute;left:0;right:0;bottom:0;height:150px;z-index:1;width:100%}
.btn{font:inherit;font-weight:700;background:linear-gradient(90deg,var(--gd),var(--sf));color:#2a0f3d;border:0;border-radius:999px;padding:12px 28px;cursor:pointer;box-shadow:0 6px 22px #ff8a1f55;margin:4px;text-decoration:none;display:inline-block}
.btn.o{background:transparent;color:var(--cr);border:2px solid var(--gd);box-shadow:none}
main{max-width:1060px;margin:0 auto;padding:56px 20px 70px}
h2{font-size:clamp(28px,4.6vw,42px);color:var(--gd);text-align:center;margin:44px 0 22px}main h2:first-child{margin-top:0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px}
.card{position:relative;padding:26px;border-radius:24px;background:linear-gradient(160deg,#3a1568,#220b45);border:2px solid var(--ln);overflow:hidden;transition:transform .25s,border-color .25s;text-decoration:none;display:block}
a.card:hover,.card:hover{transform:translateY(-6px);border-color:var(--gd)}
.card::after{content:'';position:absolute;right:-40px;top:-40px;width:130px;height:130px;border-radius:50%;background:radial-gradient(#ff8a1f55,transparent 70%)}
.card .e{font-size:44px;display:block;position:relative;z-index:1}.card h3{font-size:23px;color:var(--gd);margin:6px 0 4px;position:relative;z-index:1}.card p{color:var(--mu);font-size:17px;position:relative;z-index:1}
.pn{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:50px}
.panel{background:#ffffff0f;border:2px solid var(--ln);border-radius:26px;padding:26px;text-align:center;margin-top:10px}
#rang{width:100%;max-width:420px;display:block;margin:0 auto;filter:drop-shadow(0 0 28px #d81b7855)}
#rang .p{fill:#2c0f55;stroke:var(--gd);stroke-width:.8;cursor:pointer;transition:fill .2s}#rang .p:hover{stroke:#fff}
.sws{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin:16px 0}.sws button{width:42px;height:42px;border-radius:50%;border:3px solid transparent;cursor:pointer}.sws button[aria-pressed=true]{border-color:#fff;box-shadow:0 0 14px #fff8}
#sky{width:100%;height:340px;display:block;border-radius:22px;background:linear-gradient(#05010f,#2a0b4d);border:2px solid var(--ln);cursor:crosshair}
.sweets{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px}
.sweet{font:inherit;border:0;border-radius:24px;padding:24px 10px;color:#2a0f3d;font-weight:700;cursor:pointer;transition:transform .2s}.sweet:hover{transform:translateY(-5px)}.sweet i{display:block;font-size:52px;font-style:normal}
#fact{min-height:3.4em;margin-top:22px;color:var(--gd);font-size:20px;text-align:center}
.form{max-width:560px;margin:0 auto;text-align:left}label{display:block;font-weight:700;color:var(--gd);margin:14px 0 6px}
input,textarea,select{font:inherit;width:100%;padding:12px 14px;border-radius:14px;border:2px solid var(--ln);background:var(--n2);color:var(--cr)}textarea{height:100px;resize:vertical}
#res{display:none;margin:24px auto 0;max-width:560px;padding:26px;border-radius:24px;border:3px solid var(--gd);white-space:pre-line;text-align:left;background:radial-gradient(circle at 50% 0,#ffc43d44,transparent 60%),linear-gradient(160deg,#4a1672,#a3195b);box-shadow:0 0 44px #ff8a1f55}
footer{text-align:center;padding:50px 20px 70px;color:var(--mu);background:linear-gradient(var(--n2),#000)}footer b{display:block;font:400 clamp(30px,6vw,48px) 'Yatra One',serif;color:var(--gd)}
.cf{position:fixed;top:-20px;width:10px;height:16px;z-index:99;animation:fall 3s linear forwards}@keyframes fall{to{transform:translateY(110vh) rotate(720deg);opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

JS = r"""
var $=function(i){return document.getElementById(i)},RM=matchMedia('(prefers-reduced-motion:reduce)').matches;
function stars(){var b=document.querySelector('.bg');if(!b)return;for(var i=0;i<60;i++){var s=document.createElement('i');s.className='star';var z=1+Math.random()*2.4;s.style.cssText='left:'+Math.random()*100+'%;top:'+Math.random()*80+'%;width:'+z+'px;height:'+z+'px;animation-delay:'+Math.random()*3+'s';b.appendChild(s)}
if(!RM&&$('city'))for(i=0;i<8;i++){var l=document.createElement('i');l.className='lan';l.style.cssText='left:'+(5+Math.random()*90)+'%;--dx:'+(Math.random()*120-60)+'px;animation-duration:'+(16+Math.random()*16)+'s;animation-delay:-'+Math.random()*20+'s;scale:'+(.6+Math.random()*.7);b.appendChild(l)}}
function mandala(){var m=$('mand');if(!m)return;var h='',i;for(i=0;i<24;i++)h+='<ellipse cy="-70" rx="10" ry="26" fill="none" stroke="#ffc43d" stroke-width=".8" transform="rotate('+i*15+')"/>';for(i=0;i<12;i++)h+='<path d="M0-20Q14-48 0-96Q-14-48 0-20" fill="none" stroke="#ff8a1f" stroke-width=".8" transform="rotate('+i*30+')"/>';m.innerHTML=h+'<circle r="98" fill="none" stroke="#ffc43d" stroke-width=".6"/>'}
function city(){var c=$('city');if(!c)return;var x=0,h='<rect width="1200" height="170" fill="#0a0318"/>';while(x<1180){var w=40+Math.random()*60,t=40+Math.random()*80,y=170-t;h+=Math.random()<.22?'<path d="M'+x+' 170V'+(y+30)+'Q'+(x+w/2)+' '+(y-30)+' '+(x+w)+' '+(y+30)+'V170z" fill="#120626"/>':'<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+t+'" fill="#120626"/>';for(var j=0;j<4;j++)if(Math.random()<.7)h+='<rect x="'+(x+8+Math.random()*(w-20))+'" y="'+(y+10+Math.random()*(t-30))+'" width="5" height="7" fill="#ffc43d" opacity=".85"/>';x+=w+4}c.innerHTML=h}
function confetti(){if(RM)return;var c=['#ffd166','#ff8a3d','#ff6b8a','#8a5cff','#7ef9ff'];for(var i=0;i<30;i++){var p=document.createElement('div');p.className='cf';p.style.cssText='left:'+Math.random()*100+'vw;background:'+c[i%5]+';animation-delay:'+Math.random()*.4+'s';document.body.appendChild(p);(function(q){setTimeout(function(){q.remove()},3600)})(p)}}
function fireworks(){var cv=$('sky');if(!cv)return;var cx=cv.getContext('2d'),P=[],run=0,cl=['#ffc43d','#ff8a1f','#ff4f9a','#27d3c0','#fff1d0','#b388ff'];
function fit(){cv.width=cv.clientWidth;cv.height=cv.clientHeight}fit();addEventListener('resize',fit);
function bu(x,y){var k=cl[Math.random()*6|0];for(var i=0;i<60;i++){var a=6.283*i/60,s=1.5+Math.random()*3.6;P.push({x:x,y:y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,l:1,c:k})}if(!run){run=1;lp()}}
function lp(){cx.fillStyle='rgba(5,1,15,.22)';cx.fillRect(0,0,cv.width,cv.height);P=P.filter(function(p){return p.l>0});P.forEach(function(p){p.x+=p.vx;p.y+=p.vy;p.vy+=.045;p.vx*=.99;p.l-=.012;cx.globalAlpha=Math.max(p.l,0);cx.fillStyle=p.c;cx.beginPath();cx.arc(p.x,p.y,2.2,0,6.3);cx.fill()});cx.globalAlpha=1;if(P.length)requestAnimationFrame(lp);else{run=0;cx.clearRect(0,0,cv.width,cv.height)}}
function show(n){if(RM)return;for(var i=0;i<n;i++)setTimeout(function(){bu(cv.width*(.1+Math.random()*.8),cv.height*(.1+Math.random()*.5))},i*260)}
cv.onclick=function(e){var r=cv.getBoundingClientRect();bu((e.clientX-r.left)*cv.width/r.width,(e.clientY-r.top)*cv.height/r.height)};$('launch').onclick=function(){show(9)};setTimeout(function(){show(4)},400)}
function rangoli(){var r=$('rang');if(!r)return;var pc=['#ffc43d','#ff8a1f','#ff4f9a','#d81b78','#27d3c0','#b388ff','#fff1d0','#3d7bff'],cur=pc[0],h='',i;
for(i=0;i<8;i++)h+='<ellipse class="p" cy="-30" rx="9" ry="19" transform="rotate('+i*45+')"/>';for(i=0;i<16;i++)h+='<ellipse class="p" cy="-60" rx="8" ry="17" transform="rotate('+i*22.5+')"/>';for(i=0;i<16;i++)h+='<circle class="p" cy="-87" r="6" transform="rotate('+(i*22.5+11.25)+')"/>';r.innerHTML=h+'<circle class="p" r="12"/>';
r.onclick=function(e){if(e.target.classList.contains('p'))e.target.style.fill=cur};var s=$('sws');pc.forEach(function(k,i){var b=document.createElement('button');b.style.background=k;b.setAttribute('aria-label','Colour '+(i+1));b.setAttribute('aria-pressed',i==0);b.onclick=function(){cur=k;[].forEach.call(s.children,function(x){x.setAttribute('aria-pressed',x===b)})};s.appendChild(b)});
function all(f){[].forEach.call(r.querySelectorAll('.p'),f)}$('rnd').onclick=function(){all(function(p){p.style.fill=pc[Math.random()*8|0]})};$('clr').onclick=function(){all(function(p){p.style.fill=''})}}
function sweets(){document.querySelectorAll('.sweet').forEach(function(b){b.onclick=function(){$('fact').textContent=b.dataset.name+': '+b.dataset.fact;confetti()}})}
function wish(){var f=$('wf');if(!f)return;f.onsubmit=function(e){e.preventDefault();var q=new URLSearchParams({name:$('nm').value,msg:$('ms').value,lang:$('lg').value});
fetch('/api/wish?'+q).then(function(r){return r.json()}).then(function(d){var r=$('res');r.style.display='block';r.textContent=d.text;$('cp').style.display=d.ok?'inline-block':'none';if(d.ok)confetti()}).catch(function(){$('res').style.display='block';$('res').textContent='Could not reach the Python server.'})};
$('cp').onclick=function(){var b=this;try{navigator.clipboard.writeText($('res').textContent).then(function(){b.textContent='Copied!';setTimeout(function(){b.textContent='Copy wish'},1500)})}catch(e){}}}
stars();mandala();city();fireworks();rangoli();sweets();wish();
"""

# ───────────────────────── PAGE BUILDERS ─────────────────────────
E = html.escape
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Yatra+One&family=Mukta:wght@400;600;700&display=swap" rel="stylesheet">'


def cards(items):
    return '<div class="grid">' + "".join(
        f'<div class="card"><span class="e">{e}</span><h3>{E(t)}</h3><p>{E(d)}</p></div>' for e, t, d in items) + "</div>"


def extra_block(kind):
    if kind == "rangoli":
        return ('<h2>Colour your own rangoli</h2><div class="panel"><p>Pick a colour, then tap the petals.</p>'
                '<div class="sws" id="sws"></div><svg id="rang" viewBox="-100 -100 200 200" role="img" aria-label="Rangoli to colour"></svg>'
                '<p style="margin-top:16px"><button class="btn" id="rnd">Surprise me</button><button class="btn o" id="clr">Clear</button></p></div>')
    if kind == "sky":
        return ('<h2>Light up the sky</h2><canvas id="sky" aria-label="Fireworks sky. Tap to launch"></canvas>'
                '<p style="text-align:center;margin-top:12px;color:var(--mu)">Tap the sky or press the button.</p>'
                '<p style="text-align:center"><button class="btn" id="launch">Launch fireworks</button></p>')
    if kind == "sweets":
        tiles = "".join(f'<button class="sweet" style="background:{c}" data-name="{E(n)}" data-fact="{E(f)}"><i>{e}</i>{E(n)}</button>'
                        for e, n, f, c in SWEETS)
        return f'<div class="sweets">{tiles}</div><p id="fact" aria-live="polite">Tap a sweet.</p>'
    if kind == "wish":
        langs = "".join(f'<option value="{k}">{k.title()}</option>' for k in GREETINGS)
        return ('<form class="form" id="wf"><label for="nm">Friend’s name</label><input id="nm" maxlength="40" placeholder="e.g. Aarav" required>'
                '<label for="ms">Your message</label><textarea id="ms" maxlength="300" placeholder="Write something special…"></textarea>'
                f'<label for="lg">Greeting language</label><select id="lg">{langs}</select>'
                '<p style="text-align:center;margin-top:18px"><button class="btn" type="submit">Create wish 🪔</button></p></form>'
                '<div id="res"></div><p style="text-align:center"><button class="btn o" id="cp" style="display:none">Copy wish</button></p>')
    return ""


def render(path):
    key = path.strip("/") or "home"
    nav = "".join(f'<a href="{h}"{" class=on" if h == path else ""}>{E(n)}</a>' for h, n in NAV)
    if key == "home":
        top = ('<header class="hero"><div class="bg"></div><svg id="mand" viewBox="-100 -100 200 200" aria-hidden="true"></svg><div class="c">'
               '<div class="hi">शुभ दीपावली</div><h1>Happy Diwali</h1><p class="sub">The festival of lights, when every home glows and light wins over darkness.</p>'
               '<a class="btn" href="/wishes">Make a wish</a><a class="btn o" href="/crackers">Fireworks</a></div>'
               '<svg id="city" viewBox="0 0 1200 170" preserveAspectRatio="none" aria-hidden="true"></svg></header>')
        body = ('<main><h2>Explore Diwali</h2><div class="grid">' + "".join(
            f'<a class="card" href="{h}"><span class="e">{e}</span><h3>{E(t)}</h3><p>{E(d)}</p></a>' for h, e, t, d in HOME_CARDS) + "</div></main>")
        title = "शुभ दीपावली – Happy Diwali"
    else:
        p = PAGES[key]
        top = (f'<header class="head"><div class="bg"></div><div class="c"><div class="big">{p["emoji"]}</div><h1>{E(p["title"])}</h1><p>{E(p["intro"])}</p></div></header>')
        body = "<main>" + "".join(f"<h2>{E(h)}</h2>{cards(i)}" for h, i in p["blocks"]) + extra_block(p.get("extra")) + "</main>"
        idx = [h for h, _ in NAV].index(path)
        prev_l, next_l = NAV[idx - 1], NAV[(idx + 1) % len(NAV)]
        body = body[:-7] + (f'<div class="pn"><a class="btn o" href="{prev_l[0]}">← {E(prev_l[1])}</a>'
                            f'<a class="btn" href="{next_l[0]}">{E(next_l[1])} →</a></div></main>')
        title = f'{p["title"]} · Diwali'
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<title>{E(title)}</title>{FONTS}<style>{CSS}</style></head><body><nav aria-label="Main">{nav}</nav>{top}{body}'
            f'<footer><b>शुभ दीपावली</b><p>Happy Diwali. May this year’s light reach every corner of your life.</p></footer><script>{JS}</script></body></html>')


# ───────────────────────── SERVER ─────────────────────────
ROUTES = {h: None for h, _ in NAV}


class Handler(BaseHTTPRequestHandler):
    def send(self, code, ctype, data):
        b = data.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/wish":
            q = parse_qs(u.query)
            g = lambda k: q.get(k, [""])[0]
            return self.send(200, "application/json", json.dumps(make_wish(g("name"), g("msg"), g("lang")), ensure_ascii=False))
        path = u.path if u.path == "/" else u.path.rstrip("/")
        if path in ROUTES:
            return self.send(200, "text/html", render(path))
        self.send(404, "text/html", "<h1 style='font-family:sans-serif'>404 – page not found 🪔 <a href='/'>Home</a></h1>")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    url = f"http://localhost:{port}"
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"🪔 Diwali site running at {url}   (Ctrl+C to stop)")
    threading.Timer(1, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nHappy Diwali! Server stopped.")