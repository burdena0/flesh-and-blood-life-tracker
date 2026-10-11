"""Refresh assembly and copper PNGs directly from the latest KiCad SVG exports."""
from pathlib import Path
from resvg_py import svg_to_bytes

root = Path(__file__).resolve().parents[1]
for name in ['assembly-top', 'pcb-top', 'pcb-back']:
    source = root / 'docs' / (name + '.svg')
    target = source.with_suffix('.png')
    target.write_bytes(svg_to_bytes(svg_path=str(source), width=1600,
                                    dpi=96, background='#ffffff'))
    print('Refreshed', target.name)
