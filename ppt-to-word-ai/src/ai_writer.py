# 导入必要的库和模块
import os  # 操作系统相关功能，用于获取环境变量
import re  # 正则表达式库，用于文本处理

# 根据配置动态导入模型SDK
try:
    import google.generativeai as genai  # Google Gemini AI接口
except ImportError:
    genai = None

try:
    from volcenginesdkarkruntime import Ark  # 火山引擎大模型SDK
except ImportError:
    Ark = None

def clean_extracted_text(text: str) -> str:
    """清理和规范化提取的文本 - 根据反馈改进
    
    参数:
        text: 需要清理的原始文本
        
    返回:
        清理和规范化后的文本
    """
    # 删除特殊字符并规范化空格
    text = re.sub(r'\s+', ' ', text)  # 将多个空格替换为一个
    text = re.sub(r'\n\s*\n', '\n\n', text)  # 规范化多个换行符
    text = text.strip()  # 去除首尾空白
    
    # 删除无关和过短的文本片段
    lines = text.split('\n')  # 按行分割文本
    clean_lines = []  # 存储清理后的行
    
    for line in lines:
        line = line.strip()  # 去除行首尾空白
        # 过滤过短的行（少于15个字符）
        if len(line) < 15:
            continue
        # 过滤演示文稿中常见的通用内容
        if any(generic in line.lower() for generic in [
            "slide", "页面", "点击这里", "下一页", "上一页", 
            "背景", "模板", "设计", "菜单", "导航"
        ]):
            continue
        clean_lines.append(line)  # 添加有效行到结果列表
    
    return '\n'.join(clean_lines)

def generate_explanation(content: str) -> str:
    """根据配置使用AI大模型生成格式化的学术解释
    
    参数:
        content: 从PPT或PDF中提取的原始内容
        
    返回:
        AI生成的格式化学术解释文本
    """
    # 获取模型类型配置
    model_type = os.getenv('AI_MODEL_TYPE', 'gemini')  # 默认使用Gemini模型
    
    # 根据模型类型选择相应的API
    if model_type.lower() == 'gemini' and genai is not None:
        # 配置Gemini模型
        api_key = os.getenv('GEMINI_API_KEY')  # 从环境变量获取API密钥
        if not api_key:
            raise ValueError("环境变量中未设置GEMINI_API_KEY")  # 如果未设置API密钥则抛出错误
        
        # 使用API密钥配置Gemini
        genai.configure(api_key=api_key)  # 配置API密钥
        model = genai.GenerativeModel('gemini-2.5-flash')  # 创建生成式模型实例
    elif model_type.lower() == 'volcengine' and Ark is not None:
        # 配置火山引擎大模型
        api_key = os.getenv('ARK_API_KEY')
        model=os.getenv('model_id')  # 从环境变量获取API密钥
        if not api_key:
            raise ValueError("环境变量中未设置ARK_API_KEY")  # 如果未设置API密钥则抛出错误
        
        # 使用API密钥配置火山引擎大模型
        client = Ark(api_key=api_key)  # 创建火山引擎大模型客户端
    else:
        raise ValueError(f"不支持的模型类型: {model_type} 或所需SDK未安装")
    
    # 首先清理内容
    clean_content = clean_extracted_text(content)  # 清理和规范化提取的文本
    
#     prompt = f"""Eres un experto en crear material didáctico académico de alta calidad en ESPAÑOL.

# CONTENIDO A PROCESAR:
# {clean_content}

# INSTRUCCIONES CRÍTICAS PARA EXCELENCIA ACADÉMICA:

# 📋 ESTRUCTURA JERÁRQUICA OBLIGATORIA:
# - ## para títulos principales temáticos (NO por slide, sino por tema)
# - ### para subtemas lógicos  
# - #### para conceptos específicos
# - Reorganiza el contenido lógicamente, ignorando el orden original de slides
# - Crea una narrativa académica coherente y progresiva

# 🚫 ELIMINAR ABSOLUTAMENTE:
# - Repeticiones de conceptos básicos ya explicados
# - Frases genéricas sin valor específico del contenido
# - Texto de relleno o artificialmente alargado
# - Contenido fuera del material fuente
# - Explicaciones superficiales

# 💻 CÓDIGO (obligatorio si aparece):
# - Explica línea por línea el funcionamiento
# - Comenta el propósito en el contexto académico
# - No asumas conocimientos previos no justificados
# - Incluye comentarios explicativos en español

# � ENRIQUECIMIENTO PEDAGÓGICO:
# - Tablas comparativas para listas complejas
# - Viñetas (•) para conceptos clave
# - Resúmenes al final de secciones importantes
# - Ejercicios prácticos relevantes al contenido
# - Preguntas de reflexión para consolidar aprendizaje

# ✅ CALIDAD ACADÉMICA:
# - Mínimo 200 palabras por sección principal (sin relleno)
# - Profundidad real basada únicamente en el material fuente
# - Español formal pero didáctico
# - Estructura lógica que facilite el aprendizaje progresivo
# - Transiciones fluidas entre conceptos

# 🎯 OBJETIVO: Documento profesional, pedagógicamente sólido y realmente útil para el aprendizaje.
# - Progresión lógica de conceptos simples a complejos
# - Cada párrafo debe aportar valor educativo específico

# ❌ PROHIBIDO ESTRICTAMENTE:
# - Contenido genérico no relacionado con el archivo fuente
# - Repeticiones de conceptos ya cubiertos
# - Frases de relleno sin valor específico
# - Explicaciones superficiales de código
# - Desviarse del material original

# FORMATO DE SALIDA REQUERIDO:
# - Documento completamente en español
# - Estructura clara con títulos jerárquicos
# - Contenido pedagógicamente organizado
# - Sin repeticiones innecesarias
# - Enfoque en la comprensión profunda del material específico

# Genera un documento que sea una referencia académica útil, completa y pedagógicamente sólida basada ÚNICAMENTE en el contenido proporcionado."""

    prompt = f"""你是一个精通创建高质量初中学科教学材料的专家。

待处理的内容：
{clean_content}

指令：
🎯 目标：将原始PPT内容转化为一个结构化、专业、且真正有用的学习文档。

📋 结构化与重组：
- 使用 **##** 作为主要章节标题（按主题划分，而非按幻灯片划分）。
- 使用 **###** 作为逻辑子主题。
- 使用 **####** 作为具体概念或要点。
- 逻辑上重组内容，创建一个连贯、渐进的学习叙述，忽略原始幻灯片顺序。

🚫 绝对禁止：
- 重复已解释过的概念。
- 没有实质内容、只是为了凑字数的通用短语和填充词。
- 任何超出源材料范围的内容。
- 对概念的肤浅解释。
- 原始PPT中的导航词汇（如“下一页”、“点击这里”等）。

💻 代码（如果出现）：
- 逐行详细解释代码的功能和目的。
- 解释代码在整个学术背景中的作用。
- 假设读者没有先验知识，提供清晰、基础的解释。
- 在代码块中添加中文注释。

✅ 内容质量与教学方法：
- 每个主要章节至少有200字（不含填充）。
- 确保所有内容都基于且仅基于提供的源材料，进行深度分析和扩展。
- 使用正式但易于理解的中文进行写作。
- 采用项目符号（•）、列表、对比表格或总结等形式，让关键信息更易于吸收。
- 在章节末尾添加“思考题”或“小练习”，帮助读者巩固所学。

格式要求：
- 文档内容必须完全用中文书写。
- 结构清晰，采用分级标题。
- 内容组织具有教育逻辑。
- 没有不必要的重复。
- 专注于对特定学科内容的深入理解。

请根据上述所有指令，生成一份基于所提供内容的，完整且教学严谨的学术参考文档。
"""

    try:
        # 根据模型类型调用相应的API
        if model_type.lower() == 'gemini':
            # 调用Gemini模型生成内容
            response = model.generate_content(
                prompt,  # 提示词
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # 较低的温度值，使输出更保守、更可预测，适合学术内容
                    max_output_tokens=2048,  # 最大输出标记数
                    top_p=0.9  # 控制输出多样性的参数
                )
            )
            return response.text  # 返回生成的文本
        elif model_type.lower() == 'volcengine':
            # 调用火山引擎大模型生成内容
            response = client.chat.completions.create(
                model = os.getenv('model_id'),
                messages=[
                    {"role": "user", "content":f"{prompt}"}
                ],
                thinking={"type": "disabled"},
                temperature=0.3,  # 较低的温度值，使输出更保守、更可预测，适合学术内容
                top_p=0.9  # 控制输出多样性的参数
            )
            return response.choices[0].message.content  # 返回生成的文本
    except Exception as e:
        # 错误处理机制
        return f"AI内容生成错误: {str(e)}\n\n原始内容:\n{clean_content}"  # 返回错误信息和原始内容