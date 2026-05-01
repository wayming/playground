import pdfplumber
import fitz
import os
import sys
import re
import json

def radical_scan(pdf_path):
    print(f"🚀 启动激进扫描模式: {pdf_path}")
    chapters = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # 扫描前 10 页，范围扩大
        for i in range(min(10, len(pdf.pages))):
            page = pdf.pages[i]
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # 正则 1：匹配 "标题 123"（末尾是数字且与文字有空格）
                match = re.search(r'^([A-Za-z\s&,]{3,})\s+(\d+)$', line)
                # 正则 2：匹配 "123 标题"（某些 ASX 报告页码在左边）
                match_rev = re.search(r'^(\d+)\s+([A-Za-z\s&,]{3,})$', line)
                
                if match:
                    title, p_num = match.group(1).strip(), int(match.group(2))
                    if p_num > i + 1: # 排除指向当前页之前的页码
                        chapters.append({"title": title, "start_page": p_num})
                elif match_rev:
                    p_num, title = int(match_rev.group(1)), match_rev.group(2).strip()
                    if p_num > i + 1:
                        chapters.append({"title": title, "start_page": p_num})

    # 去重并排序
    unique_chaps = []
    seen_pages = set()
    # 按页码排序后去重，保留第一个发现的标题
    for c in sorted(chapters, key=lambda x: x['start_page']):
        if c['start_page'] not in seen_pages and c['start_page'] <= 1000: # 1000页安全阈值
            unique_chaps.append(c)
            seen_pages.add(c['start_page'])
            
    return unique_chaps

def split_execution(pdf_path, chapters):
    if not chapters:
        print("🛑 依然无法识别。请运行以下命令检查是否有文字层：")
        print(f"python3 -c \"import fitz; print(fitz.open('{pdf_path}')[0].get_text())\"")
        return

    doc = fitz.open(pdf_path)
    output_dir = "split_chapters"
    os.makedirs(output_dir, exist_ok=True)
    
    summary = {}
    for i, chap in enumerate(chapters):
        start = chap['start_page']
        end = chapters[i+1]['start_page'] - 1 if i+1 < len(chapters) else doc.page_count
        
        if start > doc.page_count: continue
        
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=start-1, to_page=min(end-1, doc.page_count-1))
        
        name = "".join(filter(str.isalnum, chap['title'][:20])) # 取前20个字符做文件名
        fname = f"CH{i+1:02d}_P{start}_{name}.pdf"
        path = os.path.join(output_dir, fname)
        new_doc.save(path)
        new_doc.close()
        summary[chap['title']] = {"range": [start, end], "file": path}
        print(f"✅ 生成章节: {fname}")
        
    doc.close()

if __name__ == "__main__":
    p = sys.argv[1]
    chaps = radical_scan(p)
    split_execution(p, chaps)