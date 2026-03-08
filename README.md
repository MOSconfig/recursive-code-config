# Rec Mono Code Fonts

Custom builds of [Recursive](https://recursive.design) monospace fonts for coding, with CJK glyphs from [Resource Han Rounded (资源圆体)](https://github.com/CyanoHao/Resource-Han-Rounded) and [Nerd Font](https://www.nerdfonts.com/) icons.

## Included Fonts

| Family | Regular Slant | Config |
|---|---|---|
| **Rec Mono Baker** | -6° | `config.baker.yaml` |
| **Rec Mono St.Helens** | -4° | `config.helens.yaml` |

Both families are fully Casual (`CASL: 1`), Cursive (`CRSV: 1`), with all stylistic sets enabled and code ligatures on. Each includes Regular, Italic, Bold, and Bold Italic styles.

### Pre-built Fonts

Ready-to-install `.ttf` files are in the `fonts/` directory:

```
fonts/RecMonoBaker/        — Rec Mono Baker (4 styles)
fonts/RecMonoSt.Helens/    — Rec Mono St.Helens (4 styles)
```

## Installation

Copy the font files to your system font directory:

- **macOS**: `cp fonts/RecMonoBaker/*.ttf fonts/RecMonoSt.Helens/*.ttf ~/Library/Fonts/`
- **Linux**: `cp fonts/RecMono*/*.ttf ~/.local/share/fonts/ && fc-cache -f`
- **Windows**: Right-click the `.ttf` files → Install

In your editor, set the font family and enable ligatures. For example in VS Code:

```json
{
  "editor.fontFamily": "Rec Mono St.Helens",
  "editor.fontLigatures": true
}
```

## Building from Source

### Prerequisites

- **Python 3** with pip
- **FontForge** with Python bindings
  ```bash
  brew install fontforge   # macOS
  ```
- Resource Han Rounded font files in `font-data/`:
  - `ResourceHanRoundedCN-Regular.ttf`
  - `ResourceHanRoundedCN-Bold.ttf`

### Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Build

Each config is built with a single command. The build script runs all four stages automatically:

1. Instantiate variable font into 4 static RIBBI styles
2. Merge CJK glyphs (double-width) from Resource Han Rounded
3. Patch Nerd Font icons (all icon sets)
4. Rename font family (strip Nerd Font suffix)

```bash
source venv/bin/activate

# Build St.Helens (CJK scale 1.1)
./scripts/build.sh config.helens.yaml 1.1

# Build Baker (CJK scale 1.1)
./scripts/build.sh config.baker.yaml 1.1
```

The second argument is the CJK scale factor (default: `1.1`). This controls the relative size of CJK characters compared to Latin glyphs.

### Custom Configurations

To create your own variant:

1. Copy an existing config (e.g. `config.baker.yaml`) to a new file
2. Edit the `Family Name`, axis values, and features
3. Run `./scripts/build.sh your-config.yaml`

See the config files for documentation on available axis values and stylistic sets.

## Configuration Options

### Variable Axes

| Axis | Range | Description |
|---|---|---|
| `MONO` | 0–1 | 0 = Sans, 1 = Mono |
| `CASL` | 0–1 | 0 = Linear, 1 = Casual |
| `wght` | 300–1000 | Font weight |
| `slnt` | 0 to -15 | Slant in degrees |
| `CRSV` | 0–1 | 0 = Roman, 1 = Cursive |

### Stylistic Sets

| Feature | Description |
|---|---|
| `ss01` | Single-story a |
| `ss02` | Single-story g |
| `ss03` | Simplified f |
| `ss04` | Simplified i |
| `ss05` | Simplified l |
| `ss06` | Simplified r |
| `ss07` | Simplified k |
| `ss08` | Serifless L and Z |
| `ss09` | Simplified 6 and 9 |
| `ss10` | Dotted 0 |
| `ss11` | Simplified 1 |
| `ss12` | Simplified @ |

## Credits

- [Recursive](https://github.com/arrowtype/recursive) by Arrow Type
- [Resource Han Rounded](https://github.com/CyanoHao/Resource-Han-Rounded) by CyanoHao
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) by Ryan L McIntyre
- Original [recursive-code-config](https://github.com/arrowtype/recursive-code-config) by Arrow Type

## License

See [LICENSE](LICENSE) for the Recursive font license (SIL Open Font License).
