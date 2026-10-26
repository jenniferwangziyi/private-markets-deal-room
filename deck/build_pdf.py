"""Render deck/harbourline_deal_room.md (slides separated by ---) to a 16:9 PDF with headless Chrome."""
import pathlib, subprocess, markdown
src = pathlib.Path(__file__).with_name("harbourline_deal_room.md")
slides = [markdown.markdown(s, extensions=["tables", "fenced_code"]) for s in src.read_text().split("\n---\n")]
css = """@page { size: 13.333in 7.5in; margin: 0 }
body { margin: 0; font-family: 'DM Sans', Helvetica, Arial, sans-serif; color: #0B3C49; }
.s { width: 13.333in; height: 7.5in; box-sizing: border-box; padding: 0.55in 0.75in; page-break-after: always; background: #FAF7F2; position: relative; overflow: hidden; }
.s:first-child { background: #0B3C49; color: #fff; display: flex; flex-direction: column; justify-content: center; }
.s:first-child h1 { font-size: 44px; } .s:first-child p { color: #E7D3BC; font-size: 20px; }
h1 { font-size: 34px; margin: 0 0 14px } h2 { font-size: 30px; margin: 0 0 18px; color: #0B3C49; border-left: 8px solid #C89B6D; padding-left: 14px }
p, li { font-size: 17px; line-height: 1.45 } strong { color: #1F7A8C } .s:first-child strong { color: #fff }
table { border-collapse: collapse; width: 100%; font-size: 15px; background: #fff } th { background: #0B3C49; color: #fff; text-align: left; padding: 7px 10px }
td { border-bottom: 1px solid #E5DED3; padding: 7px 10px; vertical-align: top } pre { font-size: 11.5px; background: #fff; border: 1px solid #E5DED3; padding: 12px; overflow: hidden }
em { color: #6b7280 } .foot { position: absolute; bottom: 0.25in; right: 0.75in; font-size: 11px; color: #9aa3ad }"""
html = "<html><head><meta charset='utf-8'><link href='https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap' rel='stylesheet'>" \
       f"<style>{css}</style></head><body>" + "".join(f"<div class='s'>{h}<div class='foot'>Harbourline Capital · AI deal room · {i + 1}</div></div>" for i, h in enumerate(slides)) + "</body></html>"
out_html = src.with_suffix(".html"); out_html.write_text(html)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={src.with_suffix('.pdf')}", str(out_html)], check=True, capture_output=True)
print("wrote", src.with_suffix(".pdf"), len(slides), "slides")
