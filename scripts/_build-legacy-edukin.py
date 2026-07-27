#!/usr/bin/env python3
# Edukin migration builder for ajascollege.ac.in  -> ajascollege-new
import re,os,glob,json,html,shutil,sys
from html.parser import HTMLParser

ROOT='/Users/aathif/Projects/ajascollege'
SRC=os.path.join(ROOT,'ajascollege.ac.in')
OUT=os.path.join(ROOT,'ajascollege-new')
EDU=os.path.join(ROOT,'edukin-package/edukin')
SITE='Al Jamia Arts & Science College'

# ---- WP post-id -> slug map, derived from the mirror's rel=shortlink tags ----
def build_id2slug():
    m={}
    for fp in glob.glob(os.path.join(SRC,'**','index.html'),recursive=True):
        rel=os.path.relpath(fp,SRC)
        slug='.' if rel=='index.html' else os.path.dirname(rel)
        try: s=open(fp,encoding='utf-8',errors='ignore').read(60000)
        except OSError: continue
        mm=re.search(r"rel=['\"]shortlink['\"] href=['\"][^'\"]*index\.html@p=(\d+)\.html['\"]",s)
        if mm: m.setdefault(mm.group(1),slug)
    return m
id2slug=build_id2slug()
MIGRATE_CSS='''
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;600;700;800&display=swap');
/* ============================================================
   Typeface: Rubik replaces the theme's Poppins everywhere except
   the icon fonts, which must keep their own family to render.
   ============================================================ */
body,button,input,select,textarea,
h1,h2,h3,h4,h5,h6,p,a,li,span,div,td,th,label,blockquote,figcaption,
.flat-title,.widget-title,.title,.breadcrumbs-wrap .title,.education-text,
.numb-count,.name-count,.entry-title,.item-title,.sub-title,.caption{
    font-family:'Rubik',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;}
i,em.fa,.fa,[class^="fa-"],[class*=" fa-"]{font-family:FontAwesome !important;}
[class^="icon-"],[class*=" icon-"],.icon-event,.icon-quote{font-family:'icomoon' !important;}
[class^="ti-"],[class*=" ti-"]{font-family:'themify' !important;}
/* Rubik runs a touch wider than Poppins — tighten the display sizes */
h1,h2,h3,h4,h5,h6,.flat-title,.education-text,.breadcrumbs-wrap .title{letter-spacing:-.4px;}
.flat-title{font-weight:600;}

/* ============================================================
   AJAS layer on top of Edukin.
   Rule: do NOT restyle Edukin chrome. Only (a) adapt the nav to a
   10-item / 4-level college menu, (b) type-set migrated body copy,
   (c) add the few blocks Edukin has no component for.
   Edukin palette: #ff5f60 coral · #3f4c99 indigo · #7ecc88 green
                   #183251 navy · #ffbe34 amber · #25cf71 · #a476b4
   Font: Poppins (inherited from style.css) — no override.
   ============================================================ */

/* ---------- inner-page banner: Edukin's .bg-header, AJAS photo ---------- */
.bg-header{
    background-image:linear-gradient(rgba(24,50,81,.86),rgba(24,50,81,.86)),url('uploads/2024/01/P1222323-building-2048x1154-1.webp');
    background-size:cover;background-position:center 32%;background-repeat:no-repeat;
    height:auto;padding-bottom:70px;
}
.breadcrumbs-blog{padding-top:64px;}
.breadcrumbs-wrap .title{font-size:34px;line-height:44px;font-weight:600;}
.breadcrumbs-inner li a{font-size:14px;opacity:.85;}
.breadcrumbs-inner li:last-of-type{font-size:14px;color:#fff;opacity:.85;}

/* top bar sits on the photo, so give it its own tint */
.flat-header-blog .top-bar{background:rgba(9,24,42,.55);border-bottom:1px solid rgba(255,255,255,.12);}
.top-bar .information{margin:0;padding:0;list-style:none;}
.top-bar .information li{display:inline-block;color:#fff;font-size:14px;margin-right:26px;}
.top-bar .information li i{margin-right:7px;color:#ff5f60;}
.top-bar .information li a{color:#fff;}

/* ---------- nav: 10 top-level items, up to 4 levels ---------- */
/* one row, always: logo left, menu right, never wrapping to a second line */
.menu-bar .menu-bar-wrap{
    padding:0;border-top:0;background:transparent;border-radius:0;
    display:flex;align-items:center;justify-content:space-between;flex-wrap:nowrap;gap:20px;}
.menu-bar #logo{margin:0;flex:0 0 auto;}
.header-menu{max-width:none;float:none;flex:1 1 auto;display:flex;justify-content:flex-end;}
#main-nav>ul.menu{display:flex;flex-wrap:nowrap;align-items:center;justify-content:flex-end;}
.main-nav .menu li{padding-left:0;}
.menu-bar #main-nav>ul>li{padding-top:26px;padding-bottom:26px;}
#main-nav>ul.menu>li>a{
    font-size:14px;padding:0 11px;white-space:nowrap;letter-spacing:.1px;position:relative;
    transition:color .22s ease;}
/* underline that grows from the centre on hover / active */
#main-nav>ul.menu>li>a:before{
    content:"";position:absolute;left:11px;right:11px;bottom:-6px;height:2px;background:#ff5f60;
    transform:scaleX(0);transform-origin:center;transition:transform .28s cubic-bezier(.2,.7,.3,1);}
#main-nav>ul.menu>li:hover>a:before,#main-nav>ul.menu>li.current>a:before{transform:scaleX(1);}
#main-nav>ul.menu>li>a:after{content:"";}
#main-nav>ul.menu>li.has-sub>a:after{
    content:"\\f107";font-family:FontAwesome;margin-left:6px;font-size:11px;opacity:.7;font-weight:400;}
/* dropdown panels — Edukin's dark panel, tightened for long labels */
#main-nav .sub-menu{
    background-color:#183251;margin-left:0;min-width:246px;padding:8px 0;line-height:1.45;
    border-top:3px solid #ff5f60;box-shadow:0 18px 40px rgba(9,24,42,.34);}
#main-nav .sub-menu li a{
    display:block;padding:9px 20px;font-size:13.5px;font-weight:500;color:#dfe7f1;white-space:normal;}
#main-nav .sub-menu li a:hover{background:rgba(255,255,255,.06);color:#ff5f60;}
/* level 3+ flyouts */
#main-nav .sub-menu li{position:relative;}
#main-nav .sub-menu .sub-menu{left:100%;top:-11px;border-top-width:3px;}
#main-nav .sub-menu li.has-sub>a:after{
    content:"\\f105";font-family:FontAwesome;position:absolute;right:16px;top:9px;opacity:.6;}
#main-nav .sub-menu li:hover>.sub-menu{opacity:1;visibility:visible;transform:translateY(0);}
#main-nav .sub-menu li:not(:hover)>.sub-menu{opacity:0;visibility:hidden;}
/* keep the last few menus from running off-screen */
.menu-bar #main-nav>ul>li:nth-last-child(-n+3) .sub-menu{left:auto;right:0;}
.menu-bar #main-nav>ul>li:nth-last-child(-n+3) .sub-menu .sub-menu{left:auto;right:100%;}
/* utility links in the top bar */
.top-utility{float:right;margin:0;padding:0;list-style:none;}
.top-utility li{display:inline-block;position:relative;margin-left:18px;}
.top-utility li a{color:#fff;font-size:13px;font-weight:500;text-transform:capitalize;}
.top-utility li a:hover{color:#ff5f60;}
.top-utility li:after{content:"";width:1px;height:12px;background:rgba(255,255,255,.3);position:absolute;right:-10px;top:4px;}
.top-utility li:last-of-type:after{display:none;}
#logo img{max-height:56px;width:auto;}

/* ---------- migrated body copy ---------- */
.migrate-content{font-size:16px;line-height:29px;color:#8a8a8a;}
.migrate-content h1,.migrate-content h2,.migrate-content h3,
.migrate-content h4,.migrate-content h5,.migrate-content h6{color:#183251;font-weight:600;line-height:1.35;}
.migrate-content>:first-child{margin-top:0;}
.migrate-content h1{font-size:28px;margin:0 0 22px;}
.migrate-content h2{font-size:23px;margin:34px 0 14px;}
.migrate-content h3{font-size:19px;margin:28px 0 12px;}
.migrate-content h4{font-size:17px;margin:24px 0 10px;}
.migrate-content h5,.migrate-content h6{font-size:15px;margin:20px 0 8px;}
.migrate-content h2:after,.migrate-content h1:after{
    content:"";display:block;width:52px;height:3px;background:#ff5f60;margin-top:13px;border-radius:2px;}
.migrate-content p{margin:0 0 18px;}
.migrate-content a{color:#ff5f60;font-weight:500;}
.migrate-content a:hover{text-decoration:underline;}
.migrate-content ul,.migrate-content ol{margin:0 0 20px;padding:0;list-style:none;}
.migrate-content ol{list-style:decimal;margin-left:22px;}
.migrate-content ul>li{position:relative;padding-left:28px;margin:10px 0;}
.migrate-content ul>li:before{
    content:"\\f00c";font-family:FontAwesome;position:absolute;left:0;top:1px;color:#7ecc88;font-size:13px;}
.migrate-content ol>li{margin:10px 0;padding-left:6px;}
.migrate-content img{max-width:100%;height:auto;border-radius:6px;margin:18px auto;display:block;}
.migrate-content blockquote{
    border-left:4px solid #ff5f60;background:#f7f9fc;margin:0 0 22px;padding:20px 26px;
    font-style:italic;color:#5c6b7f;}
.migrate-content table{width:100%;border-collapse:collapse;margin:0 0 24px;font-size:15px;}
.migrate-content th,.migrate-content td{border:1px solid #e7ebf1;padding:12px 15px;text-align:left;vertical-align:top;}
.migrate-content th{background:#183251;color:#fff;font-weight:600;}
.migrate-content tr:nth-child(even) td{background:#f7f9fc;}
.embed-wrap{position:relative;padding-bottom:56.25%;height:0;margin:20px 0;border-radius:6px;overflow:hidden;}
.embed-wrap iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0;}
.mig-empty-note{background:#fff7e6;border-left:4px solid #ffbe34;padding:16px 20px;color:#8a6d3b;}

/* full-width page: programme grid across the container, form band below */
.wide-page .wide-intro{max-width:none;margin-bottom:52px;}
.wide-page .wide-intro>h1,.wide-page .wide-intro>h2:first-child{
    text-align:center;border-top:0;padding-top:0;margin:0 0 40px;}
.wide-page .wide-intro>h2:first-child:after{margin-left:auto;margin-right:auto;}
.form-band{
    background:#fff;border:1px solid #eef1f5;border-radius:10px;padding:44px 48px;
    box-shadow:0 4px 26px rgba(24,50,81,.06);}
.form-band-title{font-size:24px;font-weight:600;color:#183251;margin:0 0 8px;}
.form-band-title:after{
    content:"";display:block;width:52px;height:3px;border-radius:2px;margin-top:14px;
    background:linear-gradient(90deg,#ff5f60,#ffbe34);}
@media(max-width:767px){.form-band{padding:26px 20px;}}

/* programme cards (folded out of the repeated fee tables) */
.prog-cards{margin-top:10px;}
/* across the full container these can run three-up */
.wide-page .prog-cards>div{flex:0 0 33.3333%;max-width:33.3333%;}
@media(max-width:991px){.wide-page .prog-cards>div{flex:0 0 50%;max-width:50%;}}
@media(max-width:575px){.wide-page .prog-cards>div{flex:0 0 100%;max-width:100%;}}
.prog-card{
    background:#fff;border:1px solid #eef1f5;border-radius:8px;padding:26px 26px 22px;height:100%;
    margin-bottom:26px;box-shadow:0 4px 22px rgba(24,50,81,.06);position:relative;overflow:hidden;
    transition:transform .3s cubic-bezier(.2,.7,.3,1),box-shadow .3s,border-color .3s;}
.prog-card:before{
    content:"";position:absolute;left:0;top:0;bottom:0;width:3px;
    background:linear-gradient(#ff5f60,#ffbe34);opacity:0;transition:opacity .3s;}
.prog-card:hover{transform:translateY(-5px);box-shadow:0 18px 44px rgba(24,50,81,.14);border-color:#fde3e3;}
.prog-card:hover:before{opacity:1;}
.pc-name{font-size:18px;font-weight:600;color:#183251;margin:0 0 16px;line-height:1.35;}
.pc-name:after{content:none;}
/* Rows, not columns: two cards sit inside an already-narrow content well,
   so three side-by-side chips force values like "06 sem / 03yrs" to break. */
.pc-meta{
    margin:0 0 18px;padding:0;list-style:none;background:#f7f9fc;border-radius:8px;overflow:hidden;}
.pc-meta li{
    display:flex;align-items:baseline;justify-content:space-between;gap:14px;
    padding:10px 16px;margin:0 !important;border-bottom:1px solid #edf1f6;}
.pc-meta li:last-child{border-bottom:0;}
.pc-meta li:before{content:none !important;}
.pc-meta .pm-k{
    font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:#a3b0c0;font-weight:600;
    flex:0 0 auto;}
.pc-meta .pm-v{
    font-size:14.5px;color:#183251;font-weight:500;text-align:right;line-height:1.35;}
.pc-note{font-size:14px;line-height:24px;color:#8a8a8a;margin-top:10px;}
.pc-note strong{color:#183251;font-weight:600;display:block;margin-bottom:3px;font-size:13.5px;}

/* role -> name roster table */
.mig-roster{width:100%;border-collapse:collapse;margin:6px 0 26px;font-size:15px;}
.mig-roster td{border:1px solid #e7ebf1;padding:12px 16px;vertical-align:top;}
.mig-roster td.rl{background:#f7f9fc;font-weight:600;color:#183251;width:52%;}
.mig-roster td.nm{color:#8a8a8a;}
.mig-roster tr:hover td{background:#fff2f2;}

/* downloads table */
.mig-downloads{width:100%;border-collapse:collapse;margin:8px 0 26px;}
.mig-downloads td{border:1px solid #e7ebf1;padding:12px 16px;vertical-align:middle;}
.mig-downloads td.dl-name{color:#5c6b7f;font-size:15px;}
.mig-downloads td.dl-act{width:130px;text-align:right;}
.mig-downloads tr:nth-child(even) td{background:#f7f9fc;}
.dl-btn{display:inline-block;background:#183251;color:#fff !important;padding:7px 18px;border-radius:20px;
    font-size:13px;font-weight:500;white-space:nowrap;}
.dl-btn:hover{background:#ff5f60;text-decoration:none !important;}
.dl-btn i{margin-right:6px;}

/* ---------- content column / sidebar shell ---------- */
.blog-single.content-blog{padding:80px 0 90px;background:#fff;}
.blog-single .site-content{
    background:#fff;border:1px solid #eef1f5;border-radius:6px;padding:44px 46px;
    box-shadow:0 4px 30px rgba(24,50,81,.06);}
.blog-single .sidebar .widget{
    background:#fff;border:1px solid #eef1f5;border-radius:6px;padding:26px 24px;margin-bottom:30px;
    box-shadow:0 4px 24px rgba(24,50,81,.05);}
.blog-single .sidebar .widget-title{
    font-size:18px;font-weight:600;color:#183251;margin:0 0 18px;padding-bottom:13px;border-bottom:1px solid #eef1f5;}
.blog-single .sidebar .widget-title span{position:relative;}
.blog-single .sidebar .widget-title span:after{
    content:"";position:absolute;left:0;bottom:-14px;width:44px;height:2px;background:#ff5f60;}
.sidebar .categories-wrap{margin:0;padding:0;list-style:none;}
.sidebar .categories-wrap li{border-bottom:1px solid #f3f5f8;}
.sidebar .categories-wrap li:last-child{border-bottom:0;}
.sidebar .categories-wrap li a{
    display:block;padding:10px 0 10px 20px;color:#8a8a8a;font-size:14px;position:relative;
    line-height:1.45;transition:.2s;}
.sidebar .categories-wrap li a:before{
    content:"\\f105";font-family:FontAwesome;position:absolute;left:2px;top:10px;color:#ff5f60;}
.sidebar .categories-wrap li a:hover{color:#ff5f60;padding-left:26px;}
.widget-downloads .categories-wrap li a:before{content:none;}
.widget-downloads .categories-wrap li a i{color:#ff5f60;margin-right:8px;}
.mig-contact{margin:0;padding:0;list-style:none;}
.mig-contact li{position:relative;padding:0 0 15px 28px;color:#8a8a8a;font-size:14px;line-height:1.6;}
.mig-contact li i{position:absolute;left:0;top:3px;color:#ff5f60;}
.mig-contact li a{color:#8a8a8a;}
.mig-contact li a:hover{color:#ff5f60;}
.widget-sent.widget{background:transparent !important;border:0 !important;box-shadow:none !important;padding:0 !important;}
.widget-sent .apply-admission-wrap{
    background:linear-gradient(135deg,#183251,#3f4c99) !important;border:0 !important;border-radius:6px;
    padding:34px 26px !important;text-align:center;}
.widget-sent .apply-admission-wrap .title span{color:#fff;font-size:21px;font-weight:600;}
.widget-sent .apply-admission-wrap .caption{color:rgba(255,255,255,.72);font-size:14px;margin:12px 0 22px;}
.widget-sent .mig-cta-btn .btn,.widget-sent .apply-admission-wrap .btn{
    display:inline-block;background:#ff5f60;color:#fff !important;padding:12px 30px;border-radius:24px;
    font-weight:500;font-size:14.5px;}
.widget-sent .apply-admission-wrap .btn:hover{background:#fff;color:#183251 !important;}

/* static forms */
.migrate-form{margin-top:16px;}
.migrate-form input,.migrate-form textarea{
    width:100%;padding:13px 16px;margin-bottom:18px;border:1px solid #e2e7ee;border-radius:4px;font-size:15px;
    font-family:inherit;color:#5c6b7f;}
.migrate-form input:focus,.migrate-form textarea:focus{outline:none;border-color:#ff5f60;}
.migrate-form .btn{background:#ff5f60;color:#fff;border:0;padding:14px 38px;border-radius:26px;font-weight:500;}
.migrate-form .btn:hover{background:#183251;}
.migrate-form-note{background:#fff7e6;border:1px solid #ffe2ad;color:#8a6d3b;padding:14px 18px;border-radius:4px;
    margin:20px 0;font-size:14px;}
.migrate-form-note i{margin-right:7px;color:#ffbe34;}

/* faculty portrait inside a bio */
.fac-photo{float:right;width:250px;margin:0 0 24px 30px;}
.fac-photo img{width:100%;border-radius:6px;box-shadow:0 10px 30px rgba(24,50,81,.16);margin:0;}

/* gallery grid (Edukin ships no gallery component) */
.gallery-grid{margin-top:6px;}
.gal-item{margin-bottom:26px;}
.gal-item a{display:block;border-radius:6px;overflow:hidden;box-shadow:0 6px 22px rgba(24,50,81,.1);}
.gal-item img{width:100%;height:238px;object-fit:cover;transition:.4s;}
.gal-item a:hover img{transform:scale(1.07);}

/* ---------- listing cards (Edukin .flat-course, extra bits) ---------- */
/* equal-height cards: Edukin's demo relies on fixed-length dummy copy */
.flat-courses .row{display:flex;flex-wrap:wrap;}
.flat-courses .course{margin-bottom:30px;display:flex;}
.flat-course{
    display:flex;flex-direction:column;width:100%;background:#fff;border:1px solid #eef1f5;border-radius:6px;
    overflow:hidden;box-shadow:0 4px 24px rgba(24,50,81,.07);transition:transform .3s,box-shadow .3s;}
.flat-course:hover{transform:translateY(-6px);box-shadow:0 18px 42px rgba(24,50,81,.16);}
.flat-course .course-content{flex:1;display:flex;flex-direction:column;padding:24px 24px 26px;}
.flat-course .wrap-course-content{flex:1;display:flex;flex-direction:column;}
.flat-course .author-info{margin-top:auto;padding-top:16px;}
.flat-course .enroll a{
    display:inline-block;color:#ff5f60 !important;font-weight:500;font-size:14px;
    border:1px solid #ffd2d2 !important;background:transparent !important;
    padding:7px 20px;border-radius:20px;transition:.25s;}
.flat-course .enroll a:hover{background:#ff5f60 !important;border-color:#ff5f60 !important;color:#fff !important;}
.flat-course .entry-image.pic img{width:100%;height:212px;object-fit:cover;}
.flat-course .course-content h4{font-size:18px;line-height:1.4;}
.flat-course .course-content h4 a{color:#183251;}
.flat-course .course-content h4 a:hover{color:#ff5f60;}
.flat-course .course-content p{font-size:14px;line-height:25px;}
.mig-noimg{width:100%;height:212px;background:linear-gradient(135deg,#183251,#3f4c99);position:relative;}
.mig-noimg:after{
    content:"\\f19d";font-family:FontAwesome;position:absolute;left:0;top:0;right:0;bottom:0;
    display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.18);font-size:56px;}
/* Edukin parks the caption at bottom:-31px so social icons can slide up on
   hover; our bios have no socials, so dock it and let names of any length fit. */
.team-box-layout-h1{
    margin-bottom:30px;background:#fff;border:1px solid #eef1f5;border-radius:6px;overflow:hidden;
    box-shadow:0 4px 22px rgba(24,50,81,.07);transition:transform .3s,box-shadow .3s;
    display:flex;flex-direction:column;height:calc(100% - 30px);}
.team-box-layout-h1:hover{transform:translateY(-5px);box-shadow:0 16px 38px rgba(24,50,81,.16);}
.team-box-layout-h1 .item-img img{
    width:100%;height:280px;object-fit:cover;object-position:center top;padding-bottom:0;display:block;}
.team-box-layout-h1 .item-content{
    position:static;background:#fffcf7;padding:18px 18px 20px;text-align:center;flex:1;
    display:flex;flex-direction:column;justify-content:center;}
.team-box-layout-h1 .item-title{margin-bottom:5px;line-height:1.35;}
.team-box-layout-h1 .item-title a{color:#183251;font-size:16px;}
.team-box-layout-h1 .item-title a:hover{color:#ff5f60;}
.team-box-layout-h1 .item-content .item-subtitle{font-size:13.5px;color:#8a8a8a;line-height:1.45;margin-bottom:0;}
.flat-team .row{display:flex;flex-wrap:wrap;}
.listing-intro{max-width:760px;margin:0 auto 52px;text-align:center;color:#8a8a8a;font-size:16px;line-height:29px;}

/* ---------- home: bits Edukin has no component for ---------- */
.prog-columns .prog-col{
    background:#fff;border:1px solid #eef1f5;border-radius:6px;padding:34px 32px;height:100%;
    box-shadow:0 6px 30px rgba(24,50,81,.07);}
.prog-columns .prog-col h3{
    font-size:20px;font-weight:600;color:#183251;margin:0 0 6px;}
.prog-columns .prog-col .prog-sub{font-size:14px;color:#ff5f60;font-weight:500;margin-bottom:20px;display:block;}
.prog-columns .prog-col ul{margin:0;padding:0;list-style:none;}
.prog-columns .prog-col ul li{position:relative;padding:9px 0 9px 30px;border-bottom:1px solid #f3f5f8;font-size:15px;color:#5c6b7f;}
.prog-columns .prog-col ul li:last-child{border-bottom:0;}
.prog-columns .prog-col ul li:before{
    content:"\\f19d";font-family:FontAwesome;position:absolute;left:0;top:10px;color:#ff5f60;font-size:14px;}
.prog-columns{display:flex;flex-wrap:wrap;}
.prog-columns .prog-col{transition:transform .3s cubic-bezier(.2,.7,.3,1),box-shadow .3s;}
.prog-columns .prog-col:hover{transform:translateY(-4px);box-shadow:0 18px 44px rgba(24,50,81,.12);}
.prog-note{font-size:14.5px;line-height:26px;color:#8a8a8a;margin:22px 0 0;}
.ajas-programmes .pd-top60{padding-top:74px;}
.ajas-programmes .flat-courses{margin-top:6px;}
.mig-quicklinks{margin:0;padding:0;list-style:none;}
.mig-clubs .club-chip{
    display:block;background:#fff;border:1px solid #eef1f5;border-radius:6px;padding:18px 20px;margin-bottom:22px;
    color:#183251;font-size:15px;font-weight:500;transition:.25s;box-shadow:0 4px 18px rgba(24,50,81,.05);}
.mig-clubs .club-chip:hover{background:#183251;color:#fff;transform:translateY(-4px);
    box-shadow:0 14px 30px rgba(24,50,81,.18);}
.mig-clubs .club-chip i{color:#ff5f60;margin-right:10px;}
.mig-clubs .club-chip:hover i{color:#fff;}
.mig-clubs .chip-note{font-size:14px;line-height:25px;color:#8a8a8a;margin:-12px 0 30px;padding:0 4px;}

/* footer additions */
.logo-footer .footer-brand-text{color:#fff;font-size:26px;font-weight:600;line-height:1.15;display:block;}
.logo-footer .footer-brand-text span{display:block;font-size:14px;font-weight:400;color:rgba(255,255,255,.6);margin-top:6px;}
#footer .footer-address{color:rgba(255,255,255,.65);font-size:14px;line-height:26px;margin-top:18px;}
#footer .footer-address li{position:relative;padding-left:26px;margin-bottom:10px;list-style:none;}
#footer .footer-address li i{position:absolute;left:0;top:5px;color:#ff5f60;}
#footer .footer-address li a{color:rgba(255,255,255,.65);}
#footer .footer-address li a:hover{color:#ff5f60;}

/* ============================================================
   Placeholder replacement.
   The Edukin package ships blank grey art in every photo and icon
   slot. Each one below is re-pointed at a college photograph or a
   Font Awesome glyph so the page matches the template's live demo.
   ============================================================ */
.ajas-icon{
    display:inline-block;width:74px;height:74px;line-height:74px;text-align:center;border-radius:50%;
    background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.28);}
.ajas-icon i{font-size:30px;color:#fff;line-height:74px;}
.iconbox-icon .ajas-icon{width:64px;height:64px;line-height:64px;}
.iconbox-icon .ajas-icon i{font-size:26px;line-height:64px;}

/* facilities band (was images/home1/parallax1.jpg — blank) */
.flat-services.style1.parallax1,.parallax1{
    background-image:url('uploads/2025/03/WhatsApp-Image-2025-03-17-at-4.16.10-PM.jpeg') !important;
    background-size:cover;background-position:center;}
.flat-services.style1 .section-overlay{background:rgba(255,95,96,.90);}
.flat-services.style1{padding:88px 0;}
.flat-imagebox.imagebox-services .imagebox-content h5{margin-top:26px;margin-bottom:16px;}
/* these two sections use .container-fluid, which runs text to the viewport edge */
.flat-services.style1>.container-fluid,.flat-benefit.style1>.container-fluid,
.flat-event.flat-event-style1>.container-fluid{
    max-width:1200px;margin:0 auto;padding-left:15px;padding-right:15px;}

/* why-choose band (was images/home1/17.png — blank) */
.flat-benefit.style1{
    background-image:linear-gradient(105deg,rgba(15,33,53,.96) 0%,rgba(24,50,81,.93) 55%,rgba(31,66,107,.88) 100%),
        url('uploads/2024/01/building-admin-P1222310-1024x577-copy-1.png') !important;
    background-size:cover;background-position:center;}
.flat-benefit.style1 .iconbox-content h3 a{color:#fff;font-size:19px;}
.flat-benefit.style1 .iconbox-content h3 a:hover{color:#ff5f60;}
.flat-benefit.style1 .iconbox-content p{color:rgba(255,255,255,.72);font-size:14.5px;line-height:26px;}
.flat-benefit.style1 .iconbox{margin-bottom:42px;}
.flat-benefit.style1 .col-benefit-left{padding-right:60px;}
.flat-benefit .form-apply .apply-now .btn-50 .btn,
.flat-benefit .form-apply .btn,.flat-benefit .btn-50 .btn,
.flat-benefit .btn-50.hv-border .btn{
    background:#ff5f60 !important;color:#fff !important;padding:15px 44px !important;border-radius:28px !important;
    font-weight:500;font-size:15px;display:inline-block !important;border:2px solid #ff5f60 !important;
    width:auto !important;height:auto !important;line-height:1 !important;opacity:1 !important;
    box-shadow:0 14px 32px rgba(255,95,96,.4);transition:.28s cubic-bezier(.2,.7,.3,1);}
.flat-benefit .form-apply .btn:hover,.flat-benefit .btn-50 .btn:hover{
    background:#fff !important;border-color:#fff !important;color:#183251 !important;transform:translateY(-3px);}
.flat-benefit .btn-50{margin-top:26px;}
/* .section-overlay183251 is a translucent sheet painted over the form —
   lift the form itself above it or the fields and button look greyed out */
.flat-benefit .form-apply{position:relative;}
.flat-benefit .form-apply .section-overlay183251{z-index:0;}
.flat-benefit .form-apply .apply-now{position:relative;z-index:2;}
.flat-benefit .form-apply input::placeholder{color:rgba(255,255,255,.72);}
/* Edukin's staggered event collage depends on its demo images' exact sizes;
   ours are posters of every shape, so lay them out as a plain stacked grid. */
.ajas-events .images-list{
    display:grid;grid-template-columns:1fr 1fr;grid-gap:18px;height:auto !important;padding:0 !important;}
.ajas-events .images-list-1,.ajas-events .images-list-2{
    display:contents;position:static !important;transform:none !important;}
.ajas-events .img-event{
    position:relative;overflow:hidden;border-radius:8px;margin:0 !important;
    box-shadow:0 14px 38px rgba(24,50,81,.16);float:none !important;width:auto !important;}
.ajas-events .images-list-1 .img-event:first-child{grid-column:1 / -1;}
.ajas-events .img-event img{
    width:100%;height:250px;object-fit:cover;display:block;transition:transform .5s cubic-bezier(.2,.7,.3,1);}
.ajas-events .images-list-1 .img-event:first-child img{height:300px;}
.ajas-events .img-event:hover img{transform:scale(1.06);}
.ajas-events .img-event .number{
    position:absolute;left:16px;top:16px;width:38px;height:38px;line-height:38px;text-align:center;
    border-radius:50%;color:#fff;font-weight:600;font-size:15px;z-index:2;}

/* quick-link band (was images/home1/parallax2.jpg — blank) */
.parallax2{
    background-image:url('uploads/2025/03/WhatsApp-Image-2025-03-17-at-4.01.34-PM.jpeg') !important;
    background-size:cover;background-position:center 30%;}
.quick-link .section-overlay{background:rgba(15,33,53,.90);}
.quick-link.quick-link-style1{padding:96px 0;}

/* footer band (was images/footer/01.png — blank) */
#footer.footer-type1{
    background-image:linear-gradient(rgba(12,28,48,.97),rgba(12,28,48,.97)),
        url('uploads/2024/01/P1222323-building-2048x1154-1.webp') !important;
    background-size:cover;background-position:center;}
/* accreditation band at the top of the footer, on every page */
.footer-trust{
    border-bottom:1px solid rgba(255,255,255,.10);background:rgba(0,0,0,.16);padding:32px 0 28px;
    text-align:center;}
.trust-line{
    color:rgba(255,255,255,.62);font-size:13.5px;letter-spacing:.4px;margin:0 0 22px;line-height:1.7;}
.trust-marks{
    display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:12px 40px;
    margin:0;padding:0;list-style:none;}
.trust-marks li{
    display:flex;flex-direction:column;align-items:center;gap:9px;list-style:none;}
/* the seals are dark artwork on white, so they need a light chip to read
   against the navy footer — greyscaling them just produced pale blobs */
.trust-marks img{
    height:56px;width:auto;display:block;background:#fff;border-radius:8px;padding:6px 10px;
    box-shadow:0 4px 14px rgba(0,0,0,.22);transition:transform .3s cubic-bezier(.2,.7,.3,1);}
.trust-marks li:hover img{transform:translateY(-3px);}
.trust-marks span{
    font-size:10.5px;letter-spacing:1.3px;text-transform:uppercase;color:rgba(255,255,255,.55);
    font-weight:600;white-space:nowrap;}
@media(max-width:767px){
    .footer-trust{padding:26px 0 22px;}
    .trust-line{font-size:12.5px;}
    .trust-marks{gap:14px 22px;}
    .trust-marks img{height:32px;}
    .trust-marks span{display:none;}
}
#footer #footer-widget{padding:78px 0 54px;}
#footer #footer-widget h3.widget.widget-title,
#footer #footer-widget .widget.widget-title{color:#fff !important;font-size:18px;margin-bottom:22px;font-weight:600;}
#footer #footer-widget .widget-nav-menu li{margin-bottom:11px;list-style:none;}
#footer #footer-widget .widget-nav-menu li a{color:rgba(255,255,255,.64) !important;font-size:14.5px;}
#footer #footer-widget .widget-nav-menu li a:hover{color:#ff5f60 !important;}
#footer .widget-social-media li{display:inline-block;margin-right:9px;}
#footer .widget-social-media li a i{
    width:40px;height:40px;line-height:40px;text-align:center;border-radius:50%;
    background:rgba(255,255,255,.1);color:#fff;font-size:16px;display:inline-block;transition:.25s;}
#footer .widget-social-media li a i:hover{background:#ff5f60;}
#bottom.bottom-type1{background:rgba(0,0,0,.28);padding:20px 0;}
#bottom #copyright,#bottom #copyright a{color:rgba(255,255,255,.5);font-size:13.5px;}
#bottom ul.bottom-nav{margin:0;padding:0;list-style:none;float:right;}
#bottom ul.bottom-nav>li{display:inline-block;margin-left:22px;}
#bottom ul.bottom-nav>li>a{color:rgba(255,255,255,.5);font-size:13.5px;}
#bottom ul.bottom-nav>li>a:hover{color:#ff5f60;}

/* principal photo panel (Edukin's decorative dot art was blank — dropped) */
.flat-introduce-style1{padding:70px 0 96px;}
.flat-introduce .videobox{position:relative;display:inline-block;}
.flat-introduce .videobox img{
    width:100%;border-radius:8px;box-shadow:0 26px 64px rgba(24,50,81,.24);position:relative;z-index:1;
    display:block;}
/* offset frame anchored to the photo's own corners, not floating beside it */
.flat-introduce .videobox:after{
    content:"";position:absolute;left:-22px;bottom:-22px;width:62%;height:62%;
    border-left:4px solid #ff5f60;border-bottom:4px solid #ff5f60;border-radius:0 0 0 8px;
    opacity:.35;z-index:0;}

/* Edukin's read-more pill, unstyled in the shipped CSS */
.btn-box-shadow{
    display:inline-block;background:#ff5f60;color:#fff !important;padding:13px 32px;border-radius:26px;
    font-weight:500;font-size:14.5px;box-shadow:0 10px 26px rgba(255,95,96,.3);transition:.25s;}
.btn-box-shadow:hover{background:#183251;box-shadow:0 10px 26px rgba(24,50,81,.28);color:#fff !important;}
.content-introduce .btn-about{margin-top:26px;}

/* ---------- home page ---------- */
/* Edukin's nav text is white, so the in-flow home header needs a dark ground.
   No z-index here: it would trap the sticky header in a stacking context and
   let later sections (the admissions card) paint over it. */
/* Edukin's .flat-header is position:absolute so the demo header floats over a
   transparent hero. Ours is a solid bar, so it must sit in flow — otherwise it
   covers the top ~140px of the slider and clips the kicker line. */
.wrap-header{position:relative;z-index:auto;}
.ajas-home-header{background:#183251;position:static;}
.ajas-home-header .top-bar{background:rgba(0,0,0,.24);border-bottom:1px solid rgba(255,255,255,.1);}
.ajas-home-header #logo img{filter:brightness(0) invert(1);}
.bg-header #logo img{filter:brightness(0) invert(1);}

/* ---------- sticky header: compact, navy, above everything ---------- */
.header.menu-bar{transition:background .3s ease,box-shadow .3s ease;}
.header.header-sticky{
    background:rgba(18,40,66,.97) !important;
    -webkit-backdrop-filter:saturate(160%) blur(10px);backdrop-filter:saturate(160%) blur(10px);
    box-shadow:0 10px 30px rgba(9,24,42,.28) !important;z-index:100000 !important;}
.header.header-sticky .menu-bar-wrap{padding:0;}
/* while the hero is still on screen, the bar stays in flow and scrolls away */
body.hero-hold .header.header-sticky{
    position:static !important;background:transparent !important;box-shadow:none !important;
    -webkit-backdrop-filter:none;backdrop-filter:none;animation:none !important;}
body.hero-hold .header-sticky #logo img{max-height:56px !important;}
body.hero-hold .header-sticky.menu-bar #main-nav>ul>li{padding-top:26px;padding-bottom:26px;}
body.hero-hold .header-sticky #main-nav>ul.menu>li>a{font-size:14px;}
.header-sticky #logo img{max-height:38px !important;transition:max-height .3s ease;}
.header-sticky.menu-bar #main-nav>ul>li{padding-top:15px;padding-bottom:15px;}
.header-sticky #main-nav>ul.menu>li>a{font-size:13.5px;}
#logo img{transition:max-height .3s ease;}
/* the admissions card overlaps the strip below the slider — keep it under the nav */
.partner-clients .iconbox-style1{position:relative;z-index:5;}

/* ---------- hero (static markup, CSS-only cross-fade) ---------- */
.ajas-hero{position:relative;overflow:hidden;background:#0c1e34;padding:120px 0 104px;}
.hero-media{position:absolute;left:0;top:0;right:0;bottom:0;z-index:0;}
.hero-layer{
    position:absolute;left:0;top:0;right:0;bottom:0;background-size:cover;background-position:center 42%;
    opacity:0;animation:heroFade 21s infinite;}
.hero-layer.hl1{animation-delay:0s;}
.hero-layer.hl2{animation-delay:7s;}
.hero-layer.hl3{animation-delay:14s;}
@keyframes heroFade{
    0%{opacity:0}   4%{opacity:1}   30%{opacity:1}   36%{opacity:0}   100%{opacity:0}
}
.hero-scrim{
    position:absolute;left:0;top:0;right:0;bottom:0;
    background:linear-gradient(100deg,rgba(9,24,42,.94) 0%,rgba(11,30,52,.86) 42%,rgba(11,30,52,.52) 100%);}
.ajas-hero .container{position:relative;z-index:2;}
.hero-inner{max-width:720px;}
.hero-kicker{
    font-size:13px;letter-spacing:3.2px;text-transform:uppercase;color:#ffbe34;font-weight:600;margin:0 0 20px;}
.hero-title{
    font-size:56px;line-height:1.1;font-weight:600;color:#fff;margin:0 0 22px;letter-spacing:-1px;}
.hero-text{font-size:17px;line-height:31px;color:rgba(255,255,255,.8);margin:0 0 34px;max-width:620px;}
.hero-cta{display:flex;flex-wrap:wrap;gap:14px;margin-bottom:52px;}
.hero-btn{
    display:inline-block;padding:16px 36px;border-radius:30px;font-size:15px;font-weight:500;
    border:2px solid transparent;transition:.28s cubic-bezier(.2,.7,.3,1);}
.hero-btn-primary{
    background:#ff5f60;border-color:#ff5f60;color:#fff;box-shadow:0 14px 34px rgba(255,95,96,.36);}
.hero-btn-primary:hover{
    background:#fff;border-color:#fff;color:#183251;transform:translateY(-3px);}
.hero-btn-ghost{background:transparent;border-color:rgba(255,255,255,.55);color:#fff;}
.hero-btn-ghost:hover{background:#fff;border-color:#fff;color:#183251;transform:translateY(-3px);}
.hero-facts{
    display:flex;flex-wrap:wrap;gap:14px 48px;margin:0;padding:26px 0 0;list-style:none;
    border-top:1px solid rgba(255,255,255,.16);}
.hero-facts li{list-style:none;margin:0;}
.hero-facts strong{
    display:block;font-size:30px;font-weight:600;color:#fff;line-height:1.1;letter-spacing:-.6px;}
.hero-facts span{
    display:block;font-size:12px;letter-spacing:1.6px;text-transform:uppercase;
    color:rgba(255,255,255,.6);margin-top:6px;font-weight:500;}
@media(prefers-reduced-motion:reduce){
    .hero-layer{animation:none;}
    .hero-layer.hl1{opacity:1;}
}
/* Edukin's .btn-styl2 is a fixed-size round play button; ours is a text
   button, so every one of its circle dimensions has to be unset. */
.ajas-slider .tp-caption .btn-styl1,.ajas-slider .tp-caption .ajas-btn-ghost{
    display:inline-block !important;width:auto !important;height:auto !important;
    line-height:1 !important;border-radius:30px !important;font-weight:500;font-size:15px;
    letter-spacing:.2px;text-align:center;vertical-align:middle;transition:.28s cubic-bezier(.2,.7,.3,1);}
.ajas-slider .tp-caption .btn-styl1{
    background:#ff5f60 !important;color:#fff !important;padding:17px 38px !important;margin-right:14px;
    border:2px solid #ff5f60 !important;box-shadow:0 14px 34px rgba(255,95,96,.36);}
.ajas-slider .tp-caption .btn-styl1:hover{
    background:#fff !important;border-color:#fff !important;color:#183251 !important;
    transform:translateY(-3px);box-shadow:0 18px 40px rgba(0,0,0,.3);}
.ajas-slider .tp-caption .ajas-btn-ghost{
    background:transparent !important;border:2px solid rgba(255,255,255,.65) !important;color:#fff !important;
    padding:17px 36px !important;}
.ajas-slider .tp-caption .ajas-btn-ghost:hover{
    background:#fff !important;border-color:#fff !important;color:#183251 !important;transform:translateY(-3px);}
.ajas-slider .tp-caption .ajas-btn-ghost:before,.ajas-slider .tp-caption .ajas-btn-ghost:after{content:none !important;}
.ajas-slider .tp-bullet{background:rgba(255,255,255,.45);width:10px;height:10px;border-radius:50%;}
.ajas-slider .tp-bullet.selected{background:#ff5f60;}

/* quick-action tiles straddling the bottom of the hero */
.ajas-actions{position:relative;z-index:6;margin-top:-72px;padding-bottom:8px;}
.action-tile{
    display:flex;align-items:center;gap:18px;padding:26px 26px;border-radius:10px;min-height:118px;
    box-shadow:0 18px 44px rgba(9,24,42,.20);position:relative;overflow:hidden;
    transition:transform .3s cubic-bezier(.2,.7,.3,1),box-shadow .3s;}
.action-tile:hover{transform:translateY(-6px);box-shadow:0 26px 56px rgba(9,24,42,.28);}
.action-tile .tile-ico{
    flex:0 0 auto;width:54px;height:54px;line-height:54px;text-align:center;border-radius:50%;
    background:rgba(255,255,255,.18);}
.action-tile .tile-ico i{font-size:22px;line-height:54px;}
.action-tile .tile-body{flex:1 1 auto;min-width:0;}
.action-tile .tile-title{display:block;font-size:17px;font-weight:600;line-height:1.3;margin-bottom:5px;}
.action-tile .tile-sub{display:block;font-size:13.5px;line-height:1.45;opacity:.82;}
.action-tile .tile-cta{
    position:absolute;right:26px;bottom:14px;font-size:12.5px;font-weight:600;letter-spacing:1px;
    text-transform:uppercase;opacity:.85;transition:.25s;}
.action-tile:hover .tile-cta{opacity:1;}
.action-tile .tile-cta i{margin-left:5px;transition:transform .25s;}
.action-tile:hover .tile-cta i{transform:translateX(5px);}
.tile-primary{background:linear-gradient(135deg,#ff5f60,#f0484e);color:#fff;}
.tile-primary .tile-title,.tile-primary .tile-cta,.tile-primary .tile-ico i{color:#fff;}
.tile-navy{background:linear-gradient(135deg,#183251,#28477a);color:#fff;}
.tile-navy .tile-title,.tile-navy .tile-cta,.tile-navy .tile-ico i{color:#fff;}
.tile-light{background:#fff;color:#5c6b7f;border:1px solid #eef1f5;}
.tile-light .tile-ico{background:#fff4f4;}
.tile-light .tile-ico i,.tile-light .tile-cta{color:#ff5f60;}
.tile-light .tile-title{color:#183251;}
@media(max-width:991px){
    .ajas-actions{margin-top:-34px;}
    .action-tile{margin-bottom:22px;min-height:0;}
}

/* accreditation strip */
.ajas-accred{padding:58px 0 54px;text-align:center;background:#fff;}
.accred-label{
    font-size:12px;letter-spacing:3px;text-transform:uppercase;color:#a3b0c0;font-weight:600;margin:0 0 30px;}
.accred-row{
    display:flex;align-items:flex-end;justify-content:center;gap:58px;margin:0;padding:0;list-style:none;
    flex-wrap:wrap;}
.accred-row li{list-style:none;text-align:center;}
.accred-row img{
    height:78px;width:auto;display:block;margin:0 auto 12px;
    filter:grayscale(100%);opacity:.58;transition:filter .3s ease,opacity .3s ease,transform .3s ease;}
.accred-row li:hover img{filter:none;opacity:1;transform:translateY(-4px);}
.accred-row span{
    display:block;font-size:11.5px;letter-spacing:1.2px;text-transform:uppercase;color:#b3bdc9;font-weight:600;}
.accred-row li:hover span{color:#183251;}
.ajas-apply-btn{
    display:inline-block;background:#ff5f60;color:#fff !important;padding:13px 34px;border-radius:26px;
    font-weight:500;font-size:15px;border:0;}
.ajas-apply-btn:hover{background:#183251;color:#fff !important;}
.apply-admission-wrap .ajas-apply-btn{background:#183251;}
.apply-admission-wrap .ajas-apply-btn:hover{background:#0f2135;}
.apply-sent.apply-sent-style1{text-align:center;padding-top:6px;}

/* section rhythm */
.ajas-programmes{padding:96px 0 100px;}
.pd-top60{padding-top:60px;}
.pd-top30{padding-top:30px;}
.ajas-programmes .listing-intro{margin-bottom:44px;}
.ajas-news{padding:90px 0 100px;background:#f7f9fc;}
.ajas-success{padding:96px 0 90px;}
.ajas-events .content-event-list{margin-top:10px;}
.ajas-testi-role{font-size:13.5px;color:#98a5b5;margin-top:7px;letter-spacing:.3px;}
.ajas-success .iconbox-about{padding-top:24px;}
.textbox-about .btn-about a,.btn-about .btn-box-shadow{background:#ff5f60 !important;color:#fff !important;}
.textbox-about .btn-about a:hover,.btn-about .btn-box-shadow:hover{background:#183251 !important;}
.ajas-services .read-more a{color:#fff;font-weight:500;}
.ajas-services .read-more a:hover{color:#183251;}
.ajas-benefit .iconbox-content h3 a{color:#fff;}
.ajas-quicklink .info-quick-link li img{max-height:30px;width:auto;}

/* Campus news carousel — Edukin's card assumes a fixed-ratio demo image
   and an author avatar; ours has neither, so re-balance the two columns. */
.ajas-news .post-bg{background:#fff3f3;overflow:hidden;}
.ajas-news .post-bg .bg{display:flex;align-items:stretch;}
.ajas-news .post-bg .bg .position{
    float:none;flex:0 0 auto;padding:26px 26px;color:#ff5f60;letter-spacing:3px;}
.ajas-news .post-bg .bg .featured-post{float:none;flex:1;transform:translateY(-14px);padding-right:0;}
.ajas-news .post-bg .featured-post img{width:100%;height:236px;object-fit:cover;border-radius:4px;display:block;}
.ajas-news .post-content{padding:22px 30px 30px !important;}
.ajas-news .post-content .entry-info{margin-bottom:6px;}
.ajas-news .post-title h5{margin:0;}
.ajas-news .post-title h5 a{font-size:18px;line-height:1.45;color:#183251;font-weight:600;}
.ajas-news .post-title h5 a:hover{color:#ff5f60;}
.ajas-news .post-content .post-link{margin-left:0 !important;margin-top:16px !important;}
.ajas-news .post-content .post-link a{color:#ff5f60;font-size:15px;}
.ajas-news .owl-dots{margin-top:34px;}

/* Testimonials — Edukin scatters avatars over an illustration that ships
   blank; use a campus photo and cluster the avatars instead. */
.ajas-testimonials .wrap-info{
    background-image:linear-gradient(135deg,rgba(24,50,81,.90),rgba(63,76,153,.86)),
        url('uploads/2025/03/WhatsApp-Image-2025-03-17-at-4.20.43-PM.jpeg') !important;
    background-size:cover !important;background-position:center !important;
    display:flex;align-items:center;justify-content:center;padding:70px 40px !important;}
.ajas-testimonials .wrap-info .flexslider{width:100%;background:none;border:0;margin:0;}
.ajas-testimonials .wrap-info .flex-viewport{overflow:visible !important;height:auto !important;}
.ajas-testimonials .wrap-info ul.slides{
    display:flex !important;flex-wrap:wrap;justify-content:center;align-items:center;gap:18px;
    transform:none !important;width:auto !important;margin:0;padding:0;}
.ajas-testimonials .wrap-info ul li.avatar{
    position:static !important;top:auto !important;left:auto !important;bottom:auto !important;
    width:auto !important;float:none !important;display:block !important;opacity:1 !important;}
.ajas-testimonials .wrap-info ul li.avatar img{
    width:88px;height:88px;border-radius:50%;object-fit:cover;object-position:center top;
    border:4px solid rgba(255,255,255,.28);box-shadow:0 10px 26px rgba(0,0,0,.24);}
.ajas-testimonials .wrap-quote{
    background-image:none !important;background:#f7f9fc;
    padding:80px 70px !important;display:flex;align-items:center;min-height:100%;}
.ajas-testimonials{display:flex;flex-wrap:wrap;}
.ajas-testimonials .wrap-info,.ajas-testimonials .wrap-quote{width:50%;float:none;}
@media(max-width:991px){.ajas-testimonials .wrap-info,.ajas-testimonials .wrap-quote{width:100%;}}
.ajas-testimonials .wrap-quote .flexslider{width:100%;background:none;border:0;}
.ajas-testimonials .wrap-quote .client-info li .speech{
    font-size:17px;line-height:31px;color:#5c6b7f;margin:26px 0 20px;}
.ajas-testimonials .wrap-quote .client-info li .name{color:#183251;font-size:17px;}
.ajas-testimonials .wrap-quote .flex-control-nav{
    writing-mode:horizontal-tb;text-orientation:mixed;position:static;margin-top:26px;text-align:center;}
.ajas-testimonials .wrap-quote .flex-control-nav li{display:inline-block;margin:0 5px;}
.ajas-testimonials .wrap-quote .flex-control-paging li a{background:#d5dde7;width:10px;height:10px;}
.ajas-testimonials .wrap-quote .flex-control-paging li a.flex-active{background:#ff5f60;}
.ajas-events .img-event img{width:100%;height:100%;object-fit:cover;}

/* blog listing cards */
.post-blog.box-shadow-type2{
    margin-bottom:40px;border:1px solid #eef1f5;border-radius:6px;overflow:hidden;background:#fff;
    box-shadow:0 4px 26px rgba(24,50,81,.07);}
.post-blog .featured-post img{width:100%;height:330px;object-fit:cover;display:block;}
.post-blog .content-post-blog{padding:30px 32px 34px;}
.post-blog .entry-title{font-size:22px;line-height:1.35;margin:0 0 14px;font-weight:600;}
.post-blog .entry-title a{color:#183251;}
.post-blog .entry-title a:hover{color:#ff5f60;}
.post-blog .content-post-blog p{font-size:15px;line-height:27px;margin-bottom:18px;}
.post-blog .entry-date{font-size:13.5px;color:#98a5b5;margin-bottom:14px;letter-spacing:.3px;}
.post-blog .post-meta{float:left;margin-right:26px;}
.post-blog .clendar-wrap{
    background:#ff5f60;color:#fff;border-radius:6px;text-align:center;padding:12px 0;width:72px;
    margin-top:-52px;position:relative;z-index:2;box-shadow:0 8px 20px rgba(255,95,96,.32);}
.post-blog .clendar-wrap .day{font-size:24px;font-weight:600;line-height:1.1;}
.post-blog .clendar-wrap .month{font-size:12px;letter-spacing:1.4px;}
.post-blog .content-post-inner{overflow:hidden;}
.ajas-post-date{font-size:13px;color:#98a5b5;margin-top:6px;}
.post-blog .readmore{color:#ff5f60;font-weight:500;font-size:14px;}
.post-blog .readmore i{margin-left:5px;}
.blog-bl .site-content{background:transparent;border:0;box-shadow:none;padding:0;}

/* ============================================================
   Motion. Everything is opt-in via .has-reveal, so with JS off or
   prefers-reduced-motion on, content renders plainly and in place.
   ============================================================ */
.has-reveal .reveal{
    opacity:0;
    transition:opacity .75s cubic-bezier(.2,.7,.3,1),transform .75s cubic-bezier(.2,.7,.3,1);
    will-change:opacity,transform;}
.has-reveal .rv-up{transform:translateY(30px);}
.has-reveal .rv-left{transform:translateX(-34px);}
.has-reveal .rv-right{transform:translateX(34px);}
.has-reveal .rv-zoom{transform:scale(.92);}
.has-reveal .rv-fade{transform:none;}
.has-reveal .reveal.is-in{opacity:1;transform:none;}
@media(prefers-reduced-motion:reduce){
    .has-reveal .reveal{opacity:1 !important;transform:none !important;transition:none !important;}
    html{scroll-behavior:auto !important;}
}
/* sideways entrances would push past a phone viewport mid-transition */
@media(max-width:991px){
    .has-reveal .rv-left,.has-reveal .rv-right{transform:translateY(22px);}
}

/* ============================================================
   Section furniture — consistent kicker + title across the site.
   ============================================================ */
.title-section{margin-bottom:16px;}
.title-section .sub-title{
    font-size:12.5px;letter-spacing:3px;text-transform:uppercase;color:#ff5f60;font-weight:600;margin-bottom:14px;}
.flat-title.medium{font-size:40px;line-height:1.18;color:#183251;}
.flat-title.larger{font-size:42px;line-height:1.15;color:#183251;}
.flat-title.small{font-size:34px;line-height:1.2;}
.title-section.text-center .flat-title{position:relative;display:inline-block;padding-bottom:20px;}
.title-section.text-center .flat-title:after{
    content:"";position:absolute;left:50%;bottom:0;width:64px;height:3px;border-radius:2px;
    background:linear-gradient(90deg,#ff5f60,#ffbe34);transform:translateX(-50%);}
.listing-intro{max-width:760px;margin:0 auto 52px;text-align:center;color:#8a8a8a;font-size:16.5px;line-height:30px;}

/* ---------- staff rosters ---------- */
.roster-page .migrate-content{max-width:none;}
.people-grid{margin-top:8px;}
.people-card{
    display:flex;flex-direction:column;width:100%;
    background:#fff;border:1px solid #eef1f5;border-radius:10px;overflow:hidden;margin-bottom:30px;
    box-shadow:0 4px 22px rgba(24,50,81,.07);
    transition:transform .3s cubic-bezier(.2,.7,.3,1),box-shadow .3s,border-color .3s;}
.people-card .pg-body{flex:1;}
.people-card:hover{
    transform:translateY(-6px);box-shadow:0 20px 46px rgba(24,50,81,.16);border-color:#fde3e3;}
.pg-photo{position:relative;overflow:hidden;background:#f2f5f9;}
.pg-photo img{
    width:100%;height:290px;object-fit:cover;object-position:center 18%;display:block;
    transition:transform .55s cubic-bezier(.2,.7,.3,1);}
.people-card:hover .pg-photo img{transform:scale(1.06);}
.pg-photo .mig-noimg{height:290px;}
.pg-body{padding:20px 20px 22px;text-align:center;}
.pg-name{font-size:16.5px;font-weight:600;color:#183251;margin:0 0 6px;line-height:1.35;}
.pg-name:after{content:none;}
.pg-role{font-size:13.5px;color:#8a8a8a;margin:0;line-height:1.5;}
.people-grid>div{display:flex;}
@media(max-width:767px){
    .pg-photo img,.pg-photo .mig-noimg{height:210px;}
    .pg-body{padding:14px 12px 16px;}
    .pg-name{font-size:14.5px;}
    .pg-role{font-size:12.5px;}
}

/* ---------- profile pages (principal / vice-principal / faculty) ---------- */
.profile-page{padding-top:0 !important;}
.profile-card{
    display:flex;align-items:center;gap:52px;background:#fff;border:1px solid #eef1f5;border-radius:12px;
    padding:46px 52px;margin-top:-58px;position:relative;z-index:3;
    box-shadow:0 26px 64px rgba(9,24,42,.18);}
.profile-role{
    display:block;font-size:13px;letter-spacing:2.8px;text-transform:uppercase;color:#ff5f60;
    font-weight:600;margin-bottom:12px;}
.profile-photo{flex:0 0 auto;width:380px;max-width:44%;}
.profile-photo img{
    width:100%;height:450px;object-fit:cover;object-position:center 20%;border-radius:10px;display:block;
    box-shadow:0 22px 52px rgba(24,50,81,.26);}
.profile-photo .mig-noimg{width:100%;height:450px;border-radius:10px;}
.profile-head{flex:1 1 auto;min-width:0;}
.profile-name{
    font-size:38px;font-weight:600;color:#183251;line-height:1.15;margin:0 0 18px;}
.profile-name:after{content:"";display:block;width:56px;height:3px;border-radius:2px;margin-top:16px;
    background:linear-gradient(90deg,#ff5f60,#ffbe34);}
.profile-meta{margin:0 0 20px;padding:0;list-style:none;display:flex;flex-wrap:wrap;gap:10px;}
.profile-meta li{
    background:#f7f9fc;border:1px solid #eef1f5;border-radius:20px;padding:7px 18px;
    font-size:14px;color:#5c6b7f;margin:0;}
.profile-meta li:first-child{background:#fff4f4;border-color:#ffd9d9;color:#183251;font-weight:500;}
.profile-back{
    display:inline-block;font-size:13.5px;font-weight:500;color:#ff5f60;transition:.2s;}
.profile-back:hover{color:#183251;}
.profile-back i{margin-right:5px;transition:transform .2s;}
.profile-back:hover i{transform:translateX(-4px);}
.profile-bio{
    background:#fff;border:1px solid #eef1f5;border-radius:10px;padding:44px 48px;margin:30px 0 0;
    box-shadow:0 4px 26px rgba(24,50,81,.06);}
.profile-bio>:first-child{margin-top:0;}
.profile-bio h2{border-top:0;padding-top:0;margin-top:32px;}
@media(max-width:767px){
    .profile-card{flex-direction:column;text-align:center;gap:26px;padding:26px 20px;margin-top:-40px;}
    /* the desktop max-width:44% would leave a sliver once stacked */
    .profile-photo{width:100%;max-width:300px;margin:0 auto;}
    .profile-photo img,.profile-photo .mig-noimg{height:340px;}
    .profile-name{font-size:25px;}
    .profile-name:after{margin-left:auto;margin-right:auto;}
    .profile-meta{justify-content:center;}
    .profile-bio{padding:26px 22px;}
}

/* ---------- short institutional pages ---------- */
.narrow-page .site-content{padding:52px 56px;}
.page-chips{margin:36px 0 0;text-align:center;}
.chips-label{
    display:block;font-size:12px;letter-spacing:2.6px;text-transform:uppercase;color:#a3b0c0;
    font-weight:600;margin-bottom:16px;}
.page-chip{
    display:inline-block;background:#fff;border:1px solid #eef1f5;border-radius:22px;padding:9px 20px;
    margin:0 6px 10px;font-size:14px;color:#5c6b7f;transition:.25s cubic-bezier(.2,.7,.3,1);
    box-shadow:0 3px 14px rgba(24,50,81,.05);}
.page-chip:hover{
    background:#183251;border-color:#183251;color:#fff;transform:translateY(-3px);
    box-shadow:0 10px 24px rgba(24,50,81,.2);}
@media(max-width:767px){.narrow-page .site-content{padding:26px 20px;}}

/* ---------- long article pages ---------- */
.sidebar-sticky{position:sticky;top:100px;}
.blog-single .site-content{padding:52px 56px;}
/* clipart and scanned pages dominate these documents; keep them in scale */
.migrate-content img{
    max-height:330px;width:auto;object-fit:contain;
    box-shadow:0 8px 30px rgba(24,50,81,.10);background:#fff;}
.migrate-content p>img,.migrate-content>img{margin:26px auto 30px;}
/* let genuine photographs (wide, not line art) run to the column width */
.migrate-content img[src*="scaled"],.migrate-content img[src*="1536x"],.migrate-content img[src*="2048x"]{
    max-height:460px;width:100%;object-fit:cover;}
.migrate-content h2{
    margin-top:52px;padding-top:34px;border-top:1px solid #eef1f5;}
.migrate-content>h2:first-child,.migrate-content>h1+h2{border-top:0;padding-top:0;margin-top:0;}
.migrate-content h2:first-of-type{border-top:0;padding-top:0;}
.migrate-content h3{margin-top:34px;}

/* "On this page" jump nav */
.widget-toc .toc-wrap{margin:0;padding:0;list-style:none;}
.widget-toc .toc-wrap li{position:relative;padding-left:14px;border-left:2px solid #eef1f5;}
.widget-toc .toc-wrap li.lv3{padding-left:26px;}
.widget-toc .toc-wrap li a{
    display:block;padding:8px 0;color:#8a8a8a;font-size:13.5px;line-height:1.45;transition:.2s;}
.widget-toc .toc-wrap li a:hover{color:#ff5f60;}
.widget-toc .toc-wrap li.active{border-left-color:#ff5f60;}
.widget-toc .toc-wrap li.active a{color:#183251;font-weight:500;}
html{scroll-behavior:smooth;}
[id]{scroll-margin-top:110px;}

/* ---------- responsive ---------- */
@media(max-width:1400px){
    #main-nav>ul.menu>li>a{font-size:13px;padding:0 8px;}
    .header-menu{max-width:calc(100% - 250px);}
}
@media(max-width:1199px){
    #logo img{max-height:44px;}
    #main-nav>ul.menu>li>a{font-size:12.5px;padding:0 7px;}
}
/* Edukin hands over to the burger only below 992px, so 992–1199 still has to
   fit the wordmark plus ten top-level items on one line. */
@media(min-width:992px) and (max-width:1199px){
    #logo img{max-height:34px;}
    .menu-bar #main-nav>ul>li{padding-top:20px;padding-bottom:20px;}
    #main-nav>ul.menu>li>a{font-size:12px;padding:0 5px;letter-spacing:-.2px;}
    #main-nav>ul.menu>li>a:before{left:5px;right:5px;}
    #main-nav>ul.menu>li.has-sub>a:after{margin-left:3px;font-size:9px;}
    .header-sticky #logo img{max-height:30px !important;}
    .top-utility li{margin-left:12px;}
    .top-utility li a{font-size:12px;}
    .top-bar .information li{font-size:12.5px;margin-right:16px;}
}
@media(max-width:991px){
    html,body{overflow-x:hidden;}
    .bg-header{padding-bottom:50px;}
    .breadcrumbs-blog{padding-top:40px;}
    .breadcrumbs-wrap .title{font-size:26px;line-height:34px;}
    .top-utility{display:none;}
    .top-bar .information{text-align:center;}
    .top-bar .information li{margin:0 10px;font-size:13px;}
    .blog-single .site-content{padding:30px 24px;}
    .blog-single .sidebar{margin-top:40px;}
    .fac-photo{float:none;width:100%;margin:0 0 22px;}
    .prog-columns .prog-col{margin-bottom:26px;}
    .profile-card{gap:32px;padding:32px 30px;}
    .profile-photo{width:300px;max-width:40%;}
    .profile-photo img,.profile-photo .mig-noimg{height:360px;}
    .profile-name{font-size:30px;}
    .profile-bio{padding:32px 28px;}
    .wide-page .wide-intro{margin-bottom:36px;}

    /* hand the nav back to Edukin's off-canvas menu */
    .menu-bar .menu-bar-wrap{padding:14px 15px;}
    .header-menu{max-width:100%;float:none;display:block;}
    .menu-bar #main-nav>ul>li,.menu-bar #mainnav-mobi>ul>li{padding-top:0;padding-bottom:0;}
    #main-nav>ul.menu,#mainnav-mobi>ul.menu{display:block !important;flex-wrap:nowrap;}
    #main-nav>ul.menu>li,#mainnav-mobi>ul.menu>li{display:block;width:100%;}
    #mainnav-mobi{background:#183251;width:100%;overflow-y:auto;max-height:calc(100vh - 90px);}
    #mainnav-mobi>ul.menu>li>a,#mainnav-mobi .sub-menu li a{
        display:block;padding:0 15px !important;height:48px;line-height:48px;font-size:14px;color:#fff !important;
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
    #mainnav-mobi ul.sub-menu{
        background:#0f2135;position:relative;left:auto;top:auto;min-width:0;width:100%;
        box-shadow:none;border-top:0;padding-left:0 !important;border-radius:0;}
    #mainnav-mobi ul li{border-top:1px solid rgba(255,255,255,.08);}
    #main-nav>ul.menu>li.has-sub>a:after,#mainnav-mobi li.has-sub>a:after,
    #mainnav-mobi .sub-menu li.has-sub>a:after{content:none !important;}
    #mainnav-mobi .btn-submenu{
        position:absolute;right:0;top:0;width:48px;height:48px;line-height:48px;text-align:center;cursor:pointer;}
    #mainnav-mobi .btn-submenu:after{
        content:"\\f107";font-family:FontAwesome;color:rgba(255,255,255,.7);font-size:15px;}
    #mainnav-mobi .btn-submenu.active:after{content:"\\f106";}
    .mobile-button{display:block;top:auto;right:15px;}
    .ajas-home-header .mobile-button:before,.ajas-home-header .mobile-button:after,
    .ajas-home-header .mobile-button span,
    .bg-header .mobile-button:before,.bg-header .mobile-button:after,
    .bg-header .mobile-button span{background:#fff;}

    /* stacked hero + sections */
    .flat-introduce .col-left,.flat-introduce .col-right{width:100%;float:none;}
    .flat-introduce .videobox{margin-bottom:36px;}
    .flat-introduce .videobox:before{display:none;}
    .flat-benefit.style1 .col-benefit-left,.flat-benefit.style1 .col-benefit-right{
        width:100%;float:none;padding-right:15px;}
    .flat-benefit.style1 .col-benefit-right{margin-top:40px;}
    .flat-event .col-left,.flat-event .col-right{width:100%;float:none;}
    .flat-event .col-right{margin-top:36px;}
    .partner-clients .iconbox-style1 .apply-admission{transform:none !important;margin-top:34px;}
    .ajas-programmes,.ajas-news,.ajas-success,.flat-services.style1,
    .quick-link.quick-link-style1,.flat-introduce-style1{padding:56px 0 !important;}
    .flat-title{font-size:28px !important;line-height:1.25 !important;}
    .container-fluid,.container{padding-left:15px;padding-right:15px;}
    .ajas-testimonials .wrap-quote{padding:52px 26px !important;}
    .ajas-testimonials .wrap-info{padding:44px 20px !important;}
    .ajas-testimonials .wrap-info ul li.avatar img{width:64px;height:64px;}
    .team-box-layout-h1 .item-img img{height:230px;}
    #bottom ul.bottom-nav{float:none;margin-top:14px;}
    #bottom ul.bottom-nav>li{margin:0 16px 0 0;}
}
@media(max-width:767px){
    .blog-single.content-blog{padding:50px 0 60px;}
    .blog-single .site-content{padding:26px 20px;}
    .migrate-content{font-size:15px;line-height:27px;}
    .migrate-content table{display:block;overflow-x:auto;}
    .migrate-content img{max-height:260px;}
    .sidebar-sticky{position:static;}
    /* the tile CTA is absolutely placed on desktop; let it flow here */
    .action-tile{flex-wrap:wrap;padding:22px 20px 18px;}
    .action-tile .tile-cta{position:static;display:block;width:100%;margin-top:12px;text-align:right;}
    .accred-row{gap:34px 30px;}
    .accred-row img{height:62px;}
    .flat-title.medium,.flat-title.larger,.flat-title.small{font-size:27px !important;}
    .ajas-testimonials .wrap-info ul.slides{gap:12px;}
}
/* Phone overrides live last on purpose: the 991px tablet block above also
   matches phone widths, so anything set there has to be re-stated here. */
@media(max-width:767px){
    .profile-card{flex-direction:column;text-align:center;gap:26px;padding:26px 20px;margin-top:-40px;}
    .profile-photo{width:100% !important;max-width:300px !important;margin:0 auto;}
    .profile-photo img,.profile-photo .mig-noimg{height:340px !important;}
    .profile-name{font-size:25px !important;}
    .profile-name:after{margin-left:auto;margin-right:auto;}
    .profile-meta{justify-content:center;}
    .profile-bio{padding:26px 20px !important;}
}
@media(max-width:575px){
    /* keep the wordmark clear of the hamburger — the SVG is very wide, so
       cap the width, not just the height */
    #logo,.menu-bar #logo{max-width:calc(100% - 54px);}
    #logo img,.header-sticky #logo img{max-height:30px !important;max-width:100% !important;height:auto;}
    .menu-bar .menu-bar-wrap{padding:12px 52px 12px 15px;}
    .top-bar .information li{display:block;margin:2px 0;}
    /* the floated date badge leaves too little room for a long single-word
       headline at this width — stack it instead */
    .post-blog .post-meta{float:none;margin:0 0 16px;}
    .post-blog .clendar-wrap{margin-top:-46px;}
    .post-blog .entry-title{overflow-wrap:anywhere;}
    .action-tile .tile-title,.pc-name,.profile-name{overflow-wrap:anywhere;}
}
'''
ONLY=sys.argv[1:] or None   # optional: build only these slugs (for testing)
os.chdir(SRC)

def clean_title(t):
    return html.unescape(t or '').replace(' | Al Jamia  Arts &amp;  Science College','').replace(' | Al Jamia  Arts &  Science College','').replace(' | Al Jamia Arts & Science College','').strip()
def prefix(newpath): return '../'*newpath.count('/')

# ---------------- href resolution ----------------
# Old slugs that were not built as their own page (duplicates), and where
# incoming links should land instead.
REDIRECTS={'graduation-ceremony-2026':'college-news/graduation-ceremony-2026',
           'faculties/x':'faculties'}
def resolve_href(href):
    href=(href or '').strip()
    if href.lower().startswith(('mailto:','tel:','javascript:')): return ('ext',href)
    # a few old links have a URL pasted inside another; keep the inner one and
    # cut whatever trails past its file extension
    if href.count('https://')>1:
        href='https://'+href.rsplit('https://',1)[1]
        m=re.match(r'(.*?\.(?:pdf|jpe?g|png|webp|docx?|xlsx?|pptx?))',href,re.I)
        if m: href=m.group(1)
    if href.startswith('http') and 'ajascollege' not in href: return ('ext',href)
    if href.startswith('https://ajascollege.ac.in/'): href=href[len('https://ajascollege.ac.in/'):]
    if href.startswith('http://ajascollege.ac.in/'): href=href[len('http://ajascollege.ac.in/'):]
    if 'wp-content/uploads/' in href:
        return ('asset','assets/uploads/'+href.split('wp-content/uploads/',1)[1])
    # the mirror stores links relative to the source page's own depth; our
    # output re-anchors everything from the site root, so drop the ../ walk-up
    href=re.sub(r'^(?:\.\./)+','',href)
    if href in ('index.html','index.html#','#','','./'): return ('int','')
    # JetEngine download endpoints — real PDFs saved under that query-string name
    m=re.match(r'index\.html@jet_download=([0-9a-f]+)',href)
    if m: return ('asset','assets/downloads/'+m.group(1)+'.pdf')
    m=re.match(r'index\.html@p=(\d+)\.html(#.*)?$',href)
    if m:
        sl=id2slug.get(m.group(1)); frag=m.group(2) or ''
        if not sl or sl=='.': return ('int','')
        return ('int',REDIRECTS.get(sl,sl)+'/'+frag)
    m=re.match(r'([\w\-/]+)/index\.html(#.*)?$',href)
    if m: return ('int',REDIRECTS.get(m.group(1),m.group(1))+'/'+(m.group(2) or ''))
    if href.startswith('index.html#'): return ('int','')
    return ('int',href)
def linkify(kind,val):
    if kind=='ext': return val
    if kind=='asset': return '%%P%%'+val
    if val=='' : return '%%P%%index.html'
    return '%%P%%'+val

# ---------------- nav from old menus ----------------
home=open('index.html',encoding='utf-8',errors='ignore').read()
def extract_menu(mid):
    start=home.find(f'<ul id="{mid}"'); depth=0;i=start;end=None
    while i<len(home):
        if home.startswith('<ul',i): depth+=1
        elif home.startswith('</ul>',i):
            depth-=1
            if depth==0: end=i+5;break
        i+=1
    return home[start:end]
def menu_to_ul(block):
    toks=re.finditer(r'(<ul\b[^>]*>)|(</ul>)|(<li\b[^>]*>)|(</li>)|(<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>)',block,re.S)
    res=[];first=True
    for m in toks:
        if m.group(1): res.append('<ul class="menu">' if first else '<ul class="sub-menu">'); first=False
        elif m.group(2): res.append('</ul>')
        elif m.group(3): res.append('<li>')
        elif m.group(4): res.append('</li>')
        else:
            kind,val=resolve_href(m.group(6)); href=linkify(kind,val)
            txt=html.unescape(re.sub('<[^>]+>','',m.group(7))).strip()
            tgt=' target="_blank"' if kind in('ext','asset') else ''
            res.append(f'<a href="{href}"{tgt}>{html.escape(txt)}</a>')
    return mark_has_sub(''.join(res))

def mark_has_sub(menu):
    """Tag every <li> that owns a nested <ul> so CSS can draw carets / flyouts."""
    toks=list(re.finditer(r'<li>|</li>|<ul[^>]*>|</ul>',menu))
    parent=[]           # stack of indices into toks for open <li>
    owns=set()
    for i,m in enumerate(toks):
        t=m.group(0)
        if t=='<li>': parent.append(i)
        elif t=='</li>':
            if parent: parent.pop()
        elif t.startswith('<ul') and parent: owns.add(parent[-1])
    out=[];last=0
    for i,m in enumerate(toks):
        if i in owns:
            out.append(menu[last:m.start()]); out.append('<li class="menu-item has-sub">')
            last=m.end()
    out.append(menu[last:])
    return ''.join(out)

MAIN_MENU=menu_to_ul(extract_menu('menu-1-c029303'))
def flat_links(block):
    # only TOP-LEVEL <li> anchors of the utility menu (skip nested sub-items)
    items=[];depth=0
    for m in re.finditer(r'(<ul\b[^>]*>)|(</ul>)|(<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>)',block,re.S):
        if m.group(1): depth+=1
        elif m.group(2): depth-=1
        elif depth==1:  # first ul only
            txt=html.unescape(re.sub('<[^>]+>','',m.group(5))).strip()
            if not txt: continue
            kind,val=resolve_href(m.group(4))
            if kind=='int' and val=='': continue
            items.append((txt,linkify(kind,val),' target="_blank"' if kind in('ext','asset') else ''))
    return items
TOP_LINKS=flat_links(extract_menu('menu-1-e4047ae'))
TOPBAR=' '.join(f'<li><a href="{h}"{t}>{html.escape(x)}</a></li>' for x,h,t in TOP_LINKS[:8])

# ---------------- content extractor ----------------
ALLOWED={'h1','h2','h3','h4','h5','h6','p','ul','ol','li','table','thead','tbody','tr','td','th',
         'a','img','strong','b','em','br','blockquote','figure','figcaption','hr','iframe','sup','sub'}
BLOCK_DROP={'script','style','noscript','svg','button','form','input','select','option','textarea','nav','header','footer'}
class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out=[]; self.skip=0; self.imgs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in BLOCK_DROP: self.skip+=1; return
        if self.skip: return
        if tag=='i': return  # font icons
        if tag=='img':
            src=a.get('data-src') or a.get('data-lazy-src') or a.get('data-large_image') or a.get('src','')
            if src.startswith('data:'):
                # try srcset last entry
                ss=a.get('data-srcset') or a.get('srcset') or ''
                cand=[p.strip().split(' ')[0] for p in ss.split(',') if 'uploads' in p]
                src=cand[-1] if cand else src
            alt=a.get('alt','') or ''
            if src.startswith('data:'): return  # still a placeholder, skip
            kind,val=resolve_href(src)
            if kind=='asset':
                self.imgs.append(val); self.out.append(f'<img src="%%P%%{val}" alt="{html.escape(alt)}" class="img-fluid">')
            elif kind=='ext': self.out.append(f'<img src="{src}" alt="{html.escape(alt)}" class="img-fluid">')
            return
        if tag=='a':
            kind,val=resolve_href(a.get('href','#')) if ('href' in a) else ('int','')
            if 'href' not in a or a['href'].strip() in ('','#') or (kind=='int' and re.search(r'(?:^|/)(?:20\d\d/\d\d|author/|category/|tag/|comment|feed)',val)):
                self.dead_a=getattr(self,'dead_a',0)+1; self.out.append('<span>'); return
            href=linkify(kind,val)
            tgt=' target="_blank"' if kind in('ext','asset') else ''
            self.out.append(f'<a href="{href}"{tgt}>'); return
        if tag=='iframe':
            isrc=a.get('data-src') or a.get('data-lazy-src') or a.get('src','')
            if not isrc or isrc.startswith('data:'): return  # lazy placeholder, drop
            self.out.append(f'<div class="embed-wrap"><iframe src="{isrc}" loading="lazy"></iframe></div>'); return
        if tag in ALLOWED: self.out.append(f'<{tag}>')
    def handle_endtag(self,tag):
        if tag in BLOCK_DROP:
            if self.skip: self.skip-=1
            return
        if self.skip: return
        if tag=='i': return
        if tag in('img','iframe'): return
        if tag=='a':
            if getattr(self,'dead_a',0)>0: self.dead_a-=1; self.out.append('</span>')
            else: self.out.append('</a>')
            return
        if tag in ALLOWED: self.out.append(f'</{tag}>')
    def handle_data(self,d):
        if self.skip: return
        if d.strip(): self.out.append(html.escape(d))
        elif d and self.out and not self.out[-1].endswith('>'): self.out.append(' ')

def balanced(s,startpat):
    i=s.find(startpat)
    if i<0: return None
    # find the opening <div ... > that carries startpat
    lt=s.rfind('<div',0,i+len(startpat))
    depth=0;j=lt
    while j<len(s):
        if s.startswith('<div',j): depth+=1
        elif s.startswith('</div>',j):
            depth-=1
            if depth==0: return s[lt:j+6]
        j+=1
    return None

def extract_content(fp):
    s=open(fp,encoding='utf-8',errors='ignore').read()
    block=balanced(s,'data-elementor-type="wp-page"') or balanced(s,'data-elementor-type="single-post"')
    if not block:
        mm=re.search(r'<main\b[^>]*>(.*?)</main>',strip_chrome(s),re.S)
        block=mm.group(1) if mm else strip_chrome(s)
    p=Extract(); p.feed(block)
    htmlout=''.join(p.out)
    htmlout=wrap_orphans(htmlout)
    for _ in range(3):
        htmlout=re.sub(r'<(p|h[1-6]|li|ul|ol|strong|b|em|a|span)>\s*</\1>','',htmlout)
    htmlout=re.sub(r'<span>|</span>','',htmlout)
    htmlout=htmlout.replace('View Detailed Profile','').replace('Read More','')
    htmlout=re.sub(r'[ \t]{2,}',' ',htmlout)
    htmlout=re.sub(r'(</(?:p|h[1-6]|ul|ol|table|blockquote|figure)>)','\\1\n',htmlout)
    htmlout=re.sub(r'<p>\s*Skip to content\s*</p>','',htmlout)
    htmlout=re.sub(r'<p>[^<]*\| Al Jamia Arts &amp; Science College[^<]*</p>','',htmlout)
    return htmlout.strip(), p.imgs, block

BLOCKRE=re.compile(r'<h([1-6])>(.*?)</h\1>|<p>(.*?)</p>|<(ul|ol|table|blockquote|figure)\b.*?</\4>|<div class="(?:embed-wrap|fac-photo|mig-map)[^"]*">.*?</div>|<img[^>]*>',re.S)
def _plain(h): return html.unescape(re.sub(r'\s+',' ',re.sub('<[^>]+>','',h)).strip())
def structure_content(content):
    """Turn Elementor heading-soup into real structure: role/-/name runs -> Edukin tables; drop empty '-' headings; keep prose sections."""
    toks=[]
    for m in BLOCKRE.finditer(content):
        s=m.group(0)
        if m.group(1):  # heading
            txt=_plain(m.group(2))
            if txt in ('','-','–','—','_'): continue  # drop separator/empty headings
            toks.append(('h',int(m.group(1)),txt,s))
        else:
            toks.append(('x',0,'',s))
    out=[];buf=[]
    def flush():
        if not buf: return
        # buf = consecutive heading tokens
        if len(buf)>=4:  # roster: pair (label,value)
            rows=''
            i=0
            while i+1<len(buf):
                rows+=f'<tr><td class="rl">{html.escape(buf[i][2])}</td><td class="nm">{html.escape(buf[i+1][2])}</td></tr>'
                i+=2
            out.append(f'<table class="mig-roster"><tbody>{rows}</tbody></table>')
            if i<len(buf): out.append(f'<p class="mig-lead">{html.escape(buf[i][2])}</p>')
        else:
            for b in buf: out.append(b[3])
        buf.clear()
    for t in toks:
        if t[0]=='h': buf.append(t)
        else: flush(); out.append(t[3])
    flush()
    return '\n'.join(out)

PROG_ROW=re.compile(
    r'<table class="mig-roster"><tbody>'
    r'<tr><td class="rl">(?P<name>[^<]+)</td><td class="nm">(?P<dur>[^<]*)</td></tr>'
    r'<tr><td class="rl">\s*Fee\s*:?\s*</td><td class="nm">(?P<fee>[^<]*)</td></tr>'
    r'<tr><td class="rl">\s*Intake\s*:?\s*</td><td class="nm">(?P<intake>[^<]*)</td></tr>'
    r'</tbody></table>', re.I)

def structure_programmes(content):
    """The admission page is a dozen identical {photo, fee table, eligibility}
    blocks stacked vertically — several screens of scrolling for a table's
    worth of facts. Fold each one into a card and lay them out in a grid."""
    tables=list(PROG_ROW.finditer(content))
    if len(tables)<3: return content
    cards=[]
    for i,m in enumerate(tables):
        tail=content[m.end(): tables[i+1].start() if i+1<len(tables) else len(content)]
        # the notes after a table are label/value paragraph pairs
        notes=[]
        for lm in re.finditer(r'<p class="mig-lead">([^<]+)</p>\s*<p>(.*?)</p>',tail,re.S):
            label=lm.group(1).strip().rstrip(':')
            body=re.sub(r'<img[^>]*>','',lm.group(2))
            body=re.sub(r'\s+',' ',re.sub('<[^>]+>','',body)).strip()
            if body: notes.append((label,body))
        if not notes:
            for hm in re.finditer(r'<h2[^>]*>([^<]+)</h2>\s*<p>(.*?)</p>',tail,re.S):
                body=re.sub(r'\s+',' ',re.sub('<[^>]+>','',re.sub(r'<img[^>]*>','',hm.group(2)))).strip()
                if body: notes.append((hm.group(1).strip(),body))
        meta=''.join(f'<li><span class="pm-k">{k}</span><span class="pm-v">{html.escape(v)}</span></li>'
                     for k,v in [('Duration',m.group('dur').strip()),
                                 ('Fee',m.group('fee').strip()),
                                 ('Intake',m.group('intake').strip())] if v)
        nh=''.join(f'<div class="pc-note"><strong>{html.escape(l)}</strong> {html.escape(b)}</div>'
                   for l,b in notes[:2])
        cards.append(f'''<div class="col-lg-6 col-md-6 col-sm-12"><div class="prog-card">
<h3 class="pc-name">{html.escape(m.group('name').strip())}</h3>
<ul class="pc-meta">{meta}</ul>
{nh}
</div></div>''')
    grid=f'<div class="row prog-cards">{"".join(cards)}</div>'
    # replace the whole run (first table through end of the last block) with the grid,
    # keeping any prose that came before it
    start=tables[0].start()
    lead_img=re.search(r'(<img[^>]*>)\s*$',content[:start])
    if lead_img: start=lead_img.start(1)
    return content[:start]+grid

def structure_downloads(content):
    """Convert <p> blobs holding many 'label <a>View</a>' pairs into a clean download table."""
    def repl(m):
        inner=m.group(1)
        links=list(re.finditer(r'<a\b[^>]*href="([^"]*)"[^>]*>(.*?)</a>',inner,re.S))
        if len(links)<2: return m.group(0)
        rows='';last=0
        for lk in links:
            label=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',inner[last:lk.start()]))).strip(' -–—:')
            href=lk.group(1)
            rows+=f'<tr><td class="dl-name">{html.escape(label) if label else "Document"}</td><td class="dl-act"><a href="{href}" target="_blank" class="dl-btn"><i class="fa fa-download"></i> View</a></td></tr>'
            last=lk.end()
        return f'<table class="mig-downloads"><tbody>{rows}</tbody></table>'
    return re.sub(r'<p>(.*?)</p>',repl,content,flags=re.S)

def first_para(content):
    m=re.search(r'<p>(.*?)</p>',content,re.S)
    if not m: return ''
    t=re.sub('<[^>]+>','',m.group(1)); return re.sub(r'\s+',' ',html.unescape(t)).strip()
def first_img(content):
    for m in re.finditer(r'<img src="%%P%%(assets/uploads/[^"]+)"',content):
        u=m.group(1)
        if not u.lower().endswith('.svg') and not CHROME.search(u): return u
    return None

CHROME=re.compile(r'(AICTE|ISO-Logo|UGC-Logo|University-Logo|Naac|KERALA|cropped-Frame|Group-1000|AJAS-Website-Heading|/logo|Logo-|-Logo|favicon|placeholder|Frame-100|Frame-300)',re.I)
def pick_photo(raw_container):
    urls=re.findall(r'wp-content/uploads/([0-9]{4}/[0-9]{2}/[^ "\'<>()]+\.(?:jpe?g|png|webp))',raw_container)
    for u in urls:
        if not CHROME.search(u): return 'assets/uploads/'+u
    return None

def strip_chrome(s):
    # remove balanced header and footer elementor blocks so only page body remains
    for marker in ('data-elementor-type="header"','data-elementor-type="footer"'):
        i=s.find(marker)
        if i<0: continue
        lt=s.rfind('<div',0,i); depth=0;j=lt;end=None
        while j<len(s):
            if s.startswith('<div',j): depth+=1
            elif s.startswith('</div>',j):
                depth-=1
                if depth==0: end=j+6;break
            j+=1
        if end: s=s[:lt]+s[end:]
    return s

JET=re.compile(
    r'(?P<img><div class="jet-listing jet-listing-dynamic-image".*?</div>)'
    r'|(?P<fld><div class="jet-listing-dynamic-field__content"[^>]*>(?P<t>.*?)</div>)', re.S)

def extract_loop_items(fp):
    """Some pages (careers) are Elementor *archive* templates rather than
    wp-page/single-post, so the normal content extractor finds nothing and
    falls through to page chrome. Read the loop items directly."""
    s=open(fp,encoding='utf-8',errors='ignore').read()
    out=[]
    for m in re.finditer(r'data-elementor-type="loop-item"(.*?)(?=data-elementor-type="|$)',s,re.S):
        seg=m.group(1); rec={}
        for w in re.finditer(r'data-widget_type="([^"]+)".*?<div class="elementor-widget-container">(.*?)</div>',seg,re.S):
            kind=w.group(1).split('.')[0]
            txt=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>',' ',w.group(2)))).strip()
            if not txt: continue
            if kind=='theme-post-title' and 'title' not in rec: rec['title']=txt
            elif kind=='theme-post-excerpt' and 'body' not in rec: rec['body']=txt
        if rec.get('title'): out.append(rec)
    return out

def extract_people(fp):
    """Staff rosters were built with JetEngine listings — photo, then name,
    then role, per person. The generic extractor flattens that into one
    paragraph of images and loose text; read the listing structure instead."""
    s=open(fp,encoding='utf-8',errors='ignore').read()
    toks=[]
    for m in JET.finditer(s):
        if m.group('img'):
            u=(re.search(r'data-src="([^"]*wp-content/uploads/[^"]+)"',m.group('img'))
               or re.search(r'src="([^"]*wp-content/uploads/[^"]+)"',m.group('img')))
            toks.append(('img',u.group(1).split('wp-content/uploads/')[-1] if u else None))
        else:
            t=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',m.group('t')))).strip()
            if t: toks.append(('txt',t))
    people=[]; cur=None
    for kind,val in toks:
        if kind=='img':
            if cur: people.append(cur)
            cur={'photo':val,'lines':[]}
        elif cur is not None:
            cur['lines'].append(val)
    if cur: people.append(cur)
    out=[]
    for p in people:
        if not p['lines']: continue
        photo=('assets/uploads/'+p['photo']) if p['photo'] else None
        if photo and not os.path.exists(os.path.join(OUT,photo)): photo=None
        out.append((photo,p['lines'][0],' · '.join(p['lines'][1:3])))
    return out

def people_grid(people,P):
    cards=''
    for photo,name,role in people:
        pic=(f'<div class="pg-photo"><img src="{P}{photo}" alt="{html.escape(name)}"></div>'
             if photo else '<div class="pg-photo"><div class="mig-noimg"></div></div>')
        cards+=f'''<div class="col-lg-3 col-md-4 col-sm-6 col-6"><div class="people-card">
{pic}
<div class="pg-body"><h3 class="pg-name">{html.escape(name)}</h3>
{f'<p class="pg-role">{html.escape(role)}</p>' if role else ''}</div>
</div></div>'''
    return f'<div class="row people-grid">{cards}</div>'

def collect_all_images(fp):
    s=strip_chrome(open(fp,encoding='utf-8',errors='ignore').read())
    urls=re.findall(r'wp-content/uploads/([0-9]{4}/[0-9]{2}/[^ "\'<>()]+?\.(?:jpe?g|png|webp))',s)
    out=[]
    for u in urls:
        if CHROME.search(u): continue
        a='assets/uploads/'+u
        if a not in out: out.append(a)
    return out

INLINE_BLOCKS=('p','h1','h2','h3','h4','h5','h6','li','td','th','blockquote','figcaption')
def wrap_orphans(hout):
    # wrap loose text/inline (img,a,span,strong,em,br) that sits outside any block element in <p>
    tokens=re.split(r'(<[^>]+>)',hout)
    depth=0; res=[]; buf=[]
    def flush():
        if buf:
            seg=''.join(buf).strip()
            if seg and re.sub(r'<[^>]+>','',seg).strip(): res.append('<p>'+seg+'</p>')
            elif seg: res.append(seg)
            buf.clear()
    for tk in tokens:
        if not tk: continue
        m=re.match(r'</?([a-zA-Z0-9]+)',tk)
        if tk.startswith('<') and m:
            tag=m.group(1).lower()
            if tag in INLINE_BLOCKS or tag in ('ul','ol','table','thead','tbody','tr','figure','div','iframe','hr'):
                if tk.startswith('</'):
                    depth=max(0,depth-1); res.append(tk)
                elif tk.endswith('/>') or tag=='hr' or tag=='br':
                    (res if depth>0 else buf).append(tk)
                else:
                    flush(); depth+=1; res.append(tk)
            else:
                (res if depth>0 else buf).append(tk)
        else:
            (res if depth>0 else buf).append(tk)
    flush()
    return ''.join(res)
# ---------------- shell ----------------
PHONE='+91 7994 188918'
EMAIL='mail@ajascollege.ac.in'
ADDRESS='Poopalam, Valambur (P.O), Perinthalmanna, Malappuram Dt, Kerala — 679325'
LOGO='assets/uploads/2024/01/AJAS-Website-Heading-Last.svg'
BANNER='assets/uploads/2024/01/P1222323-building-2048x1154-1.webp'

def head_block(title, P, desc='', extra_css=''):
    css=P+'stylesheet/'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)} | {SITE}</title>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="description" content="{html.escape(desc or SITE+', Perinthalmanna — affiliated to the University of Calicut.')}">
<link rel="stylesheet" href="{css}bootstrap.css">
<link rel="stylesheet" href="{css}font-awesome.css">
<link rel="stylesheet" href="{css}themify-icons.css">
<link rel="stylesheet" href="{css}animate.css">
<link rel="stylesheet" href="{css}style.css">
<link rel="stylesheet" href="{css}shortcodes.css">
<link rel="stylesheet" href="{css}jquery-fancybox.css">
<link rel="stylesheet" href="{css}responsive.css">
<link rel="stylesheet" href="{css}flexslider.css">
<link rel="stylesheet" href="{css}owl.theme.default.min.css">
<link rel="stylesheet" href="{css}owl.carousel.min.css">
<link rel="stylesheet" href="{css}jquery.mCustomScrollbar.min.css">
{extra_css}<link rel="stylesheet" href="{P}assets/migrate.css">
<link href="{P}icon/favicon.ico" rel="shortcut icon">
</head>
<body>
<div id="loading-overlay"><div class="loader"></div></div>'''

def topbar_block():
    return f'''<div class="top-bar clearfix">
<div class="container"><div class="row">
<div class="col-lg-5 col-md-6 col-sm-12">
<ul class="information">
<li class="phone lt-sp003"><i class="fa fa-phone" aria-hidden="true"></i> <a href="tel:+917994188918">{PHONE}</a></li>
<li class="email"><i class="fa fa-envelope" aria-hidden="true"></i> <a href="mailto:{EMAIL}">{EMAIL}</a></li>
</ul>
</div>
<div class="col-lg-7 col-md-6 col-sm-12"><ul class="nav-sing top-utility">{TOPBAR}</ul></div>
</div></div>
</div>'''

def navbar_block(P):
    return f'''<header class="header header-blog menu-bar hv-menu-type2">
<div class="container"><div class="menu-bar-wrap clearfix">
<div id="logo" class="logo"><a href="{P}index.html"><img src="{P}{LOGO}" alt="{html.escape(SITE)}"></a></div>
<div class="mobile-button"><span></span></div>
<div class="header-menu"><nav id="main-nav" class="main-nav">{MAIN_MENU}</nav></div>
</div></div>
</header>'''

def footer_block(P):
    # Accreditation marks repeated site-wide — these are the credentials a
    # prospective student and their family actually check for.
    marks=''.join(f'<li><img src="{P}{u}" alt="{html.escape(n)}"><span>{html.escape(n)}</span></li>'
                  for u,n in PARTNERS)
    return f'''<footer id="footer" class="footer-type1">
<div class="footer-trust"><div class="container">
<p class="trust-line">Affiliated to the University of Calicut &middot; Recognised under UGC 2(f)
&middot; Government of Kerala &amp; AICTE &middot; Established 2010</p>
<ul class="trust-marks">{marks}</ul>
</div></div>
<div id="footer-widget"><div class="container"><div class="row">
<div class="col-lg-4 col-md-6 col-footer">
<div class="logo-footer"><span class="footer-brand-text">Al Jamia<span>Arts &amp; Science College</span></span></div>
<ul class="footer-address">
<li><i class="fa fa-map-marker" aria-hidden="true"></i> {html.escape(ADDRESS)}</li>
<li><i class="fa fa-envelope" aria-hidden="true"></i> <a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li><i class="fa fa-phone" aria-hidden="true"></i> <a href="tel:+917994188918">{PHONE}</a></li>
</ul>
</div>
<div class="col-lg-2 col-md-6 col-company">
<h3 class="widget widget-title">College</h3>
<ul class="widget-nav-menu">
<li><a href="{P}overview/">Overview</a></li>
<li><a href="{P}vision-mission/">Vision &amp; Mission</a></li>
<li><a href="{P}principal/">Principal</a></li>
<li><a href="{P}recognitions/">Recognitions</a></li>
<li><a href="{P}contact/">Contact Us</a></li>
</ul>
</div>
<div class="col-lg-2 col-md-6 col-link">
<h3 class="widget widget-title">Academics</h3>
<ul class="widget-nav-menu">
<li><a href="{P}departments/">Departments</a></li>
<li><a href="{P}programe-offered/">Programmes</a></li>
<li><a href="{P}faculties/">Faculties</a></li>
<li><a href="{P}examinations/">Examinations</a></li>
<li><a href="{P}library/">Library</a></li>
</ul>
</div>
<div class="col-lg-2 col-md-6 col-course">
<h3 class="widget widget-title">Students</h3>
<ul class="widget-nav-menu">
<li><a href="{P}admission/">Admission</a></li>
<li><a href="{P}scholorship/">Scholarships</a></li>
<li><a href="{P}placement-cell/">Placement Cell</a></li>
<li><a href="{P}alumnae/">Alumni</a></li>
<li><a href="{P}register-a-complaint/">Grievance</a></li>
</ul>
</div>
<div class="col-lg-2 col-md-6 col-media">
<h3 class="widget widget-title">Follow Us</h3>
<ul class="widget-social-media">
<li><a href="https://www.facebook.com/ajascollege" target="_blank" rel="noopener"><i class="fa fa-facebook" aria-hidden="true"></i></a></li>
<li><a href="https://www.instagram.com/ajascollege" target="_blank" rel="noopener"><i class="fa fa-instagram" aria-hidden="true"></i></a></li>
<li><a href="https://www.linkedin.com/school/ajascollege" target="_blank" rel="noopener"><i class="fa fa-linkedin" aria-hidden="true"></i></a></li>
<li><a href="https://www.youtube.com/@ajascollege" target="_blank" rel="noopener"><i class="fa fa-youtube-play" aria-hidden="true"></i></a></li>
</ul>
</div>
</div></div></div>
<div id="bottom" class="bottom-type1 clearfix has-spacer">
<div id="bottom-bar-inner" class="container"><div class="bottom-bar-inner-wrap">
<div class="bottom-bar-content"><div id="copyright">
&copy; <span class="text-year">2026</span> <span class="text-name">{html.escape(SITE)}.</span>
<span class="license"><a href="{P}index.html">All Rights Reserved</a></span>
</div></div>
<div class="bottom-bar-menu"><ul class="bottom-nav">
<li class="menu-item"><a href="{P}overview/">About</a></li>
<li class="menu-item"><a href="{P}iqac/">IQAC</a></li>
<li class="menu-item"><a href="{P}policy-documents/">Policies</a></li>
<li class="menu-item"><a href="{P}career/">Careers</a></li>
<li class="menu-item"><a href="{P}contact/">Contact</a></li>
</ul></div>
</div></div>
</div>
<a id="scroll-top" class="show"></a>
</footer>'''

def scripts_block(P):
    js=P+'javascript/'
    s=f'''<script src="{js}jquery.min.js"></script>
<script src="{js}plugins.js"></script>
<script src="{js}jquery-countTo.js"></script>
<script src="{js}jquery-ui.js"></script>
<script src="{js}jquery-fancybox.js"></script>
<script src="{js}flex-slider.min.js"></script>
<script src="{js}scroll-img.js"></script>
<script src="{js}owl.carousel.min.js"></script>
<script src="{js}jquery.mCustomScrollbar.concat.min.js"></script>
<script src="{js}parallax.js"></script>
<script src="{js}jquery-isotope.js"></script>
<script src="{js}equalize.min.js"></script>
<script src="{js}main.js"></script>'''
    # progressive scroll-reveal + active-section tracking for the jump nav.
    # No library: IntersectionObserver only, and it degrades to "everything
    # visible" if the browser or the user's motion settings say no.
    s+='''
<script>
(function(){
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!('IntersectionObserver' in window) || reduce) { document.documentElement.classList.add('no-reveal'); }
  else {
    document.documentElement.classList.add('has-reveal');
    // [selector, motion variant] — variants are defined in migrate.css
    var groups = [
      ['.title-section, .listing-intro, .accred-label',            'up'],
      ['.action-tile',                                             'up'],
      ['.accred-row li',                                           'fade'],
      ['.videobox, .profile-photo',                                'left'],
      ['.content-introduce, .profile-head',                        'right'],
      ['.prog-columns > div, .prog-cards > div',                   'up'],
      ['.flat-courses .course, .team-box-layout-h1, .post-blog',   'up'],
      ['.flat-imagebox, .iconbox-benefit .iconbox',                'up'],
      ['.content-event',                                           'left'],
      ['.images-list .img-event',                                  'zoom'],
      ['.ajas-success .textbox-about',                             'left'],
      ['.iconbox-about .iconbox',                                  'zoom'],
      ['.wrap-link-left',                                          'left'],
      ['.wrap-link-right, .info-quick-link li',                    'right'],
      ['.mig-clubs > div, .gal-item, .page-chip',                  'up'],
      ['.people-card',                                             'up'],
      ['.site-content, .profile-card, .profile-bio',               'up'],
      ['.sidebar .widget',                                         'right']
      // the footer deliberately does not animate — it is chrome, not content
    ];
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if (e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, {rootMargin:'0px 0px -7% 0px', threshold:0.05});
    var seen = new WeakSet();
    groups.forEach(function(g){
      var i = 0;
      document.querySelectorAll(g[0]).forEach(function(el){
        if (seen.has(el)) return;
        seen.add(el);
        el.classList.add('reveal', 'rv-' + g[1]);
        el.style.transitionDelay = ((i++ % 4) * 80) + 'ms';
        io.observe(el);
      });
    });
    // counters restart cleanly when their tile animates in
    var nums = document.querySelectorAll('.numb-count');
    if (nums.length && window.jQuery && jQuery.fn.countTo){
      var cio = new IntersectionObserver(function(es){
        es.forEach(function(e){
          if (!e.isIntersecting) return;
          cio.unobserve(e.target);
          jQuery(e.target).countTo({
            from: 0, to: parseInt(e.target.getAttribute('data-to'), 10) || 0,
            speed: 1800, refreshInterval: 40
          });
        });
      }, {threshold:0.5});
      nums.forEach(function(n){ cio.observe(n); });
    }
  }
  // On the home page the sticky bar engages ~130px down, which is exactly
  // where the hero headline still is — so it clipped the kicker. Hold the
  // sticky state back until the hero has genuinely scrolled away.
  // The theme adds .header-sticky ~130px down — right where the hero kicker
  // still is, so the bar clipped it. Removing the class here loses a race with
  // the theme's own scroll handler, so flag it on <body> and let CSS neutralise
  // the sticky state instead. Class order can't matter to CSS.
  var hero = document.querySelector('.ajas-hero');
  var wrap = document.querySelector('.wrap-header');
  if (hero){
    var gate = function(){
      // Revolution absolutely positions its wrapper, so the section's own rect
      // reports top 0; add the header block explicitly instead.
      var head = wrap ? wrap.offsetHeight : 0;
      var release = head + hero.getBoundingClientRect().height - 80;
      document.body.classList.toggle('hero-hold', window.pageYOffset < release);
    };
    window.addEventListener('scroll', gate, {passive:true});
    window.addEventListener('resize', gate);
    window.addEventListener('load', gate);
    gate();
  }

  // highlight the current section in the "On this page" nav
  var links = document.querySelectorAll('.widget-toc a');
  if (links.length){
    var targets = [];
    links.forEach(function(a){
      var t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
      if (t) targets.push({a:a, t:t});
    });
    var onScroll = function(){
      var y = window.pageYOffset + 140, cur = null;
      targets.forEach(function(o){ if (o.t.offsetTop <= y) cur = o; });
      links.forEach(function(a){ a.parentNode.classList.remove('active'); });
      if (cur) cur.a.parentNode.classList.add('active');
    };
    window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
    links.forEach(function(a){
      a.addEventListener('click', function(e){
        var t = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
        if (!t) return;
        e.preventDefault();
        window.scrollTo({top: t.offsetTop - 110, behavior: reduce ? 'auto' : 'smooth'});
      });
    });
  }
})();
</script>'''
    return s

def shell(title, crumbs, content, newpath, bodyextra=''):
    """Standard interior page: Edukin blog chrome (banner + breadcrumbs) + content."""
    P=prefix(newpath)
    crumb_html=''.join(f'<li><a href="%%P%%{h}">{html.escape(t)}</a></li>' for t,h in crumbs[:-1])
    crumb_html+=f'<li class="active">{html.escape(crumbs[-1][0])}</li>'
    page=(head_block(title,P)+f'''
<div class="bg-header">
<div class="flat-header-blog">
{topbar_block()}
{navbar_block(P)}
<div class="page-title page-title-blog"><div class="page-title-inner">
<div class="breadcrumbs breadcrumbs-blog text-left"><div class="container"><div class="breadcrumbs-wrap">
<ul class="breadcrumbs-inner">{crumb_html}</ul>
<div class="title">{html.escape(title)}</div>
</div></div></div>
</div></div>
</div>
</div><!-- bg-header -->
{content}
'''+footer_block(P)+'\n'+scripts_block(P)+'\n'+bodyextra+'\n</body>\n</html>')
    return page.replace('%%P%%',P)

def home_shell(content, desc):
    """Home: solid header in flow (Edukin home2 pattern) + static hero below.
    Revolution Slider is deliberately not loaded — the hero is plain markup."""
    P=''
    page=(head_block('Home',P,desc)+f'''
<div class="wrap-header">
<div class="flat-header flat-header-style2 ajas-home-header">
{topbar_block()}
{navbar_block(P)}
</div>
</div><!-- wrap-header -->
{content}
'''+footer_block(P)+'\n'+scripts_block(P)+'\n</body>\n</html>')
    return page.replace('%%P%%','')
# ---------------- sidebar (Edukin widgets) ----------------
def widget_links(title, links, P):
    if not links: return ''
    lis=''.join(f'<li><a href="{P}{h}">{html.escape(t)}</a></li>' for t,h in links)
    return f'<div class="widget widget-categories"><h4 class="widget-title"><span>{html.escape(title)}</span></h4><ul class="categories-wrap">{lis}</ul></div>'

def _pdf_label(href):
    n=href.split('/')[-1].rsplit('.',1)[0]
    n=re.sub(r'[-_]+',' ',n)
    n=re.sub(r'\b\d{6,}\b','',n)  # strip long numeric suffixes
    n=re.sub(r'\s+',' ',n).strip()
    return (n[:44] or 'Document')
def widget_downloads(content, P):
    hrefs=[]
    for h in re.findall(r'<a href="%%P%%(assets/uploads/[^"]+\.pdf)"',content):
        if h not in hrefs: hrefs.append(h)
    if not hrefs: return ''
    lis=''.join(f'<li><a href="{P}{h}" target="_blank"><i class="fa fa-file-pdf-o"></i> {html.escape(_pdf_label(h))}</a></li>' for h in hrefs[:12])
    return f'<div class="widget widget-categories widget-downloads"><h4 class="widget-title"><span>Downloads</span></h4><ul class="categories-wrap">{lis}</ul></div>'

WIDGET_CTA='''<div class="widget widget-sent"><div class="apply-admission"><div class="apply-admission-wrap type1 bd-type1"><div class="apply-admission-inner">
<h2 class="title text-center"><span>Apply for Admission</span></h2>
<div class="caption text-center text-white">FYUGP &amp; PG programmes open</div>
<div class="mig-cta-btn"><a href="%%P%%admission/" class="btn">Apply Now</a></div>
</div></div></div></div>'''
WIDGET_CONTACT='''<div class="widget widget-contact-info"><h4 class="widget-title"><span>Contact</span></h4>
<ul class="mig-contact"><li><i class="fa fa-map-marker"></i> Poopalam, Valambur (P.O), Perinthalmanna, Malappuram, Kerala 679325</li>
<li><i class="fa fa-phone"></i> <a href="tel:+917994188918">+91 7994 188918</a></li>
<li><i class="fa fa-envelope"></i> <a href="mailto:mail@ajascollege.ac.in">mail@ajascollege.ac.in</a></li></ul></div>'''

def slugify(t):
    return re.sub(r'-+','-',re.sub(r'[^a-z0-9]+','-',t.lower())).strip('-')[:60] or 'section'

def anchor_headings(content):
    """Give h2/h3 stable ids and return (content, [(level,text,id)]) for the jump nav."""
    toc=[]; seen={}
    def repl(m):
        lvl=int(m.group(1)); inner=m.group(2)
        txt=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',inner))).strip()
        if not txt or len(txt)>90: return m.group(0)
        sid=slugify(txt)
        seen[sid]=seen.get(sid,0)+1
        if seen[sid]>1: sid=f'{sid}-{seen[sid]}'
        toc.append((lvl,txt,sid))
        return f'<h{lvl} id="{sid}">{inner}</h{lvl}>'
    content=re.sub(r'<h([23])>(.*?)</h\1>',repl,content,flags=re.S)
    return content,toc

def widget_toc(toc,P):
    """'On this page' nav — only worth showing once a page has real sections."""
    if len(toc)<3: return ''
    lis=''.join(f'<li class="lv{l}"><a href="#{i}">{html.escape(t)}</a></li>' for l,t,i in toc[:14])
    return ('<div class="widget widget-toc"><h4 class="widget-title"><span>On this page</span></h4>'
            f'<ul class="toc-wrap">{lis}</ul></div>')

def build_sidebar(d, content, P, toc=None):
    w=[]
    parts=d.split('/')
    if toc: w.append(widget_toc(toc,P))
    def sib(pref,label,limit=14):
        items=[(t,x+'/') for x,t in PAGES if x.startswith(pref+'/') and x!=pref]
        return widget_links(label, items[:limit], P)
    if parts[0]=='departments' and d!='departments':
        w.append(sib('departments','All Departments'))
    elif parts[0]=='faculties' and d!='faculties':
        w.append(widget_links('Faculty', [(t,x+'/') for x,t in PAGES if x.startswith('faculties/') and x!='faculties'][:12], P))
    elif parts[0]=='clubs--cells':
        w.append(sib('clubs--cells','Clubs & Cells'))
    elif parts[0]=='labs':
        w.append(sib('labs','Laboratories'))
    elif parts[0]=='college-news' and d!='college-news':
        w.append(widget_links('Recent News',[(t,x+'/') for x,t in PAGES if x.startswith('college-news/') and x!='college-news'][:8], P))
    elif parts[0]=='event' and d!='event':
        w.append(widget_links('Events',[(t,x+'/') for x,t in PAGES if x.startswith('event/') and x!='event'][:8], P))
    else:
        w.append(widget_links('Quick Links',[('Overview','overview/'),('Vision & Mission','vision-mission/'),('Admission','admission/'),('Departments','departments/'),('Faculties','faculties/'),('Library','library/'),('Examinations','examinations/'),('Contact Us','contact/')], P))
    w.append(widget_downloads(content, P))
    w.append(WIDGET_CTA)
    w.append(WIDGET_CONTACT)
    return '<div class="sidebar">'+''.join(x for x in w if x)+'</div>'

# ---------------- content-page wrappers ----------------
def _sitecontent(content):
    return f'''<div class="site-content clearfix"><article class="post post-blog-single"><div class="content-blog-single"><div class="content-blog-single-inner"><div class="content-blog-single-wrap migrate-content">
{content}
</div></div></div></article></div>'''

def wrap_textpage(content, d, P):
    content,toc=anchor_headings(content)
    return f'''<div class="blog-single content-blog"><div class="container"><div class="row">
<div class="col-lg-8">{_sitecontent(content)}</div>
<div class="col-lg-4"><div class="sidebar-sticky">{build_sidebar(d,content,P,toc)}</div></div>
</div></div></div>'''

def wrap_profile(content, d, P, title):
    """People pages (principal, vice-principal, faculty bios) as a profile card
    rather than a blog post with a sidebar: portrait, name, credentials, bio."""
    portrait=None
    m=re.search(r'<img[^>]+src="(%%P%%[^"]+|[^"]+)"[^>]*>',content)
    if m:
        portrait=m.group(1)
        content=content[:m.start()]+content[m.end():]
    content=re.sub(r'<div class="fac-photo">\s*</div>','',content)
    # short leading headings/paragraphs are credentials and role, not prose
    meta=[]
    while True:
        mm=re.match(r'\s*<(h[1-6]|p)[^>]*>(.*?)</\1>',content,re.S)
        if not mm: break
        txt=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',mm.group(2)))).strip()
        if not txt or len(txt)>90 or len(meta)>=3: break
        if txt.lower()==title.lower(): content=content[mm.end():]; continue
        meta.append(txt); content=content[mm.end():]
    # On /principal/ and /vice-principal/ the page title is the ROLE and the
    # first heading is the person's name. On faculty pages it is the reverse.
    name, role = title, ''
    if d in PEOPLE and meta:
        name, role = meta[0], title
        meta = meta[1:]
    pic=(f'<div class="profile-photo"><img src="{portrait}" alt="{html.escape(name)}"></div>'
         if portrait else '<div class="profile-photo"><div class="mig-noimg"></div></div>')
    metah=''.join(f'<li>{html.escape(x)}</li>' for x in meta)
    body=re.sub(r'^\s+','',content)
    bio=(f'<div class="profile-bio migrate-content">{body}</div>'
         if re.sub('<[^>]+>','',body).strip() else '')
    back=('faculties/','Back to all faculty') if d.startswith('faculties/') else ('college-council/','College administration')
    return f'''<div class="blog-single content-blog profile-page"><div class="container">
<div class="profile-card">
{pic}
<div class="profile-head">
{f'<span class="profile-role">{html.escape(role)}</span>' if role else ''}
<h1 class="profile-name">{html.escape(name)}</h1>
{f'<ul class="profile-meta">{metah}</ul>' if metah else ''}
<a class="profile-back" href="{P}{back[0]}"><i class="fa fa-angle-left" aria-hidden="true"></i> {back[1]}</a>
</div>
</div>
{bio}
</div></div>'''

def wrap_narrow(content, d, P):
    """Short institutional pages read badly as a blog post beside a sidebar —
    give them a single centred column and move the links to the foot."""
    content,toc=anchor_headings(content)
    links=[('Overview','overview/'),('Vision &amp; Mission','vision-mission/'),
           ('Departments','departments/'),('Admission','admission/'),
           ('Faculties','faculties/'),('Contact Us','contact/')]
    chips=''.join(f'<a class="page-chip" href="{P}{h}">{t}</a>' for t,h in links)
    return f'''<div class="blog-single content-blog narrow-page"><div class="container">
<div class="row justify-content-center"><div class="col-lg-9">
<div class="site-content clearfix"><article class="post post-blog-single">
<div class="content-blog-single"><div class="content-blog-single-inner">
<div class="content-blog-single-wrap migrate-content">{content}</div>
</div></div></article></div>
<div class="page-chips"><span class="chips-label">Explore more</span>{chips}</div>
</div></div>
</div></div>'''

def wrap_gallery(content,imgs,d,P):
    imgs=[im for im in dict.fromkeys(imgs) if os.path.exists(os.path.join(OUT,im))]
    grid=''.join(f'<div class="col-lg-4 col-md-6 gal-item"><a href="{P}{im}" data-fancybox="g"><img src="{P}{im}" alt="" class="img-fluid"></a></div>' for im in imgs)
    txt=re.sub(r"<p>\s*<img[^>]+>\s*</p>","",re.sub(r"(?<!<p>)<img[^>]+>","",content))
    body=f'<div class="content-blog-single-wrap migrate-content">{txt}</div>' if re.sub("<[^>]+>","",txt).strip() else ''
    return f'''<div class="blog-single content-blog"><div class="container">
{('<div class="row"><div class="col-lg-12">'+body+'</div></div>') if body else ''}
<div class="row gallery-grid">{grid}</div>
</div></div>'''

def wrap_wide_form(content, formhtml, d, P):
    """Admission-style page: the programme grid gets the full container width,
    with the enquiry form as a separate band underneath. Squeezing a two-column
    card grid into a 8/12 column beside a sidebar made it unreadable."""
    return f'''<div class="blog-single content-blog wide-page"><div class="container">
<div class="migrate-content wide-intro">{content}</div>
<div class="row justify-content-center"><div class="col-lg-8">
<div class="site-content clearfix"><div class="form-band">
<h2 class="form-band-title">Admission enquiry</h2>
<div class="migrate-form-note"><i class="fa fa-info-circle"></i> This form is a static reproduction of the
original. Submissions are not processed — please use the contact details to reach the college.</div>
{formhtml}
</div></div>
</div></div>
</div></div>'''

def wrap_form(content, formhtml, d, P):
    inner=f'''<div class="content-blog-single-wrap migrate-content">{content}
<div class="migrate-form-note"><i class="fa fa-info-circle"></i> This form is a static reproduction of the original. Submissions are not processed — please use the contact details to reach the college.</div>
{formhtml}</div>'''
    return f'''<div class="blog-single content-blog"><div class="container"><div class="row">
<div class="col-lg-8"><div class="site-content clearfix"><article class="post post-blog-single">{inner}</article></div></div>
<div class="col-lg-4"><div class="sidebar-sticky">{build_sidebar(d,content,P)}</div></div>
</div></div></div>'''

def form_block(fields):
    fh='<form class="migrate-form" onsubmit="return false;"><div class="row">'
    for f in fields:
        col='col-lg-12' if f[0]=='textarea' else 'col-lg-6'
        fh+=f'<div class="{col}">'
        if f[0]=='textarea': fh+=f'<textarea placeholder="{f[1]}" rows="5"></textarea>'
        else: fh+=f'<input type="{f[0]}" placeholder="{f[1]}">'
        fh+='</div>'
    fh+='</div><button class="btn send-button" type="submit">Submit</button></form>'
    return fh

# ---------------- page inventory ----------------
def all_pages():
    rows=[]
    for f in sorted(glob.glob('**/index.html',recursive=True))+['index.html']:
        d=os.path.dirname(f) or '.'
        if '/feed' in d or d=='feed' or d.startswith(('2024','2026','author','comments','wp-content','wp-includes')): continue
        if d=='faculties/x' or d=='graduation-ceremony-2026': continue
        s=open(f,encoding='utf-8',errors='ignore').read()
        m=re.search(r'<title>([^<]*)</title>',s)
        rows.append((d,clean_title(m.group(1) if m else d)))
    seen=set();out=[]
    for d,t in rows:
        if d in seen: continue
        seen.add(d);out.append((d,t))
    return out
PAGES=all_pages()
FORMS={'contact','feedback','payments','register-a-complaint','library-book-suggession','counselling','counselling-desk-reviews','admission','scholorship'}
GALL={'state-off-the-art-facilities','student-life','seminar-hall'}
PEOPLE={'principal','vice-principal'}
FORMDEF={
 'contact':[('text','Full name'),('email','Email Address'),('text','Subject'),('textarea','Your message')],
 'feedback':[('text','Full name'),('email','Email Address'),('text','Category'),('textarea','Your feedback')],
 'payments':[('text','Student name'),('text','Register / Admission no'),('text','Purpose'),('text','Amount')],
 'register-a-complaint':[('text','Full name'),('email','Email Address'),('text','Subject'),('textarea','Complaint details')],
 'library-book-suggession':[('text','Full name'),('text','Department'),('text','Book title'),('text','Author'),('textarea','Remarks')],
 'counselling':[('text','Full name'),('email','Email Address'),('text','Phone'),('textarea','Reason for counselling')],
 'counselling-desk-reviews':[('text','Full name'),('text','Department'),('textarea','Your review')],
 'admission':[('text','Full name'),('email','Email Address'),('text','Phone'),('text','Programme applying for'),('textarea','Message')],
 'scholorship':[('text','Full name'),('text','Register no'),('text','Scholarship name'),('textarea','Details')],
}
def crumbs_for(d,title):
    c=[('Home','index.html')]
    parts=d.split('/')
    if parts[0]=='faculties' and d!='faculties': c.append(('Faculties','faculties/'))
    elif parts[0]=='departments' and d!='departments': c.append(('Departments','departments/'))
    elif parts[0]=='clubs--cells': c.append(('Students Corner','index.html'))
    elif parts[0]=='college-news' and d!='college-news': c.append(('News','college-news/'))
    elif parts[0]=='event' and d!='event': c.append(('Events','event/'))
    elif parts[0]=='labs': c.append(('Facilities','index.html'))
    c.append((title,d+'/'))
    return c

def write_page(newpath, s):
    fp=os.path.join(OUT,newpath); os.makedirs(os.path.dirname(fp),exist_ok=True)
    open(fp,'w',encoding='utf-8').write(s)
# ---------------- listing builders (native Edukin components) ----------------
def _thumb_and_excerpt(d):
    content,imgs,raw=extract_content(os.path.join(SRC,d,'index.html'))
    return (first_img(content) or pick_photo(raw)), first_para(content)

_MONTHS=['January','February','March','April','May','June','July',
         'August','September','October','November','December']
def published_date(d):
    """(pretty, day, MONTH) from the archived page's article:published_time."""
    try: s=open(os.path.join(SRC,d,'index.html'),encoding='utf-8',errors='ignore').read(40000)
    except OSError: return ('','','')
    m=re.search(r'article:published_time" content="(\d{4})-(\d{2})-(\d{2})',s)
    if not m: return ('','','')
    y,mo,dy=m.group(1),int(m.group(2)),int(m.group(3))
    return (f'{_MONTHS[mo-1]} {dy}, {y}', f'{dy:02d}', _MONTHS[mo-1][:3].upper())

def course_card(title,href,thumb,excerpt,P):
    """Edukin .flat-course card — used for departments, clubs, labs, events."""
    pic=(f'<img src="{P}{thumb}" alt="{html.escape(title)}">' if thumb else '<div class="mig-noimg"></div>')
    ex=html.escape(excerpt[:135])+('…' if len(excerpt)>135 else '') if excerpt else ''
    return f'''<div class="course clearfix col-lg-4 col-md-6 col-sm-12">
<div class="flat-course">
<div class="featured-post post-media"><div class="entry-image pic">{pic}
<div class="hover-effect"></div>
<div class="links"><a href="{P}{href}">View</a></div>
</div></div>
<div class="course-content clearfix"><div class="wrap-course-content">
<h4><a href="{P}{href}">{html.escape(title)}</a></h4>
<p>{ex}</p>
<div class="author-info"><div class="enroll"><a href="{P}{href}">Read more</a></div></div>
</div></div>
</div></div>'''

def team_card(title,href,thumb,role,P):
    """Edukin .team-box-layout-h1 — used for the faculty grid."""
    pic=(f'<img src="{P}{thumb}" alt="{html.escape(title)}" class="img-fluid">' if thumb else '<div class="mig-noimg"></div>')
    return f'''<div class="col-lg-3 col-md-4 col-sm-6 col-xs-12">
<div class="team-box-layout-h1">
<div class="item-img">{pic}</div>
<div class="item-content">
<div class="item-title"><a href="{P}{href}">{html.escape(title)}</a></div>
<div class="item-subtitle">{html.escape(role)}</div>
</div>
</div></div>'''

def blog_card(title,href,thumb,excerpt,P,date=('','','')):
    """Edukin .post-blog card — used for news and event listings."""
    pic=(f'<div class="featured-post"><a href="{P}{href}"><img src="{P}{thumb}" alt="{html.escape(title)}"></a></div>'
         if thumb else '<div class="featured-post"><div class="mig-noimg"></div></div>')
    ex=html.escape(excerpt[:190])+('…' if len(excerpt)>190 else '') if excerpt else ''
    pretty,day,mon=date
    cal=(f'<div class="post-meta"><div class="clendar-wrap">'
         f'<div class="day">{day}</div><div class="month">{mon}</div></div></div>') if day else ''
    return f'''<article class="post-blog box-shadow-type2">
{pic}
<div class="content-post content-post-blog">
{cal}
<div class="content-post-inner">
<h3 class="entry-title"><a href="{P}{href}">{html.escape(title)}</a></h3>
{f'<p class="entry-date">{pretty}</p>' if pretty else ''}
{f'<p>{ex}</p>' if ex else ''}
<div class="btn-readmore"><a href="{P}{href}" class="readmore">Read more <i class="fa fa-angle-right" aria-hidden="true"></i></a></div>
</div></div>
</article>'''

LISTING_INTRO={
 'faculties':'Our teaching community brings together scholars and practitioners across the arts, sciences, commerce and computing — mentoring students well beyond the syllabus.',
 'departments':'Fourteen departments offering UG (Honours) and PG programmes affiliated to the University of Calicut.',
 'college-news':'Announcements, achievements and campus happenings from Al Jamia Arts &amp; Science College.',
 'event':'Seminars, workshops, outreach drives and cultural programmes organised across the campus.',
 'clubs--cells':'Student clubs and statutory cells covering the arts, sports, service, welfare and redressal.',
 'labs':'Practical teaching laboratories supporting the science, computing and psychology programmes.',
}

def build_listing(index_slug, child_dirs, title, newpath, kind='course'):
    P=prefix(newpath)
    intro=LISTING_INTRO.get(index_slug,'')
    intro_html=f'<p class="listing-intro">{intro}</p>' if intro else ''
    if kind=='team':
        cards=[]
        for d,t in child_dirs:
            thumb,ex=_thumb_and_excerpt(d)
            role=re.sub(r'\s+',' ',ex).strip()
            role=('Assistant Professor' if not role else role.split('.')[0][:52])
            cards.append(team_card(t,d+'/',thumb,role,P))
        body=f'''<div class="flat-team blog-single content-blog"><div class="container">
{intro_html}<div class="row">{''.join(cards)}</div>
</div></div>'''
    elif kind=='blog':
        left=[]
        # newest first, by the archived page's raw ISO publish date
        def _iso(d):
            try: s=open(os.path.join(SRC,d,'index.html'),encoding='utf-8',errors='ignore').read(40000)
            except OSError: return ''
            m=re.search(r'article:published_time" content="([\d\-T:]+)',s)
            return m.group(1) if m else ''
        dated=sorted(child_dirs,key=lambda x:_iso(x[0]),reverse=True)
        for d,t in dated:
            thumb,ex=_thumb_and_excerpt(d)
            left.append(blog_card(t,d+'/',thumb,ex,P,published_date(d)))
        sb=build_sidebar(index_slug,'',P)
        body=f'''<div class="blog-bl content-blog blog-single"><div class="container">
{intro_html}<div class="row">
<div class="col-lg-8"><div class="site-content">{''.join(left)}</div></div>
<div class="col-lg-4">{sb}</div>
</div></div></div>'''
    else:
        cards=[]
        for d,t in child_dirs:
            thumb,ex=_thumb_and_excerpt(d)
            cards.append(course_card(t,d+'/',thumb,ex,P))
        body=f'''<div class="courses-grid-page blog-single content-blog"><div class="container">
{intro_html}<div class="flat-courses clearfix"><div class="row">{''.join(cards)}</div></div>
</div></div>'''
    return shell(title,[('Home','index.html'),(title,index_slug+'/')],body,newpath)

# ---------------- home builder ----------------
# Real content lifted from the old ajascollege.ac.in home page.
# Hero backgrounds only — the headline is fixed. Each was checked to be a real
# campus photograph (the March-2025 set also contains certificate scans).
HOME_SLIDES=[
 dict(img='assets/uploads/2024/01/P1222323-building-2048x1154-1.webp'),   # campus block, greenery
 dict(img='assets/uploads/2025/03/WhatsApp-Image-2025-03-17-at-3.27.45-PM.jpeg'),  # entrance signage
 dict(img='assets/uploads/2025/03/WhatsApp-Image-2025-03-17-at-4.16.10-PM.jpeg'),  # library
]

PARTNERS=[('assets/uploads/2025/05/University-Logo.jpg','University of Calicut'),
          ('assets/uploads/2024/01/UGC-Logo-e1748242432780.jpg','UGC'),
          ('assets/uploads/2024/01/AICTE-Logo-e1748242290739.jpg','AICTE'),
          ('assets/uploads/2025/10/Naac-Symbol.jpg','NAAC'),
          ('assets/uploads/2024/01/ISO-Logo-e1748242407313.jpg','ISO certified')]

UG_PROGRAMMES=['B.Com','BBA','BCA','B.Sc. Microbiology','BA Islamic Studies','BA English',
               'B.Sc. Geography','B.Sc. Psychology','B.Sc. Food Technology',
               'B.Sc. Computer Science','B.Sc. Artificial Intelligence']
PG_PROGRAMMES=['MA Islamic Finance','M.Sc. Psychology','MA Arabic']

# The Edukin package ships blank placeholder art for every icon and photo slot
# (ThemeForest strips licensed imagery), so icon slots use Font Awesome glyphs
# and every photographic slot uses the college's own photographs.
FACILITIES=[('Library','library/','fa-book',
             'A reference and lending library with OPAC access, journals, e-resources and dedicated reading space for every department.'),
            ('Laboratories','labs/computer-lab/','fa-flask',
             'Computer, Artificial Intelligence, Psychology, Geography, Microbiology, Physics and Food Technology labs, equipped for hands-on coursework.'),
            ('Seminar Hall','seminar-hall/','fa-microphone',
             'An air-conditioned seminar hall used for conferences, guest lectures, workshops and departmental programmes throughout the year.')]

BENEFITS=[('Value-based education','vision-mission/','fa-lightbulb-o',
           'A curriculum built to enrich, enlighten and empower — shaping character alongside academic achievement.'),
          ('Recognised &amp; accredited','recognitions/','fa-certificate',
           'Minority status, affiliation to the University of Calicut, Government of Kerala recognition and ISO certification.'),
          ('Skills &amp; placement','placement-cell/','fa-briefcase',
           'Add-on certificate courses, ASAP, Keltron, G-Tec and NPTEL/SWAYAM pathways, backed by an active placement cell.'),
          ('Research &amp; innovation','research-and-publications/','fa-flask',
           'Faculty publications, patents and an Innovation &amp; Entrepreneurship Development Centre driving student projects.')]

COUNTERS=[('900','Students','bg-cl25cf71'),('12','Programmes','bg-cla476b4'),
          ('30','Faculty members','bg-clffbe34'),('12','Alumni (thousands)','bg-clfb6d6d')]

TESTIMONIALS=[
 ('assets/uploads/2024/05/Mohammed-Azeer.jpeg','Mohammed Azeer','MA Islamic Finance, 2016–2018',
  'I am glad I chose Al Jamia Arts and Science College, which has guided me towards my goals and supported me in every way. Everyone here is an expert in their field, making it an excellent platform for students aiming for higher studies.'),
 ('assets/uploads/2024/05/Mohammed-sabeel.jpeg','Mohammed Shabeel K.','BBA Finance, 2016–2019',
  'I have loved my three years studying BBA at Al Jamia. The college sharpened my analytical, management and problem-solving skills, preparing me to be a creative and influential leader who will make a difference.'),
 ('assets/uploads/2024/05/559.jpg','Mufeeda Sulfath A. P','BBA, 2015–2018',
  'From 2015 to 2018 I attended Al Jamia Arts and Science College, where I made lasting connections and felt at home. The support and knowledge I gained there have left a lasting impact on me.'),
 ('assets/uploads/2024/05/Shadiya.jpeg','Sadiya','B.Sc. Psychology, 2016–2019',
  'The years I spent here shaped both my academic direction and my confidence. I cherish this institution and am excited about the future it has prepared me for.'),
 ('assets/uploads/2024/05/Safwa.jpeg','Safwa K','B.Sc. Psychology, 2016–2019 · 1st Rank Holder',
  'The faculty made room for every question and pushed me further than I thought I could go. Graduating as first rank holder is something I owe to the mentoring I received here.'),
 ('assets/uploads/2024/05/Mohammed-sibin.jpeg','Mohammed Shibin Faris','B.Com CA, 2016–2019',
  'During my three years at Al Jamia I had incredible experiences. Coaches and teachers alike made learning and athletics rewarding. The community encouraged me to explore my interests and guided my academic choices.'),
]

QUICK_LINKS=[('fa-inr','Fee details','assets/uploads/2025/02/SF-FEE-Addndm.pdf',True),
             ('fa-building-o','State-of-the-art facilities','state-off-the-art-facilities/',False),
             ('fa-graduation-cap','Scholarships','scholorship/',False),
             ('fa-comments-o','Register a complaint','register-a-complaint/',False)]

EVENT_COLORS=['7ecc88','3f4c99','ff5f60']

# The archived "Students Corner" page captured no body content, so it is
# rebuilt as a hub over the destinations the old site's own menu placed
# under it — no invented copy.
STUDENT_LIFE=[
 ('Clubs &amp; Cells','clubs--cells/','fa-users',
  'Twenty-five student clubs and statutory cells — arts, sports, coding, literary, nature, health, tourism and more.'),
 ('NSS','nss/','fa-heart',
  'National Service Scheme units running camps, outreach drives and community service throughout the year.'),
 ('Career &amp; Placements','career-and-placements/','fa-briefcase',
  'Training, aptitude coaching and recruitment drives coordinated by the placement cell.'),
 ('Scholarships','scholorship/','fa-graduation-cap',
  'Central, state and institutional scholarship schemes available to students of the college.'),
 ('Counselling Centre','counselling/','fa-comments-o',
  'Confidential academic and personal counselling with a qualified counsellor on campus.'),
 ('Library','library/','fa-book',
  'Reference and lending collections, journals, e-resources and OPAC search.'),
 ('Add-on &amp; Certificate Courses','add-on-certificate-courses/','fa-certificate',
  'Short certificate programmes taken alongside the degree, including ASAP, Keltron and G-Tec pathways.'),
 ('Register a Complaint','register-a-complaint/','fa-exclamation-circle',
  'Grievance redressal, anti-ragging and anti-sexual-harassment reporting channels.'),
]

# The archived copy of this page contains only header and footer markup, so it
# is rebuilt from the certificate-course providers that do have their own pages.
CERT_COURSES=[
 ('ASAP Kerala','asap/','fa-certificate',
  'Additional Skill Acquisition Programme courses run with the Government of Kerala, taken alongside the degree.'),
 ('Keltron','keltron/','fa-microchip',
  'Certificate courses in research methodology, data analytics and applied computing.'),
 ('G-Tec','g-tec/','fa-laptop',
  'Computer and software certification programmes delivered on campus.'),
 ('NPTEL &amp; SWAYAM','nptel-swayam/','fa-play-circle-o',
  'MOOC pathways from the national platforms, with local mentoring and proctored exams.'),
 ('Skill enhancement programmes','skill-enhancement-programs/','fa-line-chart',
  'Departmental workshops and short programmes that build employability alongside the syllabus.'),
 ('Placement Cell','placement-cell/','fa-briefcase',
  'Training, aptitude coaching and recruitment drives for final-year students.'),
]

def build_hub(title, slug, intro, items, newpath):
    P=prefix(newpath)
    cards=''.join(f'''<div class="col-lg-4 col-md-6 col-sm-12">
<a class="club-chip" href="{P}{h}"><i class="fa {ic}" aria-hidden="true"></i> {t}</a>
<p class="chip-note">{txt}</p></div>''' for t,h,ic,txt in items)
    body=f'''<div class="blog-single content-blog"><div class="container">
<p class="listing-intro">{intro}</p>
<div class="row mig-clubs">{cards}</div>
</div></div>'''
    return shell(title,[('Home','index.html'),(title,slug+'/')],body,newpath)

def build_student_life(newpath):
    return build_hub('Students Corner','student-life',
        'Everything that happens around the classroom — clubs and cells, service, counselling, '
        'scholarships, careers and the library. Al Jamia Arts and Science College runs an active '
        'campus life alongside its academic programmes.',
        STUDENT_LIFE, newpath)

def build_home():
    P=''
    depts=[(d,t) for d,t in PAGES if d.startswith('departments/') and d!='departments'][:6]
    news =[(d,t) for d,t in PAGES if d.startswith('college-news/') and d!='college-news'][:6]
    events=[(d,t) for d,t in PAGES if d.startswith('event/') and d!='event'][:3]

    # --- 1. hero ---------------------------------------------------------
    # Plain markup rather than Revolution Slider: the plugin keeps its caption
    # layers at visibility:hidden until a GSAP timeline runs, so the headline —
    # the most important text on the site — depends on a 2018 jQuery plugin
    # booting correctly. The background images cross-fade in pure CSS.
    layers=''.join(f'<span class="hero-layer hl{i+1}" style="background-image:url({s["img"]})"></span>'
                   for i,s in enumerate(HOME_SLIDES))
    hero=f'''<section class="ajas-hero">
<div class="hero-media">{layers}<span class="hero-scrim"></span></div>
<div class="container"><div class="hero-inner">
<p class="hero-kicker">Since 2010 &middot; Perinthalmanna, Kerala</p>
<h1 class="hero-title">Value-based education,<br>rooted in Kerala.</h1>
<p class="hero-text">Al Jamia Arts and Science College moulds students into professionally competent,
socially responsible and morally sound citizens &mdash; affiliated to the University of Calicut and
recognised by the Government of Kerala.</p>
<div class="hero-cta">
<a href="admission/" class="hero-btn hero-btn-primary">Apply for admission</a>
<a href="overview/" class="hero-btn hero-btn-ghost">Explore the college</a>
</div>
<ul class="hero-facts">
<li><strong>14</strong><span>Departments</span></li>
<li><strong>11</strong><span>UG Honours</span></li>
<li><strong>3</strong><span>PG programmes</span></li>
<li><strong>2010</strong><span>Established</span></li>
</ul>
</div></div>
</section><!-- hero -->'''

    # --- 2. accreditations + admission box ------------------------------
    # Three action tiles riding the bottom edge of the hero, then the
    # accreditation marks on their own quiet band. Edukin's single floating
    # admissions box collided with the badge row and with the sticky header.
    tiles=[('fa-pencil-square-o','Admissions 2026 – 27','FYUGP &amp; PG programmes are open','admission/','Apply now','tile-primary'),
           ('fa-graduation-cap','Programmes','11 UG Honours &amp; 3 PG degrees','programe-offered/','Explore','tile-navy'),
           ('fa-file-text-o','Prospectus &amp; fees','Download the fee structure','assets/uploads/2025/02/SF-FEE-Addndm.pdf','Download','tile-light')]
    tl=''
    for ic,t,sub,h,cta,cls in tiles:
        ext=' target="_blank" rel="noopener"' if h.endswith('.pdf') else ''
        tl+=f'''<div class="col-lg-4 col-md-4 col-sm-12"><a class="action-tile {cls}" href="{h}"{ext}>
<span class="tile-ico"><i class="fa {ic}" aria-hidden="true"></i></span>
<span class="tile-body"><span class="tile-title">{t}</span><span class="tile-sub">{sub}</span></span>
<span class="tile-cta">{cta} <i class="fa fa-long-arrow-right" aria-hidden="true"></i></span>
</a></div>'''
    logos=''.join(f'<li><img src="{u}" alt="{html.escape(n)}"><span>{html.escape(n)}</span></li>'
                  for u,n in PARTNERS)
    partners=f'''<section class="ajas-actions">
<div class="container"><div class="row">{tl}</div></div>
</section><!-- quick actions -->
<section class="partner-clients ajas-accred">
<div class="container">
<p class="accred-label">Affiliated, recognised &amp; accredited by</p>
<ul class="accred-row">{logos}</ul>
</div>
</section><!-- accreditation -->'''

    # --- 3. principal's message (flat-introduce) ------------------------
    introduce=f'''<section class="flat-introduce flat-introduce-style1 clearfix">
<div class="container">
<div class="col-left"><div class="videobox">
<a href="principal/"><img src="assets/uploads/2025/06/WhatsApp-Image-2025-06-12-at-9.46.05-AM.jpeg" alt="Principal, Al Jamia Arts &amp; Science College"></a>
</div></div>
<div class="col-right"><div class="content-introduce content-introduce-style1">
<div class="title-section">
<p class="sub-title lt-sp25">Dr. (Lt. Cdr. Rtd.) C. K. Abdul Rabbi Nistar</p>
<div class="flat-title larger heading-type1">Principal&rsquo;s message</div>
</div>
<div class="content-introduce-inner">
<p>It gives me immense pleasure to lead an institution that stands at the confluence of tradition and modernity. At AJASC we firmly believe that education is not merely about academic achievement but about building character, inspiring purpose and transforming lives.</p>
<p>Guided by our vision &mdash; to provide value-based education to enrich, enlighten and empower the young generation &mdash; we strive to foster an environment where students grow intellectually, morally and socially.</p>
<div class="content-list"><ul>
<li><span class="text">Established in 2010, affiliated to the University of Calicut.</span></li>
<li><span class="text">Minority status, recognised by the Government of Kerala.</span></li>
<li><span class="text">A curriculum, campus and faculty tailored to modern arts and science education.</span></li>
</ul></div>
<div class="btn-about"><a href="principal/" class="btn-box-shadow">Read full message</a></div>
</div>
</div></div>
</div>
</section><!-- flat-introduce -->'''

    # --- 4. programmes + department cards -------------------------------
    dcards=''
    for d,t in depts:
        thumb,ex=_thumb_and_excerpt(d)
        dcards+=course_card(t,d+'/',thumb,ex,P)
    ug=''.join(f'<li>{html.escape(x)}</li>' for x in UG_PROGRAMMES)
    pg=''.join(f'<li>{html.escape(x)}</li>' for x in PG_PROGRAMMES)
    programmes=f'''<section class="online-courses online-courses-style1 ajas-programmes">
<div class="container">
<div class="title-section text-center">
<p class="sub-title lt-sp17">What you can study here</p>
<div class="flat-title medium">Programmes offered</div>
</div>
<p class="listing-intro">Our students are guaranteed an exceptional educational experience through a diverse range of regular degree and postgraduate courses.</p>
<div class="row prog-columns">
<div class="col-lg-6 col-md-6 col-sm-12">
<div class="prog-col"><h3>UG (Honours) Programmes</h3><span class="prog-sub">{len(UG_PROGRAMMES)} four-year honours degrees</span><ul>{ug}</ul></div>
</div>
<div class="col-lg-6 col-md-6 col-sm-12">
<div class="prog-col"><h3>PG Programmes</h3><span class="prog-sub">{len(PG_PROGRAMMES)} postgraduate degrees</span><ul>{pg}</ul>
<p class="prog-note">Postgraduate study at Al Jamia builds directly on the honours programmes, with
research supervision and industry-linked coursework. Full eligibility criteria, intake and fee details
are listed on the programmes page.</p>
</div>
</div>
</div>
<div class="text-center pd-top15"><a href="programe-offered/" class="btn-box-shadow">All programmes &amp; eligibility</a></div>
<div class="title-section text-center pd-top60">
<p class="sub-title lt-sp17">Explore</p>
<div class="flat-title medium">Our departments</div>
</div>
<div class="flat-courses clearfix"><div class="row">{dcards}</div></div>
<div class="text-center pd-top15"><a href="departments/" class="btn bg-clff5f60 ajas-apply-btn">View all departments</a></div>
</div>
</section><!-- online-courses -->'''

    # --- 5. facilities (parallax services) ------------------------------
    fbox=''
    pads=['0% 30% 0% 0%','0% 15% 0% 16%','0% 0% 0% 30.5%']
    names=['text-one','text-two','text-three']
    for i,(t,h,ic,txt) in enumerate(FACILITIES):
        fbox+=f'''<div class="col-lg-4">
<div class="services-content-box themesflat-content-box" data-padding="{pads[i]}" data-mobipadding="0% 0% 0% 0%" data-smobipadding="0% 0% 0% 0%">
<div class="flat-imagebox imagebox-services style1"><div class="imagebox-content">
<span class="ajas-icon"><i class="fa {ic}" aria-hidden="true"></i></span>
<h5 class="{names[i]} text-white">{t}</h5>
<p class="text-white">{txt}</p>
<div class="read-more"><a href="{h}">Read More</a></div>
</div></div>
</div></div>'''
    services=f'''<section class="flat-services style1 parallax parallax1 clearfix ajas-services">
<div class="section-overlay"></div>
<div class="container-fluid"><div class="row">{fbox}</div></div>
</section><!-- flat-services -->'''

    # --- 6. why choose us + apply form ----------------------------------
    ibox=''
    imgcls=['img-one','img-two','img-three','img-four']
    for i,(t,h,ic,txt) in enumerate(BENEFITS):
        ibox+=f'''<div class="col-lg-6 col-md-6 col-sm-6 col-sx-12">
<div class="themesflat-content-box" data-padding="0% 4% 0% 0%" data-mobipadding="0% 0% 0% 0%" data-smobipadding="0% 0% 0% 0%">
<div class="iconbox">
<div class="iconbox-icon"><span class="ajas-icon"><i class="fa {ic}" aria-hidden="true"></i></span></div>
<div class="iconbox-content {imgcls[i]}"><h3><a href="{h}">{t}</a></h3><p>{txt}</p></div>
</div>
</div></div>'''
    benefit=f'''<section class="flat-benefit style1 clearfix ajas-benefit">
<div class="container-fluid">
<div class="col-benefit-left"><div class="wrap-inconbox-benefit">
<div class="title-section"><div class="flat-title small heading-type2 text-white">Why choose AJAS?</div></div>
<div class="iconbox-benefit iconbox-benefit-style1"><div class="row">{ibox}</div></div>
</div></div>
<div class="col-benefit-right">
<div class="apply-admission bg-apply-type1">
<div class="apply-admission-wrap type3 bd-type2"><div class="apply-admission-inner">
<h2 class="title text-center"><span>Apply for admission</span></h2>
</div></div>
<div class="form-apply"><div class="section-overlay183251"></div>
<form action="#" class="apply-now" onsubmit="return false;">
<ul>
<li><input type="text" placeholder="Name"></li>
<li><input type="email" placeholder="Email"></li>
<li><input type="tel" placeholder="Phone"></li>
</ul>
<div class="btn-50 hv-border text-center"><a href="admission/" class="btn bg-clff5f60">Apply now</a></div>
</form>
</div>
</div>
</div>
</div>
</section><!-- flat-benefit -->'''

    # --- 7. upcoming events ---------------------------------------------
    ev=''; evimgs=[]
    for i,(d,t) in enumerate(events):
        thumb,_=_thumb_and_excerpt(d)
        evimgs.append(thumb)
        c=EVENT_COLORS[i]
        ev+=f'''<div class="content-event">
<div class="entry-info clearfix">
<div class="entry-title"><a href="{d}/" class="cl-{c}">{html.escape(t)}</a></div>
<div class="entry-meta"><ul>
<li class="date clearfix"><span class="icon-event icon-icons8-planner-100"></span><span class="detail-event">{published_date(d)[0] or 'Academic year 2026'}</span></li>
<li class="location clearfix"><span class="icon-event icon-icons8-marker-100"></span><span class="detail-event">AJAS Campus, Perinthalmanna</span></li>
</ul></div>
</div>
<div class="entry-number number-{['one','two','three'][i]}"><span class="cl-{c}">{i+1}</span></div>
</div>'''
    bgc=['bg-cl7ecc88','bg-cl3f4c99','bg-clff5f60']
    im=lambda n:(f'<img src="{evimgs[n]}" alt="event">' if n<len(evimgs) and evimgs[n] else '<div class="mig-noimg"></div>')
    eventsec=f'''<section class="flat-event flat-event-style1 clearfix ajas-events">
<div class="container-fluid">
<div class="col-left"><div class="content-event-style1 themesflat-content-box" data-padding="13.7% 1.2% 0% 0%" data-mobipadding="0% 0% 0% 0%" data-smobipadding="0% 0% 0% 0%">
<div class="title-section"><div class="flat-title larger heading-type3">Upcoming events</div></div>
<div class="content-event-list">{ev}</div>
<div class="btn-about pd-top15"><a href="event/" class="btn-box-shadow">All events</a></div>
</div></div>
<div class="col-right"><div class="images-list themesflat-content-box" data-padding="0% 0% 0% 15.1%" data-mobipadding="0% 0% 0% 0%" data-smobipadding="0% 0% 0% 0%">
<div class="images-list-1">
<div class="img-event">{im(0)}<span class="number {bgc[0]}">1</span></div>
<div class="img-event">{im(1)}<span class="number {bgc[1]}">2</span></div>
</div>
<div class="images-list-2">
<div class="img-event">{im(2)}<span class="number {bgc[2]}">3</span></div>
</div>
</div></div>
</div>
</section><!-- flat-event -->'''

    # --- 8. our success (counters) --------------------------------------
    c=COUNTERS
    counters=f'''<div class="flat-about pd-about clearfix ajas-success"><div class="container"><div class="row">
<div class="col-lg-6">
<div class="textbox-about"><div class="title-section">
<div class="flat-title medium heading-type18">Our success</div>
</div>
<div class="textbox-content"><div class="about-introduce">
<p>More than twelve thousand students have studied at Al Jamia over the years &mdash; among them prominent Islamic scholars, writers, academicians and media professionals rendering commendable service across India and abroad.</p>
<p>Established in 2010, the college was founded to uplift educationally developing communities and mould graduates who are professionally competent, socially responsible and morally sound.</p>
<div class="btn-about"><a href="overview/" class="btn-box-shadow">About the college</a></div>
</div></div>
</div>
</div>
<div class="col-lg-6"><div class="iconbox-about"><div class="iconbox-about-wrap clearfix">
<div class="list-1">
<div class="iconbox iconbox-students"><div class="counter"><div class="content-counter">
<div class="numb-count {c[0][2]}" data-from="0" data-to="{c[0][0]}" data-speed="2000" data-inviewport="yes">{c[0][0]}</div>
<div class="name-count">{c[0][1]}</div></div></div></div>
<div class="iconbox iconbox-teacher"><div class="counter"><div class="content-counter">
<div class="numb-count {c[2][2]}" data-from="0" data-to="{c[2][0]}" data-speed="2000" data-inviewport="yes">{c[2][0]}</div>
<div class="name-count">{c[2][1]}</div></div></div></div>
</div>
<div class="list-2">
<div class="iconbox iconbox-courses"><div class="counter"><div class="content-counter">
<div class="numb-count {c[1][2]}" data-from="0" data-to="{c[1][0]}" data-speed="2000" data-inviewport="yes">{c[1][0]}</div>
<div class="name-count">{c[1][1]}</div></div></div></div>
<div class="iconbox iconbox-award"><div class="counter"><div class="content-counter">
<div class="numb-count {c[3][2]}" data-from="0" data-to="{c[3][0]}" data-speed="2000" data-inviewport="yes">{c[3][0]}</div>
<div class="name-count">{c[3][1]}</div></div></div></div>
</div>
</div></div></div>
</div></div></div><!-- flat-about -->'''

    # --- 9. testimonials -------------------------------------------------
    avatars=''.join(f'<li class="avatar"><img src="{u}" alt="{html.escape(n)}"></li>' for u,n,r,q in TESTIMONIALS)
    quotes=''.join(f'''<li>
<span class="icon-quote icon-icons8-get-quote-filled-100"></span>
<p class="speech">&ldquo; {html.escape(q)}</p>
<div class="name">{html.escape(n)}</div>
<div class="ajas-testi-role">{html.escape(r)}</div>
</li>''' for u,n,r,q in TESTIMONIALS)
    testimonial=f'''<section class="slider testimonial-flexslider testimonial-style1 equalize sm-equalize-auto clearfix ajas-testimonials">
<div class="wrap-info themesflat-content-box" data-padding="0% 0% 0% 10%" data-mobipadding="0% 0% 0% 0%" data-smobipadding="0% 0% 0% 0%">
<div id="carousel-testimonial" class="flexslider"><ul class="slides translate-none">{avatars}</ul></div>
</div>
<div class="wrap-quote themesflat-content-box" data-padding="10.47% 14.1% 0% 0%" data-mobipadding="90px 15px 80px 15px" data-smobipadding="90px 15px 80px 15px">
<div id="slider-testimonial" class="flexslider"><ul class="slides client-info">{quotes}</ul></div>
</div>
</section><!-- testimonial -->'''

    # --- 10. campus news carousel ---------------------------------------
    posts=''
    for d,t in news:
        thumb,ex=_thumb_and_excerpt(d)
        pic=(f'<img src="{thumb}" alt="{html.escape(t)}">' if thumb else '<div class="mig-noimg"></div>')
        posts+=f'''<article class="post post-style1 post-bg">
<div class="bg clearfix">
<div class="position cl-fe5e5f lt-sp4">NEWS</div>
<div class="featured-post">{pic}</div>
</div>
<div class="post-content clearfix">
<div class="entry-info cleafix"><div class="post-title"><h5><a href="{d}/" class="lt-sp04">{html.escape(t)}</a></h5></div></div>
{f'<div class="ajas-post-date">{published_date(d)[0]}</div>' if published_date(d)[0] else ''}
<div class="post-link"><a href="{d}/">Read Now</a></div>
</div>
</article>'''
    blog=f'''<section class="latest-blog cl-dots1 latest-blog-type1 latest-blog-style1 ajas-news">
<div class="container">
<div class="title-section"><div class="flat-title small heading-type4">Campus news</div></div>
<div class="flat-carousel-box data-effect clearfix" data-gap="30" data-column="2" data-column2="2" data-column3="1" data-column4="1" data-dots="true" data-auto="false" data-nav="false">
<div class="owl-carousel">{posts}</div>
</div>
<div class="text-center pd-top30"><a href="college-news/" class="btn bg-clff5f60 ajas-apply-btn">More news</a></div>
</div>
</section><!-- latest-blog -->'''

    # --- 11. quick links (parallax) --------------------------------------
    ql=''.join(f'<li><i class="fa {i}" aria-hidden="true"></i>'
               f'<a href="{h}"{" target=\"_blank\"" if ext else ""}>{html.escape(t)}</a></li>'
               for i,t,h,ext in QUICK_LINKS)
    quicklink=f'''<section class="quick-link quick-link-style1 parallax parallax2 ajas-quicklink">
<div class="section-overlay"></div>
<div class="container"><div class="row">
<div class="col-lg-7">
<div class="wrap-link-left">
<div class="caption lt-sp275">Admissions 2026 &ndash; 27 are open</div>
<div class="heading-lf lt-sp03">Ready to get started?</div>
<p>Al Jamia Arts and Science College is a resourceful destination for higher studies in the region &mdash; affiliated to the University of Calicut, recognised by the Government of Kerala and holding minority status. Apply online or visit the campus at Poopalam, Perinthalmanna.</p>
<div class="btn-apply-link"><ul>
<li><a href="admission/" class="btn btn-apply bg-clff5f60">Apply now</a></li>
<li><a href="contact/" class="btn btn-request lt-sp06">Contact us</a></li>
</ul></div>
</div>
</div>
<div class="col-lg-5"><div class="wrap-link-right">
<div class="heading-rg"><span>Quick Link</span></div>
<ul class="info-quick-link">{ql}</ul>
</div></div>
</div></div>
</section><!-- quick-link -->'''

    body=(hero+partners+introduce+programmes+services+benefit+eventsec+
          counters+testimonial+blog+quicklink)
    desc=('Al Jamia Arts and Science College, Perinthalmanna — established 2010, affiliated to the '
          'University of Calicut. UG (Honours) and PG programmes in Arts, Science, Commerce and Computing.')
    return home_shell(body,desc)
# ---------------- main ----------------
if __name__=='__main__':
    # asset copy
    if not ONLY:
        for sub in ['stylesheet','javascript','images','icon','fonts']:
            src=os.path.join(EDU,sub); dst=os.path.join(OUT,sub)
            if os.path.isdir(src) and not os.path.isdir(dst): shutil.copytree(src,dst)
        up_src=os.path.join(SRC,'wp-content/uploads'); up_dst=os.path.join(OUT,'assets/uploads')
        if os.path.isdir(up_src) and not os.path.isdir(up_dst):
            shutil.copytree(up_src,up_dst)
        # JetEngine download endpoints are saved by wget under their query string
        dl=os.path.join(OUT,'assets','downloads'); os.makedirs(dl,exist_ok=True)
        for f in glob.glob(os.path.join(SRC,'index.html@jet_download=*')):
            h=f.rsplit('jet_download=',1)[1]
            if re.fullmatch(r'[0-9a-f]+',h): shutil.copyfile(f,os.path.join(dl,h+'.pdf'))
        open(os.path.join(OUT,'assets','migrate.css'),'w').write(MIGRATE_CSS)
    built=[]; EMPTY=[]; IMGONLY=[]
    childF=[(d,t) for d,t in PAGES if d.startswith('faculties/') and d!='faculties']
    childD=[(d,t) for d,t in PAGES if d.startswith('departments/') and d!='departments']
    childN=[(d,t) for d,t in PAGES if d.startswith('college-news/') and d!='college-news']
    childE=[(d,t) for d,t in PAGES if d.startswith('event/') and d!='event']
    for d,t in PAGES:
        if ONLY and d not in ONLY: continue
        newpath='index.html' if d=='.' else d+'/index.html'
        try:
            if d=='.':
                s=build_home()
            elif d=='student-life':
                s=build_student_life(newpath)
            elif d=='add-on-certificate-courses':
                s=build_hub('Add-On / Certificate Courses','add-on-certificate-courses',
                    'Alongside the degree, students take certificate and skill programmes run with '
                    'ASAP Kerala, Keltron, G-Tec and the national MOOC platforms — widening what a '
                    'graduate leaves Al Jamia with.',
                    CERT_COURSES, newpath)
            elif d=='faculties':
                s=build_listing('faculties',childF,'Faculties',newpath,kind='team')
            elif d=='departments':
                s=build_listing('departments',childD,'Departments',newpath,kind='course')
            elif d=='college-news':
                s=build_listing('college-news',childN,'News',newpath,kind='blog')
            elif d=='event':
                s=build_listing('event',childE,'Events',newpath,kind='blog')
            else:
                content,imgs,raw=extract_content(os.path.join(SRC,d,'index.html'))
                cr=crumbs_for(d,t)
                plain=re.sub(r'<[^>]+>','',content).strip()
                if len(plain)<200:
                    loops=extract_loop_items(os.path.join(SRC,d,'index.html'))
                    if loops:
                        content=(f'<h2>{html.escape(t)}</h2>' +
                                 ''.join(f'<h3>{html.escape(r["title"])}</h3>'
                                         f'<p>{html.escape(r.get("body",""))}</p>' for r in loops))
                        plain=re.sub(r'<[^>]+>','',content).strip()
                if len(plain)<40 and not imgs:
                    region=collect_all_images(os.path.join(SRC,d,'index.html'))
                    if region:
                        IMGONLY.append(d)
                        stack=''.join(f'<p><img src="%%P%%{im}" alt="{html.escape(t)}" class="img-fluid"></p>' for im in region if os.path.exists(os.path.join(OUT,im)))
                        content=(f'<h1>{html.escape(t)}</h1>' if not content else content)+stack
                    else:
                        EMPTY.append(d)
                        content=f'<h1>{html.escape(t)}</h1>\n<p class="mig-empty-note">The original page had no extractable body content in the archived copy. Content to be added.</p>'
                P=prefix(newpath)
                # drop a leading heading that just repeats the page title (dup of banner)
                content=re.sub(r'^\s*<h[1-6]>\s*'+re.escape(html.escape(t))+r'\s*</h[1-6]>\s*','',content,count=1,flags=re.I)
                if d not in GALL:
                    content=structure_content(content)
                    content=structure_programmes(content)
                    content=structure_downloads(content)
                if d.startswith('faculties/') and not first_img(content):
                    ph=pick_photo(raw)
                    if ph: content=f'<div class="fac-photo"><img src="{P}{ph}" alt="{html.escape(t)}" class="img-fluid"></div>\n'+content
                if d=='contact' and 'google.com/maps' not in content:
                    content+='<div class="mig-map embed-wrap"><iframe src="https://www.google.com/maps?q=Al+Jamia+Arts+and+Science+College+Perinthalmanna&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>'
                # staff rosters: rebuild from the JetEngine listing markup
                roster=[] if (d.startswith('faculties/') or d in PEOPLE) else \
                       extract_people(os.path.join(SRC,d,'index.html'))
                # a roster is worth building once most entries carry a photo,
                # but people without one are still listed rather than dropped
                is_roster=sum(1 for r in roster if r[0])>=3
                if is_roster:
                    # keep only real prose above the grid — the leftover headings
                    # are the roster's own name/role labels, now inside the cards
                    names={n.lower() for _,n,_ in roster}
                    names|={r.lower() for _,_,r in roster if r}
                    intro=re.sub(r'<p>.*?</p>','',content,flags=re.S)
                    intro=re.sub(r'<img[^>]*>','',intro)
                    def _drop(m):
                        txt=re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',m.group(2)))).strip()
                        return '' if (txt.lower() in names or len(txt)<26) else m.group(0)
                    intro=re.sub(r'<(h[1-6])[^>]*>(.*?)</\1>',_drop,intro,flags=re.S)
                    intro=intro if re.sub('<[^>]+>','',intro).strip() else ''
                    content=intro+people_grid(roster,P)
                textlen=len(re.sub(r'<[^>]+>','',content).strip())
                is_person=d.startswith('faculties/') or d in PEOPLE
                if d in FORMS and 'prog-cards' in content:
                    body=wrap_wide_form(content,form_block(FORMDEF[d]),d,P)
                elif d in FORMS:
                    body=wrap_form(content,form_block(FORMDEF[d]),d,P)
                elif d in GALL:
                    gimg=imgs if len(imgs)>=4 else collect_all_images(os.path.join(SRC,d,'index.html'))
                    body=wrap_gallery(content,gimg,d,P)
                elif is_roster:
                    body=(f'<div class="blog-single content-blog wide-page roster-page">'
                          f'<div class="container"><div class="migrate-content">{content}</div>'
                          f'</div></div>')
                elif is_person:
                    body=wrap_profile(content,d,P,t)
                elif textlen<1400:
                    body=wrap_narrow(content,d,P)
                else:
                    body=wrap_textpage(content,d,P)
                s=shell(t,cr,body,newpath)
            write_page(newpath,s); built.append(d)
        except Exception as e:
            print('ERR',d,repr(e))
    # Section landing pages the old site never had — its mega-menu was the only
    # way in. Built from the child pages so every section has a real index.
    for slug,title,pref in [('clubs--cells','Clubs &amp; Cells','clubs--cells/'),
                            ('labs','Laboratories','labs/')]:
        if ONLY and slug not in ONLY: continue
        kids=[(x,y) for x,y in PAGES if x.startswith(pref)]
        if not kids: continue
        newpath=slug+'/index.html'
        try:
            write_page(newpath,build_listing(slug,kids,title,newpath,kind='course'))
            built.append(slug)
        except Exception as e:
            print('ERR',slug,repr(e))
    print('BUILT',len(built),'pages')
    print('IMAGE-ONLY pages recovered ('+str(len(IMGONLY))+'):',', '.join(IMGONLY))
    print('EMPTY/FLAGGED pages ('+str(len(EMPTY))+'):',', '.join(EMPTY))
