import matplotlib.pyplot as plt
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

'''
===bar_graph() parameters===
x: int,   x position of element, as defined in reportlab
x: int,   y position of element, as defined in reportlab
w: int,   maximum width of element
val: int, percentage(x100) of actual width to its maximum width
color: bool, whether to make this element gray or colored
'''

def bar_graph(x, y, w, val, c, color=True):
    # global c
    if color:
        if val > 60:
            this_color = bar_graph.colors['good']
        elif val > 30:
            this_color = bar_graph.colors['caution']
        else:
            this_color = bar_graph.colors['bad']
    else:
        this_color = bar_graph.colors['gray']

    c.setFillColorRGB(*this_color)    
    val = int(w * (val / 100))
    c.roundRect(
        x, y, 
        val, bar_graph.settings['thickness'], 
        min(bar_graph.settings['radius'], val), 
        stroke=0, fill=1
    )
    c.setFillColor(colors.black)

bar_graph.colors = {
    'good':    tuple((x / 255 for x in (40, 192, 123))), #'good' color (green)
    'caution': tuple((x / 255 for x in (252, 176, 78))), #'caution' color (orange)
    'bad':     tuple((x / 255 for x in (254, 97, 84))),  #'bad' color (red)
    'gray':    tuple((x / 255 for x in (100, 100, 100)))   # noncolor
}
bar_graph.settings = {
    'thickness': 15,
    'radius':    7,
}


'''
===draw() parameters===
name: str, e.g. 김철수
date: str, YYYY-MM
sex : int, 0(M) or 1(F)
scores: list[int] of length 4, where
    list[0] = 신체 건강
    list[1] = 정신 건강
    list[2] = 사회 건강
    list[3] = 생활 습관
texts: list[str] of length 2, where
    list[0] = 분석
    list[1] = 제안
'''

#####################################################################################
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)

#! PDF를 만드는데 필요한 파일 (절대주소 사용)
PDF_RESOURCE_DIR = os.path.join(current_directory, 'pdfResources')

#! 생성된 보고서를 저장하는 폴더 (절대주소 사용)
REPORT_DIR = '/usr/src/data/report'
#####################################################################################

def draw(name, date, sex, scores, texts, filename):
    pdfmetrics.registerFont(TTFont('NanumSquareR', os.path.join(PDF_RESOURCE_DIR, 'NanumSquareR.ttf')))
    pdfmetrics.registerFont(TTFont('NanumSquareB', os.path.join(PDF_RESOURCE_DIR, 'NanumSquareB.ttf')))
    pdfmetrics.registerFont(TTFont('NanumSquareEB', os.path.join(PDF_RESOURCE_DIR, 'NanumSquareEB.ttf')))
    pdfmetrics.registerFont(TTFont('Cascadia', os.path.join(PDF_RESOURCE_DIR, 'CascadiaMono.ttf')))

    h = 691.2
    w = 345.6

    c = canvas.Canvas(
        filename=os.path.join(REPORT_DIR, f'{filename}.pdf'),
        pagesize=(w, h),
    )


    avatar = 'm' if sex == 0 else 'f'
    avatar = os.path.join(PDF_RESOURCE_DIR, f'{avatar}.png')
    #avatar = './pdfResources/' + avatar + '.png'
    avatar_size = 100

    color = (x / 255 for x in (253, 219, 177))
    c.setFillColorRGB(*color)
    c.roundRect(0, h - avatar_size - 10, w, 200, 10, stroke=0, fill=1)
    c.drawImage(avatar, avatar_size // 10, h - avatar_size - 10, avatar_size, avatar_size, mask='auto')

    x = w // 2
    y = 50
    c.setFont('NanumSquareEB', 27)
    c.setFillColor(colors.black)
    c.drawCentredString(x - 5, h - y, name)
    namewidth = c.stringWidth(name, 'NanumSquareEB', 27)
    c.setFont('NanumSquareEB', 18)
    c.drawString(x + namewidth // 2, h - y, '님')

    x = w // 2
    y = 70
    c.setFillColor(colors.brown)
    c.setFont('NanumSquareB', 13)
    c.drawCentredString(x, h - y, '늘 건강 유의하세요!')
    c.setFillColor(colors.black)
    c.drawCentredString(x, h - avatar_size, date.replace('-', '년 ') + '월 보고서')

    x = (10, 110, 165)
    y = (130, 160, 190, 220)
    color = (x / 255 for x in (198, 228, 238))
    c.setFillColorRGB(*color)
    c.roundRect(5, h - y[-1] - 10, w - 10, (y[-1] - y[0]) + 27, 10, stroke=0, fill=1)

    c.setFillColor(colors.black)
    c.setFont('NanumSquareB', 18)
    c.drawString(x[0], h - y[0], '신체 건강')
    c.drawString(x[0], h - y[1], '정신 건강')
    c.drawString(x[0], h - y[2], '사회적 건강')
    c.drawString(x[0], h - y[3], '생활습관')

    c.setFont('Cascadia', 16)
    for i, y_ in enumerate(y):
        c.drawString(x[1], h - y_, f'{scores[i]: >3}')
    c.setFont('NanumSquareB', 18)
    for i, y_ in enumerate(y):
        c.drawString(x[1] + 10 * 3, h - y_, '점')

    for i, y_ in enumerate(y):
        bar_graph(x[-1], h - y_ - 5, w - x[-1] - 10, 100, c, False)
    for i, y_ in enumerate(y):
        bar_graph(x[-1], h - y_ - 5, w - x[-1] - 10, scores[i], c, True)

    x = 10
    y = 260
    c.setFont('NanumSquareEB', 18)
    c.drawString(x, h - y, '수호의 분석')
    style = getSampleStyleSheet()['Normal']
    style.fontName = 'NanumSquareR'
    style.fontSize = 14
    style.leading = style.fontSize + 5
    style.firstLineIndent = c.stringWidth('수호의 분석', 'NanumSquareEB', 18) + 10
    style.justifyBreaks = 1
    paragraph = Paragraph(texts[0], style)
    _w, _h = paragraph.wrapOn(c, w - 15, h)
    paragraph.drawOn(c, x, h - y - _h + style.fontSize - 2)

    x = 10
    y = y + _h + 20
    c.setFont('NanumSquareEB', 18)
    c.drawString(x, h - y, '수호의 제안')
    style.firstLineIndent = c.stringWidth('수호의 제안', 'NanumSquareEB', 18) + 10
    paragraph = Paragraph(texts[1], style)
    _w, _h = paragraph.wrapOn(c, w - 15, h)
    paragraph.drawOn(c, x, h - y - _h + style.fontSize - 2)

    c.showPage()
    c.save()

def pdf2img(filename):
    import pdf2image
    im = pdf2image.convert_from_path(os.path.join(REPORT_DIR, f'{filename}.pdf'))
    im[0].save(os.path.join(REPORT_DIR, f'{filename}.png'), 'PNG')
