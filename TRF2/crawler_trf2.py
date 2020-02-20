import selenium
import time
import os
import glob
import urllib.request
import matplotlib.pyplot as plt
import cv2
import numpy as np
import pytesseract
import argparse

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from itertools import product
from string import ascii_lowercase
from PIL import Image

SCREEN_ON = False

# Utility functions
def init_webdriver(path_to_driver=None, use_window=False):
    """
    Creates a webdriver suited for the task.

    Keyword arguments:
    path_to_driver -- path to geckodriver (firefox) driver executable. Leave None if the driver is set in path.
    use_window -- if True, a window of the firefox webdriver will be opened
    """
    fp = webdriver.FirefoxProfile()
    # "Brute force" solution to download every mime-type without asking
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir", os.path.join(os.getcwd(), 'tmp'))
    fp.set_preference("browser.download.defaultFolder", os.path.join(os.getcwd(), 'tmp'))
    fp.set_preference("pdfjs.disabled", True)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.hzn-3d-crossword;video/3gpp;video/3gpp2;application/vnd.mseq;application/vnd.3m.post-it-notes;application/vnd.3gpp.pic-bw-large;application/vnd.3gpp.pic-bw-small;application/vnd.3gpp.pic-bw-var;application/vnd.3gp2.tcap;application/x-7z-compressed;application/x-abiword;application/x-ace-compressed;application/vnd.americandynamics.acc;application/vnd.acucobol;application/vnd.acucorp;audio/adpcm;application/x-authorware-bin;application/x-athorware-map;application/x-authorware-seg;application/vnd.adobe.air-application-installer-package+zip;application/x-shockwave-flash;application/vnd.adobe.fxp;application/pdf;application/vnd.cups-ppd;application/x-director;applicaion/vnd.adobe.xdp+xml;application/vnd.adobe.xfdf;audio/x-aac;application/vnd.ahead.space;application/vnd.airzip.filesecure.azf;application/vnd.airzip.filesecure.azs;application/vnd.amazon.ebook;application/vnd.amiga.ami;applicatin/andrew-inset;application/vnd.android.package-archive;application/vnd.anser-web-certificate-issue-initiation;application/vnd.anser-web-funds-transfer-initiation;application/vnd.antix.game-component;application/vnd.apple.installe+xml;application/applixware;application/vnd.hhe.lesson-player;application/vnd.aristanetworks.swi;text/x-asm;application/atomcat+xml;application/atomsvc+xml;application/atom+xml;application/pkix-attr-cert;audio/x-aiff;video/x-msvieo;application/vnd.audiograph;image/vnd.dxf;model/vnd.dwf;text/plain-bas;application/x-bcpio;application/octet-stream;image/bmp;application/x-bittorrent;application/vnd.rim.cod;application/vnd.blueice.multipass;application/vnd.bm;application/x-sh;image/prs.btif;application/vnd.businessobjects;application/x-bzip;application/x-bzip2;application/x-csh;text/x-c;application/vnd.chemdraw+xml;text/css;chemical/x-cdx;chemical/x-cml;chemical/x-csml;application/vn.contact.cmsg;application/vnd.claymore;application/vnd.clonk.c4group;image/vnd.dvb.subtitle;application/cdmi-capability;application/cdmi-container;application/cdmi-domain;application/cdmi-object;application/cdmi-queue;applicationvnd.cluetrust.cartomobile-config;application/vnd.cluetrust.cartomobile-config-pkg;image/x-cmu-raster;model/vnd.collada+xml;text/csv;application/mac-compactpro;application/vnd.wap.wmlc;image/cgm;x-conference/x-cooltalk;image/x-cmx;application/vnd.xara;application/vnd.cosmocaller;application/x-cpio;application/vnd.crick.clicker;application/vnd.crick.clicker.keyboard;application/vnd.crick.clicker.palette;application/vnd.crick.clicker.template;application/vn.crick.clicker.wordbank;application/vnd.criticaltools.wbs+xml;application/vnd.rig.cryptonote;chemical/x-cif;chemical/x-cmdf;application/cu-seeme;application/prs.cww;text/vnd.curl;text/vnd.curl.dcurl;text/vnd.curl.mcurl;text/vnd.crl.scurl;application/vnd.curl.car;application/vnd.curl.pcurl;application/vnd.yellowriver-custom-menu;application/dssc+der;application/dssc+xml;application/x-debian-package;audio/vnd.dece.audio;image/vnd.dece.graphic;video/vnd.dec.hd;video/vnd.dece.mobile;video/vnd.uvvu.mp4;video/vnd.dece.pd;video/vnd.dece.sd;video/vnd.dece.video;application/x-dvi;application/vnd.fdsn.seed;application/x-dtbook+xml;application/x-dtbresource+xml;application/vnd.dvb.ait;applcation/vnd.dvb.service;audio/vnd.digital-winds;image/vnd.djvu;application/xml-dtd;application/vnd.dolby.mlp;application/x-doom;application/vnd.dpgraph;audio/vnd.dra;application/vnd.dreamfactory;audio/vnd.dts;audio/vnd.dts.hd;imag/vnd.dwg;application/vnd.dynageo;application/ecmascript;application/vnd.ecowin.chart;image/vnd.fujixerox.edmics-mmr;image/vnd.fujixerox.edmics-rlc;application/exi;application/vnd.proteus.magazine;application/epub+zip;message/rfc82;application/vnd.enliven;application/vnd.is-xpr;image/vnd.xiff;application/vnd.xfdl;application/emma+xml;application/vnd.ezpix-album;application/vnd.ezpix-package;image/vnd.fst;video/vnd.fvt;image/vnd.fastbidsheet;application/vn.denovo.fcselayout-link;video/x-f4v;video/x-flv;image/vnd.fpx;image/vnd.net-fpx;text/vnd.fmi.flexstor;video/x-fli;application/vnd.fluxtime.clip;application/vnd.fdf;text/x-fortran;application/vnd.mif;application/vnd.framemaker;imae/x-freehand;application/vnd.fsc.weblaunch;application/vnd.frogans.fnc;application/vnd.frogans.ltf;application/vnd.fujixerox.ddd;application/vnd.fujixerox.docuworks;application/vnd.fujixerox.docuworks.binder;application/vnd.fujitu.oasys;application/vnd.fujitsu.oasys2;application/vnd.fujitsu.oasys3;application/vnd.fujitsu.oasysgp;application/vnd.fujitsu.oasysprs;application/x-futuresplash;application/vnd.fuzzysheet;image/g3fax;application/vnd.gmx;model/vn.gtw;application/vnd.genomatix.tuxedo;application/vnd.geogebra.file;application/vnd.geogebra.tool;model/vnd.gdl;application/vnd.geometry-explorer;application/vnd.geonext;application/vnd.geoplan;application/vnd.geospace;applicatio/x-font-ghostscript;application/x-font-bdf;application/x-gtar;application/x-texinfo;application/x-gnumeric;application/vnd.google-earth.kml+xml;application/vnd.google-earth.kmz;application/vnd.grafeq;image/gif;text/vnd.graphviz;aplication/vnd.groove-account;application/vnd.groove-help;application/vnd.groove-identity-message;application/vnd.groove-injector;application/vnd.groove-tool-message;application/vnd.groove-tool-template;application/vnd.groove-vcar;video/h261;video/h263;video/h264;application/vnd.hp-hpid;application/vnd.hp-hps;application/x-hdf;audio/vnd.rip;application/vnd.hbci;application/vnd.hp-jlyt;application/vnd.hp-pcl;application/vnd.hp-hpgl;application/vnd.yamaha.h-script;application/vnd.yamaha.hv-dic;application/vnd.yamaha.hv-voice;application/vnd.hydrostatix.sof-data;application/hyperstudio;application/vnd.hal+xml;text/html;application/vnd.ibm.rights-management;application/vnd.ibm.securecontainer;text/calendar;application/vnd.iccprofile;image/x-icon;application/vnd.igloader;image/ief;application/vnd.immervision-ivp;application/vnd.immervision-ivu;application/reginfo+xml;text/vnd.in3d.3dml;text/vnd.in3d.spot;mode/iges;application/vnd.intergeo;application/vnd.cinderella;application/vnd.intercon.formnet;application/vnd.isac.fcs;application/ipfix;application/pkix-cert;application/pkixcmp;application/pkix-crl;application/pkix-pkipath;applicaion/vnd.insors.igm;application/vnd.ipunplugged.rcprofile;application/vnd.irepository.package+xml;text/vnd.sun.j2me.app-descriptor;application/java-archive;application/java-vm;application/x-java-jnlp-file;application/java-serializd-object;text/x-java-source,java;application/javascript;application/json;application/vnd.joost.joda-archive;video/jpm;image/jpeg;video/jpeg;application/vnd.kahootz;application/vnd.chipnuts.karaoke-mmd;application/vnd.kde.karbon;aplication/vnd.kde.kchart;application/vnd.kde.kformula;application/vnd.kde.kivio;application/vnd.kde.kontour;application/vnd.kde.kpresenter;application/vnd.kde.kspread;application/vnd.kde.kword;application/vnd.kenameaapp;applicatin/vnd.kidspiration;application/vnd.kinar;application/vnd.kodak-descriptor;application/vnd.las.las+xml;application/x-latex;application/vnd.llamagraphics.life-balance.desktop;application/vnd.llamagraphics.life-balance.exchange+xml;application/vnd.jam;application/vnd.lotus-1-2-3;application/vnd.lotus-approach;application/vnd.lotus-freelance;application/vnd.lotus-notes;application/vnd.lotus-organizer;application/vnd.lotus-screencam;application/vnd.lotus-wordro;audio/vnd.lucent.voice;audio/x-mpegurl;video/x-m4v;application/mac-binhex40;application/vnd.macports.portpkg;application/vnd.osgeo.mapguide.package;application/marc;application/marcxml+xml;application/mxf;application/vnd.wolfrm.player;application/mathematica;application/mathml+xml;application/mbox;application/vnd.medcalcdata;application/mediaservercontrol+xml;application/vnd.mediastation.cdkey;application/vnd.mfer;application/vnd.mfmp;model/mesh;appliation/mads+xml;application/mets+xml;application/mods+xml;application/metalink4+xml;application/vnd.ms-powerpoint.template.macroenabled.12;application/vnd.ms-word.document.macroenabled.12;application/vnd.ms-word.template.macroenabed.12;application/vnd.mcd;application/vnd.micrografx.flo;application/vnd.micrografx.igx;application/vnd.eszigno3+xml;application/x-msaccess;video/x-ms-asf;application/x-msdownload;application/vnd.ms-artgalry;application/vnd.ms-ca-compressed;application/vnd.ms-ims;application/x-ms-application;application/x-msclip;image/vnd.ms-modi;application/vnd.ms-fontobject;application/vnd.ms-excel;application/vnd.ms-excel.addin.macroenabled.12;application/vnd.ms-excelsheet.binary.macroenabled.12;application/vnd.ms-excel.template.macroenabled.12;application/vnd.ms-excel.sheet.macroenabled.12;application/vnd.ms-htmlhelp;application/x-mscardfile;application/vnd.ms-lrm;application/x-msmediaview;aplication/x-msmoney;application/vnd.openxmlformats-officedocument.presentationml.presentation;application/vnd.openxmlformats-officedocument.presentationml.slide;application/vnd.openxmlformats-officedocument.presentationml.slideshw;application/vnd.openxmlformats-officedocument.presentationml.template;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;application/vnd.openxmlformats-officedocument.spreadsheetml.template;application/vnd.openxmformats-officedocument.wordprocessingml.document;application/vnd.openxmlformats-officedocument.wordprocessingml.template;application/x-msbinder;application/vnd.ms-officetheme;application/onenote;audio/vnd.ms-playready.media.pya;vdeo/vnd.ms-playready.media.pyv;application/vnd.ms-powerpoint;application/vnd.ms-powerpoint.addin.macroenabled.12;application/vnd.ms-powerpoint.slide.macroenabled.12;application/vnd.ms-powerpoint.presentation.macroenabled.12;appliation/vnd.ms-powerpoint.slideshow.macroenabled.12;application/vnd.ms-project;application/x-mspublisher;application/x-msschedule;application/x-silverlight-app;application/vnd.ms-pki.stl;application/vnd.ms-pki.seccat;application/vn.visio;video/x-ms-wm;audio/x-ms-wma;audio/x-ms-wax;video/x-ms-wmx;application/x-ms-wmd;application/vnd.ms-wpl;application/x-ms-wmz;video/x-ms-wmv;video/x-ms-wvx;application/x-msmetafile;application/x-msterminal;application/msword;application/x-mswrite;application/vnd.ms-works;application/x-ms-xbap;application/vnd.ms-xpsdocument;audio/midi;application/vnd.ibm.minipay;application/vnd.ibm.modcap;application/vnd.jcp.javame.midlet-rms;application/vnd.tmobile-ivetv;application/x-mobipocket-ebook;application/vnd.mobius.mbk;application/vnd.mobius.dis;application/vnd.mobius.plc;application/vnd.mobius.mqy;application/vnd.mobius.msl;application/vnd.mobius.txf;application/vnd.mobius.daf;tex/vnd.fly;application/vnd.mophun.certificate;application/vnd.mophun.application;video/mj2;audio/mpeg;video/vnd.mpegurl;video/mpeg;application/mp21;audio/mp4;video/mp4;application/mp4;application/vnd.apple.mpegurl;application/vnd.msician;application/vnd.muvee.style;application/xv+xml;application/vnd.nokia.n-gage.data;application/vnd.nokia.n-gage.symbian.install;application/x-dtbncx+xml;application/x-netcdf;application/vnd.neurolanguage.nlu;application/vnd.na;application/vnd.noblenet-directory;application/vnd.noblenet-sealer;application/vnd.noblenet-web;application/vnd.nokia.radio-preset;application/vnd.nokia.radio-presets;text/n3;application/vnd.novadigm.edm;application/vnd.novadim.edx;application/vnd.novadigm.ext;application/vnd.flographit;audio/vnd.nuera.ecelp4800;audio/vnd.nuera.ecelp7470;audio/vnd.nuera.ecelp9600;application/oda;application/ogg;audio/ogg;video/ogg;application/vnd.oma.dd2+xml;applicatin/vnd.oasis.opendocument.text-web;application/oebps-package+xml;application/vnd.intu.qbo;application/vnd.openofficeorg.extension;application/vnd.yamaha.openscoreformat;audio/webm;video/webm;application/vnd.oasis.opendocument.char;application/vnd.oasis.opendocument.chart-template;application/vnd.oasis.opendocument.database;application/vnd.oasis.opendocument.formula;application/vnd.oasis.opendocument.formula-template;application/vnd.oasis.opendocument.grapics;application/vnd.oasis.opendocument.graphics-template;application/vnd.oasis.opendocument.image;application/vnd.oasis.opendocument.image-template;application/vnd.oasis.opendocument.presentation;application/vnd.oasis.opendocumen.presentation-template;application/vnd.oasis.opendocument.spreadsheet;application/vnd.oasis.opendocument.spreadsheet-template;application/vnd.oasis.opendocument.text;application/vnd.oasis.opendocument.text-master;application/vnd.asis.opendocument.text-template;image/ktx;application/vnd.sun.xml.calc;application/vnd.sun.xml.calc.template;application/vnd.sun.xml.draw;application/vnd.sun.xml.draw.template;application/vnd.sun.xml.impress;application/vnd.sun.xl.impress.template;application/vnd.sun.xml.math;application/vnd.sun.xml.writer;application/vnd.sun.xml.writer.global;application/vnd.sun.xml.writer.template;application/x-font-otf;application/vnd.yamaha.openscoreformat.osfpvg+xml;application/vnd.osgi.dp;application/vnd.palm;text/x-pascal;application/vnd.pawaafile;application/vnd.hp-pclxl;application/vnd.picsel;image/x-pcx;image/vnd.adobe.photoshop;application/pics-rules;image/x-pict;application/x-chat;aplication/pkcs10;application/x-pkcs12;application/pkcs7-mime;application/pkcs7-signature;application/x-pkcs7-certreqresp;application/x-pkcs7-certificates;application/pkcs8;application/vnd.pocketlearn;image/x-portable-anymap;image/-portable-bitmap;application/x-font-pcf;application/font-tdpfr;application/x-chess-pgn;image/x-portable-graymap;image/png;image/x-portable-pixmap;application/pskc+xml;application/vnd.ctc-posml;application/postscript;application/xfont-type1;application/vnd.powerbuilder6;application/pgp-encrypted;application/pgp-signature;application/vnd.previewsystems.box;application/vnd.pvi.ptid1;application/pls+xml;application/vnd.pg.format;application/vnd.pg.osasli;tex/prs.lines.tag;application/x-font-linux-psf;application/vnd.publishare-delta-tree;application/vnd.pmi.widget;application/vnd.quark.quarkxpress;application/vnd.epson.esf;application/vnd.epson.msf;application/vnd.epson.ssf;applicaton/vnd.epson.quickanime;application/vnd.intu.qfx;video/quicktime;application/x-rar-compressed;audio/x-pn-realaudio;audio/x-pn-realaudio-plugin;application/rsd+xml;application/vnd.rn-realmedia;application/vnd.realvnc.bed;applicatin/vnd.recordare.musicxml;application/vnd.recordare.musicxml+xml;application/relax-ng-compact-syntax;application/vnd.data-vision.rdz;application/rdf+xml;application/vnd.cloanto.rp9;application/vnd.jisp;application/rtf;text/richtex;application/vnd.route66.link66+xml;application/rss+xml;application/shf+xml;application/vnd.sailingtracker.track;image/svg+xml;application/vnd.sus-calendar;application/sru+xml;application/set-payment-initiation;application/set-reistration-initiation;application/vnd.sema;application/vnd.semd;application/vnd.semf;application/vnd.seemail;application/x-font-snf;application/scvp-vp-request;application/scvp-vp-response;application/scvp-cv-request;application/svp-cv-response;application/sdp;text/x-setext;video/x-sgi-movie;application/vnd.shana.informed.formdata;application/vnd.shana.informed.formtemplate;application/vnd.shana.informed.interchange;application/vnd.shana.informed.package;application/thraud+xml;application/x-shar;image/x-rgb;application/vnd.epson.salt;application/vnd.accpac.simply.aso;application/vnd.accpac.simply.imp;application/vnd.simtech-mindmapper;application/vnd.commonspace;application/vnd.ymaha.smaf-audio;application/vnd.smaf;application/vnd.yamaha.smaf-phrase;application/vnd.smart.teacher;application/vnd.svd;application/sparql-query;application/sparql-results+xml;application/srgs;application/srgs+xml;application/sml+xml;application/vnd.koan;text/sgml;application/vnd.stardivision.calc;application/vnd.stardivision.draw;application/vnd.stardivision.impress;application/vnd.stardivision.math;application/vnd.stardivision.writer;application/vnd.tardivision.writer-global;application/vnd.stepmania.stepchart;application/x-stuffit;application/x-stuffitx;application/vnd.solent.sdkm+xml;application/vnd.olpc-sugar;audio/basic;application/vnd.wqd;application/vnd.symbian.install;application/smil+xml;application/vnd.syncml+xml;application/vnd.syncml.dm+wbxml;application/vnd.syncml.dm+xml;application/x-sv4cpio;application/x-sv4crc;application/sbml+xml;text/tab-separated-values;image/tiff;application/vnd.to.intent-module-archive;application/x-tar;application/x-tcl;application/x-tex;application/x-tex-tfm;application/tei+xml;text/plain;application/vnd.spotfire.dxp;application/vnd.spotfire.sfs;application/timestamped-data;applicationvnd.trid.tpt;application/vnd.triscape.mxs;text/troff;application/vnd.trueapp;application/x-font-ttf;text/turtle;application/vnd.umajin;application/vnd.uoml+xml;application/vnd.unity;application/vnd.ufdl;text/uri-list;application/nd.uiq.theme;application/x-ustar;text/x-uuencode;text/x-vcalendar;text/x-vcard;application/x-cdlink;application/vnd.vsf;model/vrml;application/vnd.vcx;model/vnd.mts;model/vnd.vtu;application/vnd.visionary;video/vnd.vivo;applicatin/ccxml+xml,;application/voicexml+xml;application/x-wais-source;application/vnd.wap.wbxml;image/vnd.wap.wbmp;audio/x-wav;application/davmount+xml;application/x-font-woff;application/wspolicy+xml;image/webp;application/vnd.webturb;application/widget;application/winhlp;text/vnd.wap.wml;text/vnd.wap.wmlscript;application/vnd.wap.wmlscriptc;application/vnd.wordperfect;application/vnd.wt.stf;application/wsdl+xml;image/x-xbitmap;image/x-xpixmap;image/x-xwindowump;application/x-x509-ca-cert;application/x-xfig;application/xhtml+xml;application/xml;application/xcap-diff+xml;application/xenc+xml;application/patch-ops-error+xml;application/resource-lists+xml;application/rls-services+xml;aplication/resource-lists-diff+xml;application/xslt+xml;application/xop+xml;application/x-xpinstall;application/xspf+xml;application/vnd.mozilla.xul+xml;chemical/x-xyz;text/yaml;application/yang;application/yin+xml;application/vnd.ul;application/zip;application/vnd.handheld-entertainment+xml;application/vnd.zzazz.deck+xml")
    options = Options()

    if not use_window:
        options.headless = True
    
    if path_to_driver is None:
        driver = webdriver.Firefox(options=options, firefox_profile=fp)
        driver.set_page_load_timeout(30)
        return driver
    else:
        driver = webdriver.Firefox(executable_path=path_to_driver, options=options, firefox_profile=fp)
        driver.set_page_load_timeout(30)
        return driver

def get_captcha(driver, download_path='captchas/captcha.png'):
    """Takes a screenshot of the current captcha page, crops the captcha and saves it."""
    element = driver.find_element_by_xpath('//*[@id="imgCaptcha"]')
    location = element.location
    size = element.size
    driver.save_screenshot('image.png')
    x = location['x']
    y = location['y']
    width = location['x'] + size['width']
    height = location['y'] + size['height']
    im = Image.open('image.png')
    im = im.crop((int(x), int(y), int(width), int(height)))
    im.save('captchas/captcha.png')
    

def guess_captcha(image_path='captchas/captcha.png'):
    """Aplies a mask to captcha image and uses OCR to guess the captcha code."""
    img = cv2.imread(image_path)
    result = img.copy()
    image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0,220,50])
    upper = np.array([0,255,255])
    mask = cv2.inRange(image, lower, upper)
    result = cv2.bitwise_and(img, img, mask=mask)
    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(result)

def save_page_source(driver, save_path, outer_folder, process_code):
    """Saves the page source HTML."""
    html = driver.find_element_by_id('divInfraAreaProcesso').get_attribute('outerHTML')
    with open('{}/{}/{}/{}_source.html'.format(save_path, outer_folder, process_code, process_code), 'w') as f:
        f.write(html)

def get_process_code(driver):
    """Obtains and processes the process code for folder creation purposes."""
    process_code = driver.find_element_by_id('txtNumProcesso').get_attribute('innerHTML')
    process_code = process_code.replace('.', '')
    process_code = process_code.replace('-', '')
    return process_code

def save_attachments(driver, save_path, outer_folder, process_code):
    """Tries to find attachments and save them."""
    list_attachments = driver.find_elements_by_class_name('infraLinkDocumento')
    if list_attachments:
        attachment_links = [entry.get_attribute('href') for entry in list_attachments]
        for j, attachment in enumerate(attachment_links):
            try: # If file, download and wait for timeout.
                 # "Fix" for https://github.com/mozilla/geckodriver/issues/1065
                driver.get(attachment)
            except: # Move downloaded file (gets latest file and moves it)
                move_from = os.path.join(os.getcwd(), 'tmp')
                list_of_files = glob.glob(move_from + "/*")
                latest_file = max(list_of_files, key=os.path.getctime)
                file_extension = latest_file.split('.')[-1]
                move_to = '{}/{}/{}/{}_attachment_{}.{}'.format(save_path, outer_folder, process_code, process_code, j, file_extension)
                os.rename(latest_file, move_to)
                print('Attachment moved')
                continue
            try:
                driver.find_element_by_tag_name('iframe')
                WebDriverWait(driver, 10).until(ec.frame_to_be_available_and_switch_to_it("conteudoIframe"))
            except:
                pass

            with open('{}/{}/{}/{}_attachment_{}.html'.format(save_path, outer_folder, process_code, process_code, j), 'w', encoding='utf-8') as f:
                f.write(driver.page_source)

def get_links(process_page, save_path='processlinks.txt'):
    """
    Generate combinations of letters and use as queries.
    Search returns CPF/CPNJ and we save the links for later use.

    Keyword arguments:
    process_page -- link with main page
    save_path -- path to text file containing links
    """
    keywords = [''.join(i) for i in product(ascii_lowercase, repeat = 2)]
    waitmore = set('aeioumy')
    driver = init_webdriver(use_window=SCREEN_ON)
    driver.get(process_page)

    i = 1
    for query in keywords:
        attempt = 0
        print(i)
        if (i % 10 == 1): # Captcha shows up each 10 queries in this case
            time.sleep(5)
            driver = break_captcha(driver, process_page)
            name_field = driver.find_element_by_id('txtStrParte')
            name_field.click()
            name_field.clear()
            name_field.send_keys('{} *'.format(query))
        else:
            name_field = driver.find_element_by_id('txtStrParte')
            name_field.click()
            name_field.clear()
            name_field.send_keys('{} *'.format(query))
        
        name_field.send_keys(Keys.RETURN)
            
        print('Query: {}'.format(query))
        i += 1    
        if not waitmore.isdisjoint(query): # Check if bigram contains troublesome characters, wait longer if so
            wait = 50
        else:
            wait = 20
        
        try:
            time.sleep(3)
            WebDriverWait(driver, wait).until(ec.presence_of_element_located((By.CLASS_NAME, 'infraCaption')))
        except:
            print('No results')
            continue
        while True: # Keep trying until page loads completely
            print("Attempt {}, waiting for navigation to load...".format(attempt))
            attempt += 1
            time.sleep(1)

            if attempt == 100:
                print("Something went wrong, page not loading. Please try again.")
                exit()
            try:
                print('Results loaded')
                entries = driver.find_elements_by_tag_name('tr')[1:] # First element is table header
                print('Entries found: {}'.format(len(entries)))
                links = [row.find_element_by_tag_name('a').get_attribute('href') for row in entries]
                print('Links obtained: {}'.format(len(links)))
                with open(save_path, 'a+') as f:
                    for link in links:
                        f.write('{}\n'.format(link))
            except NoSuchElementException:
                print("NoSuchElementException")
                continue
            except StaleElementReferenceException:
                print("StaleElementReferenceException")
                continue
            break

def explore_links(driver, process_links, save_path, subfolders=100):
    """Explore the CPF/CNPJ link and visit/save each listed process."""
    for link in process_links: 
        try:
            driver.get(link)
            # Get process code for naming purposes
            process_code = get_process_code(driver)
            outer_folder = int(process_code) % subfolders
        except:
            print('Could not find process number, moving on to next entry')
            print('Link with issue at process level (saved to failed.txt):')
            print(link)
            with open('failed.txt', 'a+') as f:
                f.write(link)
                f.write('\n')
            continue
        # Create process dir
        try:
            os.makedirs('{}/{}/{}'.format(save_path, outer_folder, process_code))
        except OSError:
            print('Creation of the directory {} failed'.format(process_code))
            break # Duplicate entry
        # Check for additional events:
        # Sometimes we'll need to click a red button in order to show the complete info
        try:
            list_all = driver.find_element(By.XPATH, "//a[@style='color:red;']")
            driver.get(list_all.get_attribute('href'))
        except:
            pass
        # Write page source
        try:
            save_page_source(driver, save_path, outer_folder, process_code)
        except:
            print('Could not find process info, moving on to next entry')
            print('Link with issue at info level (saved to failed.txt):')
            print(link)
            with open('failed.txt', 'a+') as f:
                f.write(link)
                f.write('\n')
            continue
        # Check for attached files
        save_attachments(driver, save_path, outer_folder, process_code)

def break_captcha(driver, link):
    """Keeps trying to break captcha."""
    attempt = 1
    captcha_check = True
    while captcha_check:
        print('Breaking captcha. Attempt: {}'.format(attempt))
        driver.close()
        driver.quit()
        driver = init_webdriver(use_window=SCREEN_ON)
        driver.get(link)
        attempt += 1
        get_captcha(driver)
        
        # Trying to break captcha with "informed" guesses
        captcha = guess_captcha()
        captcha = captcha.replace('l', '1')
        captcha = captcha.replace('S', '9')

        captcha_field = driver.find_element_by_id('txtCaptcha')
        captcha_field.send_keys(captcha)
        captcha_field.send_keys(Keys.RETURN)
        time.sleep(1)
        captcha_check = driver.find_elements_by_id('txtCaptcha')
    return driver

def crawler(links_path='processlinks.txt', save_path='../processos', initial_line=0):
    """Crawl through list of links and download necessary files."""
    i = 0 # Line count
    driver = init_webdriver(use_window=SCREEN_ON)
    with open('processlinks.txt', 'r') as f:
        for name in f:
            print(i, name)
            if (i % 200 == 0 and i >= initial_line): # Close the browser to avoid memory issues
                print(i)
                driver = break_captcha(driver, name)   
            if (i < initial_line): # Used to skip to a particular line in links file
                i += 1
                continue
            i += 1
            name = name.strip('\n')
            driver.get(name)
            try:
                process_entries = [entry for entry in driver.find_elements_by_tag_name('td') if entry.find_elements_by_tag_name('a')]
                process_links = [entry.find_element_by_tag_name('a').get_attribute('href') for entry in process_entries]
                # process_code = driver.find_element_by_id('txtNumProcesso').get_attribute('innerHTML')
            except:
                print('Could not find process number, moving on to next entry')
                print('Link with issue at name level (saved to failed.txt):')
                print(name)
                with open('failed.txt', 'a+') as f:
                    f.write(name)
                    f.write('\n')
                continue
            explore_links(driver, process_links, save_path)



if __name__ == "__main__":    
    parser = argparse.ArgumentParser()
    parser.add_argument('--links', dest='links', action='store_true',
            default=False, help='query for new links and save them to text file')
    parser.add_argument('--processes', dest='processes', action='store_true',
            default=True, help='follow link file to collect processes')

    args = parser.parse_args()

    process_page = 'https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica&acao_origem=&acao_retorno=processo_consulta_publica'

    if args.links:
        get_links(process_page)
    if args.processes:
        crawler(initial_line=198600)
    