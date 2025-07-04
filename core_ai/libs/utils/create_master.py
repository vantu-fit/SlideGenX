from pptx import Presentation


import zipfile
import shutil
from pptx import Presentation
import os

def remove_all_slides(pptx_path, output_path):
    # B1: Load file và xóa slides bằng python-pptx
    prs = Presentation(pptx_path)
    slide_id_list = prs.slides._sldIdLst
    while len(slide_id_list) > 0:
        slide_id_list.remove(slide_id_list[0])
    temp_pptx = output_path + "_temp.pptx"
    prs.save(temp_pptx)

    # B2: Làm sạch file .pptx (remove các slide XML mồ côi)
    with zipfile.ZipFile(temp_pptx, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w') as zout:
            for item in zin.infolist():
                # Bỏ qua slideX.xml và rels của nó nếu cần
                if item.filename.startswith("ppt/slides/slide") or item.filename.startswith("ppt/slides/_rels/slide"):
                    continue
                zout.writestr(item, zin.read(item.filename))

    os.remove(temp_pptx)
    print(f"✅ Clean template saved to: {output_path}")


# Sử dụng
if __name__ == "__main__":
    # Đường dẫn đến file PowerPoint gốc
    pptx_path = "pptx_templates/Bold-underlines.pptx"
    
    # Đường dẫn đến file PowerPoint đầu ra
    output_path = "output_template.pptx"
    
    # Gọi hàm để xóa tất cả các slide
    remove_all_slides(pptx_path, output_path)
