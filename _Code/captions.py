from PIL import ImageFont
from pathlib import Path
import re
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',34)
header="""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,38,&H00F4F4F4,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,40,40,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for block in Path('Assets/English.srt').read_text().strip().split('\n\n'):
 _,ts,s=block.split('\n');a,b=[t[1:].replace(',','.')[:-1] for t in ts.split(' --> ')]
 if font.getlength(s)>1680:
  w=s.split();k=min(range(1,len(w)),key=lambda i:abs(font.getlength(' '.join(w[:i]))-font.getlength(' '.join(w[i:]))))
  s=' '.join(w[:k])+r'\N'+' '.join(w[k:])
 header+=f'Dialogue: 0,{a},{b},Default,,0,0,0,,{{'+r'\an5\pos(960,50)'+'}'+s+'\n'
Path('build/top.ass').write_text(header)
