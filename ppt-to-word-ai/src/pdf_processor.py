# 导入必要的库和模块
import fitz  # PyMuPDF，用于PDF文件处理
from pdf2image import convert_from_bytes  # 用于将PDF转换为图像
import pytesseract  # 用于OCR（光学字符识别）
from PIL import Image  # Python图像处理库
import io  # 用于处理二进制流数据

def extract_text_from_pdf(file_path: str) -> list:
    """从PDF中提取结构化文本和图像
    
    参数:
        file_path: PDF文件的路径
        
    返回:
        包含页面数据的列表，每个页面包含文本内容和图像
    """
    doc = fitz.open(file_path)  # 打开PDF文档
    pages_data = []  # 存储所有页面数据的列表
    
    for page_num in range(len(doc)):  # 遍历PDF中的每一页
        page = doc.load_page(page_num)  # 加载当前页面
        page_data = {  # 创建当前页面的数据结构
            "page_number": page_num+1,  # 页码（从1开始）
            "content": [],  # 存储文本内容
            "images": []  # 存储图像数据
        }
        
        # 提取文本内容
        text = page.get_text("text")  # 获取页面中的文本
        if text.strip():  # 如果文本不为空（去除空白后）
            page_data["content"].append({  # 添加到内容列表
                "type": "text",  # 类型为文本
                "data": text  # 文本数据
            })
        
        # 处理页面中的图像
        for img in page.get_images():  # 遍历页面中的所有图像
            try:
                base_image = doc.extract_image(img[0])  # 提取图像数据
                image_bytes = base_image["image"]  # 获取图像的二进制数据
                
                # 对图像进行OCR（光学字符识别）
                text = pytesseract.image_to_string(Image.open(io.BytesIO(image_bytes)))  # 将图像转换为文本
                page_data["images"].append({  # 添加到图像列表
                    "image": image_bytes,  # 图像二进制数据
                    "text": text.strip()  # OCR识别出的文本（去除空白）
                })
            except Exception as e:
                print(f"处理PDF图像时出错: {e}")  # 打印图像处理错误信息
        
        pages_data.append(page_data)
    
    return pages_data