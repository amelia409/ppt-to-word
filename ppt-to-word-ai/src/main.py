# 导入必要的库和模块
import os  # 操作系统相关功能，用于文件路径处理和目录创建
from flask import Flask, request, jsonify, send_file, render_template  # Flask Web框架相关组件
# 导入自定义模块
from src.ppt_processor import extract_structured_content  # PPT处理模块，用于提取PPT内容
from src.pdf_processor import extract_text_from_pdf  # PDF处理模块，用于提取PDF内容
from src.ai_writer import generate_explanation  # AI写作模块，用于生成解释内容
from src.word_generator import create_word_document  # Word生成模块，用于创建Word文档

# 创建Flask应用实例
app = Flask(__name__, 
           static_folder='../static',  # 静态文件目录
           template_folder='../templates')  # 模板文件目录

# Docker环境下的绝对路径配置
# 设置基础目录、输入文件目录和输出文件目录
BASE_DIR = "/app"  # Docker容器内的应用根目录
INPUT_DIR = os.path.join(BASE_DIR, "assets", "input")  # 上传文件存储目录
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "output")  # 生成文件存储目录

# 定义根路由，返回前端页面
@app.route('/')
def home():
    # 返回前端页面
    return render_template('index.html')

# 定义API状态路由
@app.route('/api/status')
def api_status():
    # 返回JSON格式的API信息，包括状态和可用的API端点
    return jsonify({
        "status": "API正常运行",  # API状态信息
        "endpoints": {  # 可用的API端点列表
            "处理文件": "POST /process",  # 用于上传和处理文件的端点
            "下载文件": "GET /download/<filename>"  # 用于下载生成文件的端点
        }
    })

# 定义处理文件的路由，只接受POST请求
@app.route('/process', methods=['POST'])
def process_file():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        # 如果没有文件，返回400错误
        return jsonify({"error": "未上传文件"}), 400  # 400表示客户端错误
    
    # 获取上传的文件对象
    file = request.files['file']
    # 检查文件名是否为空
    if file.filename == '':
        # 如果文件名为空，返回400错误
        return jsonify({"error": "文件名无效"}), 400
    
    # 验证文件扩展名是否为支持的格式
    valid_extensions = ('.pptx', '.ppt', '.pdf')  # 支持的文件格式列表
    if not file.filename.lower().endswith(valid_extensions):
        # 如果文件格式不支持，返回400错误
        return jsonify({"error": "仅支持PPT、PPTX或PDF格式"}), 400
    
    # 创建目录（使用绝对路径）
    # 确保输入和输出目录存在，不存在则创建
    os.makedirs(INPUT_DIR, exist_ok=True)  # exist_ok=True表示目录已存在也不报错
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 构建临时文件路径并保存上传的文件
    temp_path = os.path.join(INPUT_DIR, file.filename)  # 完整的文件保存路径
    file.save(temp_path)  # 将上传的文件保存到临时路径
    
    try:
        # 根据文件类型进行不同处理
        if file.filename.lower().endswith('.pdf'):
            # 如果是PDF文件，使用PDF处理器提取文本
            # extract_text_from_pdf函数会解析PDF文件并提取其中的文本内容
            content = extract_text_from_pdf(temp_path)
        else:
            # 如果是PPT/PPTX文件，使用PPT处理器提取结构化内容
            # extract_structured_content函数会解析PPT文件并提取其中的文本、图片和结构信息
            content = extract_structured_content(temp_path)
        
        # 生成Word文档
        # 将提取的内容传递给Word生成器，创建格式化的文档
        # create_word_document函数接收提取的内容和原始文件名，生成格式化的Word文档
        # 并返回生成的Word文档路径
        output_path = create_word_document(content, file.filename)
        
        # 返回成功响应
        # 从输出路径中提取文件名（不包含路径）
        output_filename = os.path.basename(output_path)
        return jsonify({
            "success": True,  # 处理状态
            "download_url": f"/download/{output_filename}",  # 生成的下载链接，指向download路由
            "output_file": output_filename  # 生成的文件名
        })
    
    except Exception as e:
        # 捕获处理过程中的任何异常
        app.logger.error(f"处理错误: {str(e)}")  # 记录错误日志
        # 返回JSON格式的错误响应，包含错误信息和详细说明
        return jsonify({
            "error": "文件处理错误",  # 错误类型
            "details": str(e)  # 错误详情
        }), 500  # 500表示服务器内部错误
    finally:
        # 无论处理成功还是失败，都会执行finally块中的代码
        # 清理临时文件，避免占用磁盘空间
        if os.path.exists(temp_path):
            os.remove(temp_path)  # 删除临时上传的文件

# 定义下载文件的路由，接受文件名作为URL参数
@app.route('/download/<filename>')
def download_file(filename):
    # 构建完整的文件路径
    file_path = os.path.join(OUTPUT_DIR, filename)
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 如果文件存在，使用Flask的send_file函数发送文件
        # as_attachment=True参数会让浏览器下载文件而不是在浏览器中打开
        return send_file(file_path, as_attachment=True)
    # 如果文件不存在，记录错误并返回404错误
    app.logger.error(f"文件未找到: {file_path}")  # 记录错误日志
    return jsonify({"error": "文件未找到"}), 404  # 404表示资源未找到

# 程序入口点，只有直接运行此文件时才会执行
if __name__ == '__main__':
    # 启动Flask应用
    # host='0.0.0.0'表示监听所有网络接口，允许外部访问
    # port=5000指定服务运行的端口号
    app.run(host='0.0.0.0', port=5000)