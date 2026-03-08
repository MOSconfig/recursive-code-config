# Rec Mono / Rec Sans Code Fonts

Custom builds of [Recursive](https://recursive.design) fonts for coding and daily use, with CJK glyphs from [Resource Han Rounded (资源圆体)](https://github.com/CyanoHao/Resource-Han-Rounded) and [Nerd Font](https://www.nerdfonts.com/) icons.

## Fonts

| Family | Type | Slant (Regular / Italic) | Features |
|---|---|---|---|
| **Rec Mono St.Helens** | Monospace (`MONO: 1`) | -4° / -10° | ss01–ss12 (all) |
| **Rec Mono Baker** | Proportional (`MONO: 0`) | -4° / -10° | ss01–ss12 (all) |

Both families:

- Fully **Casual** (`CASL: 1`) and **Cursive** (`CRSV: 1`)
- Weight **400** (Regular/Italic), **600** (Bold/Bold Italic)
- **Code ligatures** enabled
- **CJK**: Resource Han Rounded — Regular for Regular/Italic, Bold for Bold/Bold Italic, scaled 1.15×
- **Nerd Font** icons (`--complete`)
- 4 styles each: Regular, Italic, Bold, Bold Italic

**St.Helens** is the monospace variant for code editors and terminals. **Baker** is the proportional variant for UI, notes, and general reading.

## Install

Download `.ttf` files from the [latest release](https://github.com/MOSconfig/recursive-code-config/releases/latest), then:

- **macOS**: Copy to `~/Library/Fonts/`
- **Linux**: Copy to `~/.local/share/fonts/` then `fc-cache -f`
- **Windows**: Right-click → Install

## Build from Source

### Prerequisites

- Python 3, [FontForge](https://fontforge.org/) with Python bindings (`brew install fontforge`)
- CJK fonts in `font-data/`: `ResourceHanRoundedCN-Regular.ttf` and `ResourceHanRoundedCN-Bold.ttf` from [Resource Han Rounded](https://github.com/CyanoHao/Resource-Han-Rounded/releases)

### Build

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Build all 8 fonts in parallel
./scripts/build-all.sh

# Or build one family
./scripts/build.sh config.helens.yaml
./scripts/build.sh config.baker.yaml
```

The build pipeline (4 stages, fontforge steps parallelized):

1. **Instantiate** — variable font → 4 static RIBBI styles
2. **Merge CJK** — Resource Han Rounded glyphs: Regular for Regular/Italic, Bold for Bold/Bold Italic (4 styles in parallel)
3. **Nerd Font Patch** — full icon set (4 styles in parallel)
4. **Rename** — strip "Nerd Font" suffix

Default CJK scale is `1.15`. Override: `./scripts/build-all.sh 1.2`

## Credits

[Recursive](https://github.com/arrowtype/recursive) by Arrow Type · [Resource Han Rounded](https://github.com/CyanoHao/Resource-Han-Rounded) by CyanoHao · [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) by Ryan L McIntyre · Original [recursive-code-config](https://github.com/arrowtype/recursive-code-config) by Arrow Type

## License

[SIL Open Font License](LICENSE)
