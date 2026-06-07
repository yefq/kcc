import os
import re
import xml.etree.ElementTree as etree


SRC_DIR = "kindlecomicconverter"
TS_PATH = "locale/zh_CN.ts"

os.makedirs(os.path.dirname(TS_PATH), exist_ok=True)

# 正则匹配：QCoreApplication.translate("ctx", "text")
_pattern = re.compile(
    r'QCoreApplication\.translate\s*\(\s*' # QCoreApplication.translate(
    r'["\'](.*?)["\']' # "ctx"
    r'\s*,\s*' # ,
    r'(u?["\'].*?["\'])' # msg_set
    r'\s*,\s*' # ,
    , re.DOTALL)

_texts = {}

def load_texts(file_path):
    with open(file_path, "r", encoding="utf-8") as fp:
        for ctx, txt in _pattern.findall(fp.read()):
            txt: str
            if txt.startswith('u'):
                lines = [line.strip('"\'').replace(r'\n', '\n') for line in txt[1:].splitlines()]
                txt = "".join(lines)
            else:
                txt = txt.strip('"\'')
            if txt.startswith("<html>"):
                txt = txt.replace(r'\"', r'"')
            _texts.setdefault(ctx, set()).add(txt)

def update_locale():
    root: etree.Element
    if os.path.exists(TS_PATH):
        tree = etree.parse(TS_PATH)
        root = tree.getroot()
    else:
        root = etree.Element("TS", attrib={"version": "2.1", "language": "zh_CN"})
    for ctx, msg_set in _texts.items():
        ctx_elem = etree.SubElement(root, "context")
        etree.SubElement(ctx_elem, "name").text = ctx
        for msg in sorted(msg_set):
            msg_elem = etree.SubElement(ctx_elem, "message")
            etree.SubElement(msg_elem, "source").text = msg
            etree.SubElement(msg_elem, "translation") # 预设空翻译，等待后续人工翻译完善
    # 生成 ts 文件
    tree = etree.ElementTree(root)
    tree.write(TS_PATH, encoding="utf-8",xml_declaration=True, short_empty_elements=True)

    # dom = xml.dom.minidom.parseString(etree.tostring(root, encoding="utf-8"))
    # with open(TS_PATH, "w", encoding="utf-8") as fp:
    #     fp.write(dom.toprettyxml())
    print("Wrote", len(_texts), "contexts to", TS_PATH)


def main():
    for root, _, files in os.walk(SRC_DIR):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                print("Processing:", file_path)
                load_texts(file_path)
    update_locale()

if __name__ == "__main__":
    main()