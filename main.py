# news-image-20261125: one-page newspaper of Wednesday 25 November 2026.
# Stdlib only (binascii, math, os, struct, zlib). No Pillow, no numpy,
# no external font: a 5x7 bitmap font is defined below, and the PNG
# encoder is hand-written (struct + zlib + CRC). Deterministic output:
# same bytes on every run. Writes /output/entry.png (1024x1024).
import binascii
import math
import os
import struct
import zlib

W = 1024
H = 1024
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (178, 34, 34)
BLUE = (30, 64, 120)
TEAL = (0, 120, 110)
GREEN = (46, 110, 46)
ORANGE = (200, 90, 20)
PURPLE = (110, 60, 140)
GOLD = (176, 132, 0)
GREY = (120, 115, 105)
LIGHT = (232, 226, 210)
SEA = (70, 130, 170)
SKY = (190, 220, 235)

REGION_COLOR = {
    "ME": RED, "EU": BLUE, "AS": TEAL, "AF": GREEN,
    "AM": ORANGE, "OC": PURPLE, "SP": GOLD,
}
REGION_NAME = {
    "ME": "MIDDLE EAST", "EU": "EUROPE", "AS": "ASIA", "AF": "AFRICA",
    "AM": "AMERICAS", "OC": "OCEANIA", "SP": "SPACE",
}

# 5x7 bitmap font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 bits, most-significant bit first.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "*": (0x00, 0x15, 0x0E, 0x15, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "~": (0x00, 0x00, 0x09, 0x16, 0x00, 0x00, 0x00),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, w * h * 3, 3):
            self.px[i] = bg[0]
            self.px[i + 1] = bg[1]
            self.px[i + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = base + (xx - max(0, x)) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a polygon given as [(x,y), ...]
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                        xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(math.ceil(xs[k])), int(xs[k + 1]) + 1):
                    self.set(xx, y, c)

    def text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                ch2 = ch.upper()
                g = FONT.get(ch2, FONT["?"])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, s, cx, y, scale, c):
        self.text(s, cx - self.text_w(s, scale) // 2, y, scale, c)

    def wrap(self, s, max_w, scale):
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def chunk(tag, data):
    crc = binascii.crc32(tag)
    crc = binascii.crc32(data, crc)
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc & 0xFFFFFFFF)


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

# --- 50 STORIES, all reported Wednesday 25 November 2026 (UTC) ---
# fields: n, region, headline, detail, source, lon, lat, claim?
# lon/lat None = space story (no map pin; listed in the legend).
STORIES = [
    (1, "ME", "TWO TANKERS HIT MINES IN HORMUZ",
     "IRGC NAVY: SHIPS STRUCK MINES, CAUGHT FIRE; OIL SLID",
     "STRAITS TIMES", 56.0, 26.5, False),
    (2, "AM", "HUAWEI CONVICTED IN NEW YORK",
     "JURY: BANK FRAUD + TRADE-SECRET THEFT; RACKETEERING CLEARED",
     "BBC", -74.0, 40.7, False),
    (3, "AS", "ASIAN TECH SHARES TUMBLE",
     "NIKKEI -2.8%; KOSPI -6%; SOFTBANK -15% ON AI DOUBTS",
     "AL JAZEERA", 139.0, 35.7, False),
    (4, "AM", "TRUMP READIES TARIFFS ON 16 ECONOMIES",
     "CHINA, EU, JAPAN IN LINE AFTER COURT STRUCK DOWN OLD LEVIES",
     "BBC", -77.0, 38.9, False),
    (5, "ME", "HOUTHI STRIKE HITS RIYADH TOWER",
     "11 INJURED, 2 INDIAN; 2ND HIT ON PIF TOWER IN 6 DAYS",
     "CNBC", 46.7, 24.6, False),
    (6, "EU", "LEAK: ~490,000 RUSSIAN WAR DEAD",
     "LEAKED STATS DATA; SOME COUNTS TOP 700,000 WITH MISSING",
     "BBC", 37.6, 55.7, True),
    (7, "AF", "UKRAINE HITS RUSSIAN SHIPS OFF LIBYA",
     "2 LIBYAN SOLDIERS DEAD; ITALY OBJECTS, FRANCE BACKS KYIV",
     "AL JAZEERA", 20.0, 32.1, False),
    (8, "ME", "GAZA STRIKE KILLS HAMAS SECURITY CHIEF",
     "NAEEM ABU NAHEL + FAMILY AMONG 7 KILLED IN GAZA CITY",
     "BBC", 34.5, 31.5, False),
    (9, "EU", "OIL DOWN OVER 20% IN NOVEMBER",
     "BRENT BELOW $90; UK BILLS TO RISE 26% IN JANUARY",
     "OILPRICE", -0.1, 51.5, False),
    (10, "AM", "NVIDIA -4.5% AS HUANG QUESTIONED",
     "LAWMAKERS PROBE TRUMP ROLE IN CEO RETURN; PARDON AN OPTION",
     "CNBC", -122.0, 37.4, False),
    (11, "AM", "CARTAGENA SIEGE ENDS: ALL HOSTAGES FREE",
     "~20 FREED AFTER 17 HOURS; 1 GUNMAN KILLED",
     "BBC", -75.5, 10.4, False),
    (12, "SP", "PAKISTAN'S 1ST ASTRONAUT FLIES",
     "MUHAMMAD ZEESHAN ALI DOCKS AT TIANGONG; 90+ EXPERIMENTS",
     "BBC", None, None, False),
    (13, "AF", "SENEGAL AFCON TITLE RESTORED",
     "CAS OVERTURNS WALK-OFF RULING; MOROCCO VOWS TO FIGHT ON",
     "NPR", -17.4, 14.7, False),
    (14, "OC", "SOLOMONS PICK AUSTRALIA, BAR FOREIGN BASES",
     "TREATY ENDS CHINA SECURITY PACT; PM: NO MORE UNCERTAINTY",
     "RNZ", 160.0, -9.4, False),
    (15, "AM", "ABREGO GARCIA LEAVES US FOR SPAIN",
     "WRONGLY DEPORTED IN 2025; LONG LEGAL FIGHT ENDS",
     "BBC", -3.7, 40.4, False),
    (16, "EU", "RUSSIAN DRONE ENTERS POLISH AIRSPACE",
     "DAYS AFTER 3 MISSILES CAME DOWN; WARSAW WANTS US TROOPS",
     "UPI", 21.0, 52.2, False),
    (17, "EU", "MERZ: RUSSIA WANTS MORE THAN UKRAINE",
     "BERLIN DEFENDS KYIV AID; KREMLIN REJECTS WESTERN FORCE IDEA",
     "GUARDIAN", 13.4, 52.5, False),
    (18, "ME", "EISENKOT BUILDS ISRAELI COALITION",
     "TALKS WITH LIKUD; JEWISH-MAJORITY GOVT EYED BY NEXT WEEK",
     "AL JAZEERA", 35.2, 31.8, False),
    (19, "AS", "CHINA PROBES SHANGHAI CHIEF CHEN JINING",
     "4TH POLITBURO MEMBER OUT IN 2 YEARS; GRAFT PROBE",
     "AL JAZEERA", 121.5, 31.2, False),
    (20, "AS", "BANGLADESH GARMENT PAY +36%",
     "MINIMUM 12,500 TO 17,000 TAKA AFTER WEEKS OF PROTESTS",
     "AL JAZEERA", 90.4, 23.8, False),
    (21, "AS", "INDONESIA MINE FLOOD: 3 DEAD, 23 TRAPPED",
     "RIVER OVERFLOWED INTO ILLEGAL GOLD MINE IN WEST JAVA",
     "SCMP", 107.6, -6.9, False),
    (22, "EU", "UK ENERGY CAP +26% FROM JANUARY",
     "TYPICAL BILL 1,723 TO 2,166 GBP; 3RD RISE IN A ROW",
     "BBC", -0.1, 51.5, False),
    (23, "OC", "AUSTRALIA INFLATION 4.9%",
     "FUEL DROVE RISE; ASX 200 STILL GAINED 1.4%",
     "GUARDIAN", 149.1, -35.3, False),
    (24, "AM", "ARGENTINA IN TECHNICAL RECESSION",
     "2 QUARTERS OF CONTRACTION; BAKERIES REPORT SALES COLLAPSE",
     "MERCOPRESS", -58.4, -34.6, False),
    (25, "AM", "CUBA LIFE EXPECTANCY FALLS TO 74.4",
     "FROM 78.8 IN 2020; FIRST FALL SINCE 1950, SAYS WHO",
     "GUARDIAN", -82.4, 23.1, False),
    (26, "EU", "UKRAINE NEEDS EUR 115BN FOR 2027",
     "ZELENSKY: EXTERNAL FINANCING GAP; PATRIOT PAUSE HURTS",
     "BBC", 30.5, 50.4, False),
    (27, "SP", "BEPICOLOMBO REACHES MERCURY ORBIT",
     "8-YEAR TRIP ENDS; PROBE SAFE DESPITE GLITCH",
     "CBC", None, None, False),
    (28, "AF", "ZAMBIA INDICTS OPPOSITION LEADER",
     "TREASON CHARGES OVER ALLEGED PLOT; 12 OTHERS CHARGED",
     "RFI", 28.3, -15.4, False),
    (29, "AF", "SUDAN DRONES KILL 19 CIVILIANS",
     "RSF STRIKES IN BLUE NILE; 28 WOMEN, GIRLS ABDUCTED",
     "STRAITS TIMES", 33.9, 11.8, False),
    (30, "ME", "IRAQ TO SEIZE KURDISH OILFIELDS",
     "BAGHDAD: CRUDE SMUGGLED VIA IRAN, BLENDED FOR EXPORT",
     "MEE", 44.4, 33.3, False),
    (31, "AF", "DR CONGO HALTS COBALT EXPORTS AGAIN",
     "2ND PAUSE TO LIFT PRICES; CONGO LEADS BATTERY SUPPLY",
     "AFRICANEWS", 15.3, -4.3, False),
    (32, "EU", "ENGLAND HEAT DEATHS HIT RECORD 5,200",
     "TWICE THE OLD RECORD; OLDER PEOPLE MOST AT RISK",
     "BBC", -0.1, 51.5, False),
    (33, "AM", "DEMOCRATS TAKE HOUSE; TRUMP'S TURKEYS",
     "GIULIANI GETS MEDAL OF FREEDOM AT THANKSGIVING EVENT",
     "GUARDIAN", -77.0, 38.9, False),
    (34, "AM", "PENTAGON SLAMS CANADA'S DEFENCE SPENDING",
     "OTTAWA: SOVEREIGN, WE REPORT TO NO ONE; F-35 UNDER REVIEW",
     "PBS", -75.7, 45.4, False),
    (35, "EU", "SPAIN HEADS TO SNAP ELECTION",
     "PP LEADS POLLS; FAR RIGHT MAY ENTER GOVT FIRST TIME",
     "BBC", -3.7, 40.4, False),
    (36, "ME", "IRAN FLOGS SINGER 74 TIMES",
     "PARASTOO AHMADI PUNISHED OVER UNVEILED CONCERT; UN CONDEMNS",
     "FRANCE 24", 50.9, 34.6, False),
    (37, "AS", "HONG KONG MARKS TAI PO FIRE YEAR",
     "168 KILLED IN 2025; FAMILIES STILL WAIT FOR ANSWERS",
     "SCMP", 114.2, 22.3, False),
    (38, "EU", "US, ARMENIA LAUNCH TRUMP TRANSIT ROUTE",
     "YEAR AFTER PEACE SUMMIT; BAKU WELCOMES CORRIDOR",
     "EURONEWS", 44.5, 40.2, False),
    (39, "AM", "BRAZIL: WOLBACHIA CUTS VIRUS RISK 68%",
     "MOSQUITO RELEASE PROTECTS SCHOOLCHILDREN FROM DENGUE",
     "GOOD NEWS NETWORK", -52.0, -10.0, False),
    (40, "AF", "DANGOTE REFINERY $1.6BN IPO",
     "SET TO BE AFRICA'S MOST VALUABLE LISTED FIRM",
     "OILPRICE", 3.4, 6.5, False),
    (41, "AF", "DR CONGO PLANE MISSING, REBELS CLAIM HIT",
     "S. AFRICAN PILOT, UGANDAN OFFICER ABOARD; EBOLA TEAM TRAPPED",
     "BBC", 29.0, -3.0, False),
    (42, "AM", "VENEZUELA DEBT: $237.5BN REVEALED",
     "FIRST CLEAR FIGURE AHEAD OF RESTRUCTURING TALKS",
     "AL JAZEERA", -66.9, 10.5, False),
    (43, "AS", "NORTH KOREA EXPELS SWISS DIPLOMAT",
     "48 HOURS TO LEAVE; OFFICE OPENED ONLY ON 19 OCT",
     "UPI", 125.8, 39.0, False),
    (44, "AM", "US ARMY TO DETONATE 5 TONS OF EXPLOSIVE",
     "68 DRUMS OF LEAD AZIDE IN IOWA; PUBLIC WORRIED",
     "UPI", -93.6, 41.9, False),
    (45, "OC", "SYDNEY DOUBLE-MURDER VERDICT: GUILTY",
     "EX-OFFICER KILLED JESSE BAIRD AND LUKE DAVIES IN 2024",
     "BBC", 151.2, -33.9, False),
    (46, "AS", "HANOI GAS BLAST KILLS 7",
     "HOT POT RESTAURANT EXPLOSION; 9 INJURED",
     "VNEXPRESS", 105.9, 21.0, False),
    (47, "ME", "UAE BUS CRASH KILLS 13",
     "BUS HIT PARKED TRUCK IN RAS AL KHAIMAH; 14 INJURED",
     "GULF NEWS", 55.9, 25.8, False),
    (48, "AM", "CIA UNCLASSIFIED SYSTEM BREACHED",
     "HACK EXPOSED SOME DATA; ODNI ALSO HIT; FINCEN PROBED",
     "FRANCE 24", -77.2, 38.9, True),
    (49, "EU", "EU UNVEILS QUANTUM ACT",
     "LESS ASIAN DRUG RELIANCE; BIGGEST SATELLITE FACTORY OPENS",
     "LE MONDE", 4.35, 50.85, False),
    (50, "AS", "SOORYAVANSHI, 15, SMASHES 204 OFF 53",
     "FASTEST LIST A DOUBLE TON; INDIA A BEAT UAE",
     "BBC SPORT", 51.5, 25.3, False),
]

TIMELINE = [
    ("00:00", "UKRAINE NEEDS EUR 115BN FOR 2027"),
    ("04:00", "BANGLADESH PAY +36% AFTER PROTESTS"),
    ("08:00", "CARTAGENA: ALL HOSTAGES FREED"),
    ("12:00", "2 TANKERS HIT MINES IN HORMUZ"),
    ("16:00", "HUAWEI CONVICTED IN NEW YORK"),
    ("20:00", "US SHARES SLIDE ON TARIFF REPORTS"),
]

DATE_CHECK = [
    "TAI PO FIRE ITSELF (NOV 2025, 168 DEAD)",
    "SHURI CASTLE HALL REOPENED 23 NOV",
    "THOMAS MARKLE ARRESTED 6 NOV",
    "HUANG LEFT NVIDIA 12 NOV",
    "US MIDTERM VOTING 3 NOV",
    "SENEGAL AFCON FINAL WALK-OFF JAN 2026",
    "US STRIKES ON IRAN NUCLEAR SITES JUL 2025",
    "BEPICOLOMBO LAUNCHED 2018",
]

# Rough continent outlines (lon, lat), schematic equirectangular map.
NORTH_AMERICA = [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
                 (-85, 80), (-75, 73), (-65, 60), (-55, 52), (-60, 47),
                 (-70, 42), (-75, 35), (-80, 32), (-81, 26), (-84, 30),
                 (-90, 21), (-97, 26), (-105, 23), (-110, 28), (-117, 33),
                 (-125, 40), (-125, 49), (-135, 58), (-150, 61), (-165, 60)]
GREENLAND = [(-58, 64), (-45, 60), (-30, 68), (-20, 70), (-30, 76),
             (-55, 76), (-60, 70)]
SOUTH_AMERICA = [(-80, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0),
                 (-44, -3), (-35, -8), (-40, -20), (-48, -28), (-58, -35),
                 (-65, -41), (-70, -50), (-73, -54), (-70, -40), (-73, -30),
                 (-70, -18), (-77, -12), (-81, -6), (-80, 1)]
AFRICA = [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
          (35, 28), (43, 12), (51, 11), (48, 2), (40, -5), (40, -15),
          (35, -25), (28, -33), (20, -35), (15, -27), (12, -18), (9, -1),
          (9, 4), (-8, 5), (-13, 8), (-17, 15)]
EURASIA = [(-10, 36), (-9, 43), (-2, 48), (2, 51), (5, 53), (8, 57),
           (12, 56), (18, 56), (21, 54), (24, 58), (28, 59), (30, 60),
           (32, 66), (40, 68), (55, 69), (68, 73), (75, 73), (90, 75),
           (105, 77), (120, 73), (135, 72), (150, 70), (160, 66), (170, 66),
           (178, 65), (170, 60), (162, 56), (158, 52), (150, 59), (142, 55),
           (140, 50), (135, 43), (130, 42), (127, 40), (122, 38), (120, 32),
           (122, 28), (115, 23), (108, 18), (105, 10), (100, 8), (98, 12),
           (94, 17), (90, 22), (86, 20), (80, 15), (77, 8), (73, 20),
           (66, 25), (60, 25), (57, 26), (52, 28), (50, 30), (48, 29),
           (44, 29), (43, 12), (39, 21), (35, 28), (34, 31), (30, 36),
           (27, 37), (23, 36), (19, 42), (15, 44), (12, 45), (8, 44),
           (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 35), (-10, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
             (132, -32), (135, -35), (140, -38), (145, -38), (150, -37),
             (153, -32), (153, -27), (150, -22), (146, -19), (142, -11),
             (136, -12), (132, -11), (126, -14), (122, -17), (118, -20),
             (113, -22)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (45, -25),
              (43, -22), (44, -16)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-3, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
         (141, 41), (143, 43), (145, 44), (142, 42), (140, 39), (138, 37),
         (135, 35), (132, 33)]
SUMATRA = [(95, 5), (100, 0), (104, -3), (106, -6), (100, -5), (96, 2)]
BORNEO = [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3),
          (109, 0)]
NEW_GUINEA = [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9),
              (147, -8), (141, -8), (136, -6), (131, -3)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              AUSTRALIA, MADAGASCAR, UK, JAPAN, SUMATRA, BORNEO, NEW_GUINEA]

# --- drawing ---

def region_counts():
    counts = {}
    for s in STORIES:
        counts[s[1]] = counts.get(s[1], 0) + 1
    return counts


def draw_masthead(cv):
    cv.hline(14, 8, 996, INK, 3)
    cv.text_center("WEDNESDAY 25 NOVEMBER 2026", 512, 16, 3, INK)
    cv.text_center("THE WORLD IN ONE PAGE", 512, 42, 2, RED)
    counts = region_counts()
    parts = []
    for code in ("ME", "EU", "AS", "AF", "AM", "OC", "SP"):
        parts.append("%s %d" % (REGION_NAME[code], counts.get(code, 0)))
    cv.text_center("50 STORIES - 7 REGIONS - " + " - ".join(parts), 512, 62, 1, INK)
    # region count bar
    x = 14
    total = len(STORIES)
    for code in ("ME", "EU", "AS", "AF", "AM", "OC", "SP"):
        wseg = int(996 * counts.get(code, 0) / total)
        cv.rect(x, 74, wseg, 8, REGION_COLOR[code])
        x += wseg
    cv.hline(14, 86, 996, INK, 2)


def draw_timeline(cv):
    y = 92
    cv.text("UTC TIMELINE - THE DAY AS IT HAPPENED", 14, y, 1, INK)
    cv.hline(14, y + 10, 996, GREY, 1)
    slot_w = 996 // 6
    for i, (t, ev) in enumerate(TIMELINE):
        x = 14 + i * slot_w
        cv.text(t, x + 4, y + 14, 2, REGION_COLOR["EU"] if i % 2 == 0 else RED)
        lines = cv.wrap(ev, slot_w - 8, 1)
        yy = y + 30
        for ln in lines[:2]:
            cv.text(ln, x + 4, yy, 1, INK)
            yy += 9
        if i < 5:
            cv.vline(x + slot_w - 2, y + 14, 40, GREY, 1)
    cv.hline(14, 148, 996, INK, 2)


def hero_art(cv, x, y, w, h, kind, color):
    cv.rect(x, y, w, h, SKY)
    if kind == 1:  # Hormuz: sea, two tankers, mine, blast
        cv.rect(x, y + h - 34, w, 34, SEA)
        cv.rect(x + 18, y + h - 62, 90, 22, INK)
        cv.rect(x + 34, y + h - 74, 22, 12, INK)
        cv.rect(x + 130, y + h - 58, 76, 18, (60, 60, 60))
        cv.rect(x + 146, y + h - 68, 16, 10, (60, 60, 60))
        cv.circle(x + 66, y + 26, 5, INK)
        for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7), (-5, -5), (5, 5)):
            cv.line(x + 66 + dx, y + 26 + dy, x + 66 + dx * 2, y + 26 + dy * 2, INK)
        cv.circle(x + 170, y + 30, 12, RED)
        cv.circle(x + 170, y + 30, 6, (255, 220, 0))
    elif kind == 2:  # Huawei: courthouse columns + GUILTY stamp
        cv.rect(x, y + h - 8, w, 8, INK)
        cv.rect(x + 20, y + 18, w - 40, 10, INK)
        for cx in (x + 34, x + 84, x + 134, x + 184):
            cv.rect(cx, y + 28, 10, h - 36, INK)
        cv.text("GUILTY", x + 62, y + 40, 2, RED)
        cv.rect(x + 56, y + 36, 118, 26, RED)
        cv.text("GUILTY", x + 62, y + 42, 2, (255, 255, 255))
    elif kind == 3:  # Tech selloff: falling chart
        cv.rect(x, y, w, h, (255, 255, 255))
        cv.hline(x + 14, y + h - 22, w - 28, INK, 2)
        cv.vline(x + 14, y + 12, h - 34, INK, 2)
        pts = [(x + 20, y + 24), (x + 70, y + 34), (x + 110, y + 30),
               (x + 150, y + 52), (x + 190, y + 62), (x + 220, y + 78)]
        for a, b in zip(pts, pts[1:]):
            cv.line(a[0], a[1], b[0], b[1], RED)
            cv.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
        cv.line(pts[-1][0], pts[-1][1], pts[-1][0] + 12, pts[-1][1] + 14, RED)
        cv.line(pts[-1][0], pts[-1][1], pts[-1][0] + 14, pts[-1][1] - 2, RED)
        cv.text("-2.8%", x + 150, y + 10, 2, RED)
    else:  # Shenzhou: rocket, stars, Earth arc
        cv.rect(x, y, w, h, (16, 24, 48))
        for sx, sy in ((30, 18), (70, 12), (200, 16), (220, 40), (40, 44)):
            cv.circle(x + sx, y + sy, 2, (255, 255, 255))
        cv.rect(x + 108, y + 22, 24, 56, (255, 255, 255))
        cv.poly([(x + 108, y + 22), (x + 132, y + 22), (x + 120, y + 4)],
                (255, 255, 255))
        cv.poly([(x + 108, y + 78), (x + 96, y + 96), (x + 108, y + 84)],
                RED)
        cv.poly([(x + 132, y + 78), (x + 144, y + 96), (x + 132, y + 84)],
                RED)
        cv.poly([(x + 112, y + 78), (x + 128, y + 78), (x + 120, y + 100)],
                (255, 180, 0))
        cv.circle(x + 120, y + 48, 6, BLUE)
        cv.circle(x + 16, y + h - 14, 10, SEA)
        cv.text("TIANGONG", x + 140, y + h - 20, 1, (255, 255, 255))


def draw_heroes(cv):
    heroes = [STORIES[0], STORIES[1], STORIES[2], STORIES[11]]
    y = 156
    card_w = 244
    card_h = 152
    for i, s in enumerate(heroes):
        x = 14 + i * (card_w + 6)
        n, reg, head, det, src, lon, lat, claim = s
        cv.rect(x, y, card_w, card_h, (255, 255, 255))
        cv.rect(x, y, card_w, 3, REGION_COLOR[reg])
        hero_art(cv, x + 4, y + 6, card_w - 8, 66, i + 1, REGION_COLOR[reg])
        yy = y + 78
        cv.text("%d" % n, x + 6, yy, 2, REGION_COLOR[reg])
        lines = cv.wrap(head, card_w - 34, 2)
        ly = yy
        for ln in lines[:2]:
            cv.text(ln, x + 34, ly, 2, INK)
            ly += 15
        dy = y + 78 + 30
        dlines = cv.wrap(det, card_w - 12, 1)
        for ln in dlines[:2]:
            cv.text(ln, x + 6, dy, 1, INK)
            dy += 9
        tag = src + ("  [CLAIM]" if claim else "")
        cv.text(tag, x + 6, y + card_h - 12, 1, GREY)
    # borders
    for i in range(4):
        x = 14 + i * (card_w + 6)
        cv.hline(x, y, card_w, INK, 1)
        cv.hline(x, y + card_h - 1, card_w, INK, 1)
        cv.vline(x, y, card_h, INK, 1)
        cv.vline(x + card_w - 1, y, card_h, INK, 1)


def draw_small_cards(cv):
    smalls = [STORIES[i] for i in (3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 19, 20)]
    y0 = 316
    card_w = 244
    card_h = 52
    for i, s in enumerate(smalls):
        row, col = divmod(i, 4)
        x = 14 + col * (card_w + 6)
        y = y0 + row * (card_h + 5)
        n, reg, head, det, src, lon, lat, claim = s
        cv.rect(x, y, card_w, card_h, (255, 255, 255))
        cv.rect(x, y, 4, card_h, REGION_COLOR[reg])
        cv.text("%02d" % n, x + 8, y + 5, 1, REGION_COLOR[reg])
        lines = cv.wrap(head, card_w - 40, 1)
        ly = y + 5
        for ln in lines[:2]:
            cv.text(ln, x + 34, ly, 1, INK)
            ly += 9
        dlines = cv.wrap(det, card_w - 12, 1)
        if dlines:
            cv.text(dlines[0][:38], x + 8, y + 24, 1, INK)
        tag = src + (" [CLAIM]" if claim else "")
        cv.text(tag, x + 8, y + 38, 1, GREY)
        cv.hline(x, y, card_w, INK, 1)
        cv.hline(x, y + card_h - 1, card_w, INK, 1)
        cv.vline(x, y, card_h, INK, 1)
        cv.vline(x + card_w - 1, y, card_h, INK, 1)

def draw_map(cv):
    y0 = 492
    cv.text("WHERE IT HAPPENED - 50 STORIES, NUMBERED", 14, y0, 1, INK)
    cv.hline(14, y0 + 10, 996, INK, 1)
    mx, my, mw, mh = 14, y0 + 16, 700, 178
    cv.rect(mx, my, mw, mh, (214, 232, 240))
    # equirectangular: lon -180..180 -> x; lat 85..-60 -> y
    def proj(lon, lat):
        px = mx + int((lon + 180.0) / 360.0 * mw)
        py = my + int((85.0 - lat) / 145.0 * mh)
        return px, py
    for cont in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in cont]
        cv.poly(pts, (226, 214, 178))
        for a, b in zip(pts, pts[1:] + pts[:1]):
            cv.line(a[0], a[1], b[0], b[1], (150, 140, 115))
    # pins, jittered so same-city stories do not stack
    seen = {}
    for s in STORIES:
        n, reg, head, det, src, lon, lat, claim = s
        if lon is None:
            continue
        key = (round(lon), round(lat))
        k = seen.get(key, 0)
        seen[key] = k + 1
        jx = (k % 3 - 1) * 9
        jy = (k // 3) * 9 - 4
        px, py = proj(lon, lat)
        px += jx
        py += jy
        cv.circle(px, py, 4, REGION_COLOR[reg])
        cv.circle(px, py, 4, INK, fill=False)
        lab = str(n)
        lx = px + 5
        ly = py - 3
        if lx + len(lab) * 6 > mx + mw - 2:
            lx = px - 5 - len(lab) * 6
        cv.text(lab, lx, ly, 1, INK)
    # legend
    lx = 730
    ly = y0 + 16
    cv.text("LEGEND - REGION", lx, ly, 1, INK)
    counts = region_counts()
    yy = ly + 14
    for code in ("ME", "EU", "AS", "AF", "AM", "OC", "SP"):
        cv.rect(lx, yy, 12, 8, REGION_COLOR[code])
        cv.text("%s - %d" % (REGION_NAME[code], counts.get(code, 0)),
                lx + 18, yy, 1, INK)
        yy += 14
    yy += 4
    cv.text("SPACE: 12 SHENZHOU-24,", lx, yy, 1, INK)
    yy += 10
    cv.text("27 BEPICOLOMBO (NO PIN)", lx, yy, 1, INK)
    yy += 14
    cv.text("[CLAIM] = NOT YET", lx, yy, 1, RED)
    yy += 10
    cv.text("VERIFIED BY A 2ND SOURCE", lx, yy, 1, RED)
    yy += 14
    cv.text("EACH NUMBER ON THE MAP", lx, yy, 1, INK)
    yy += 10
    cv.text("MATCHES A NUMBERED", lx, yy, 1, INK)
    yy += 10
    cv.text("STORY ON THIS PAGE.", lx, yy, 1, INK)
    cv.hline(14, y0 + 198, 996, INK, 1)


def brief_line(s, cv, col_w):
    n, reg, head, det, src, lon, lat, claim = s
    suffix = " [CLAIM]" if claim else ""
    head_part = "%d. %s - " % (n, head)
    tail = " (%s)%s" % (src, suffix)
    # fit as much of the detail as possible, cut at a word boundary
    budget = col_w - cv.text_w(head_part + tail, 1)
    words = det.split(" ")
    keep = []
    used = 0
    for wd in words:
        w = cv.text_w(wd + " ", 1) if keep else cv.text_w(wd, 1)
        if used + w <= budget:
            keep.append(wd)
            used += w
        else:
            break
    det2 = " ".join(keep)
    return head_part + det2 + tail


def draw_briefs(cv):
    y0 = 700
    cv.text("THE REST OF THE DAY - BRIEFS 17-50", 14, y0, 1, INK)
    cv.hline(14, y0 + 10, 996, INK, 1)
    briefs = STORIES[16:]
    col_w = 493
    row_h = 15
    for i, s in enumerate(briefs):
        col, row = divmod(i, 17)
        x = 14 + col * (col_w + 10)
        y = y0 + 16 + row * row_h
        line = brief_line(s, cv, col_w)
        cv.text(line, x, y, 1, INK)
    cv.hline(14, y0 + 16 + 17 * row_h + 2, 996, INK, 2)


def draw_footer(cv):
    y0 = 984
    cv.text("DATE CHECK - LEFT OUT ON PURPOSE (BROKE BEFORE 25 NOV):",
            14, y0, 1, RED)
    lines = cv.wrap(" - ".join(DATE_CHECK) + ".", 996, 1)
    yy = y0 + 11
    for ln in lines[:2]:
        cv.text(ln, 14, yy, 1, INK)
        yy += 9
    cv.text("ALL 50 STORIES REPORTED 25 NOV 2026 (UTC). SOURCES ON EACH CARD.",
            14, 1012, 1, GREY)


def main():
    out = "/output"
    os.makedirs(out, exist_ok=True)
    # clear only the contents of /output, never the folder itself
    for name in os.listdir(out):
        p = os.path.join(out, name)
        if os.path.isfile(p):
            os.remove(p)
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_timeline(cv)
    draw_heroes(cv)
    draw_small_cards(cv)
    draw_map(cv)
    draw_briefs(cv)
    draw_footer(cv)
    n = write_png(cv, os.path.join(out, "entry.png"))
    print("wrote /output/entry.png %d bytes" % n)


if __name__ == "__main__":
    main()
