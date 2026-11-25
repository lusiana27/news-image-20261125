# Wednesday 25 November 2026 in one image — 50 sourced stories, UTC timeline, map and date check

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/lusiana27/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/lusiana27/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Entry for [Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
($100 shared by the top 50 entries). A program that draws one newspaper
page — **50 numbered stories from Wednesday 25 November 2026, 7 regions,
a UTC timeline, a numbered world map, and a footer DATE CHECK** — and
writes it to `/output/entry.png` (1024×1024).

## What is on the page

- **Masthead:** WEDNESDAY 25 NOVEMBER 2026 — 50 STORIES · 7 REGIONS,
  with a per-region count bar (Middle East 7, Europe 10, Asia 8,
  Africa 7, Americas 13, Oceania 3, Space 2).
- **UTC timeline:** 00:00 Ukraine needs EUR 115bn · 04:00 Bangladesh
  pay +36% · 08:00 Cartagena hostages freed · 12:00 two tankers hit
  mines in Hormuz · 16:00 Huawei convicted · 20:00 US shares slide.
- **4 hero cards:** Hormuz tankers mined, Huawei convicted in New York,
  Asian tech selloff (Nikkei −2.8%), Pakistan's first astronaut on
  Shenzhou-24.
- **12 small cards:** tariffs on 16 economies, Riyadh tower strike,
  ~490,000 leaked Russian war deaths, Ukraine's Libya strike, Gaza,
  oil −20% in November, Nvidia −4.5%, Cartagena siege, Senegal's AFCON
  title restored, Solomons–Australia treaty, Bangladesh pay rise,
  Indonesia mine flood.
- **Numbered world map** with a region legend; space stories
  (Shenzhou-24, BepiColombo) listed in the legend.
- **Briefs 17–50** with a source on every story, concrete numbers in
  every line, and `[CLAIM]` tags on claims no second source has verified
  (leaked Russian death toll, reported CIA breach).
- **DATE CHECK footer:** stories deliberately left out because they
  broke before 25 Nov (Tai Po fire itself, Shuri Castle reopening,
  Markle arrest, Huang leaving Nvidia, US midterms, Senegal walk-off,
  Iran strikes, BepiColombo launch).

## Run

```sh
python3 -S main.py   # stdlib only — no Pillow, no numpy, no external font
```

Writes `/output/entry.png` (1024×1024, under 1 MiB, deterministic: two
runs are byte-identical — verified with `sha256sum`).

## How it works

`main.py` is pure Python standard library (`binascii`, `math`, `os`,
`struct`, `zlib`). It defines its own 5×7 bitmap font, draws the whole
page on an RGB canvas (masthead, timeline, hero illustrations, cards,
schematic world map, briefs, footer), and encodes the PNG by hand
(struct + zlib + CRC chunks). No network, no third-party packages, no
external font or data files — so it runs the same way in the grader
image as it does locally.

## Referral

Made with make.fun — [join with my referral link](https://make.fun/r/j11vkafs)
(referral code `j11vkafs`).

## License

MIT — see [LICENSE](LICENSE).
