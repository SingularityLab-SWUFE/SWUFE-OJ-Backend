import markdown
import re

def change_formula(matched):
    formula = matched.group(0)
    formula = formula.replace('_', ' _')
    return '\n<p>'+formula+'</p>\n'


def markdown_format(texts: list[str]):
    for text in texts:
        text = markdown.markdown(re.sub(r'\$\$(.+?)\$\$', change_formula, text),
                                 extension_configs=[
            # 包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            # 语法高亮扩展
            'markdown.extensions.codehilite',])
