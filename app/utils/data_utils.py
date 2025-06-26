import pandas as pd
import os
from PIL import Image
import io
import base64

# 读取Excel数据文件
def load_chemicals_data():
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '涂料系统数据库-V1.1.xlsx')
    try:
        df = pd.read_excel(data_path)
        print(f"成功加载数据，共{len(df)}行, 列名为: {df.columns.tolist()}")
        # 打印前几行数据以供调试
        print("数据前3行:")
        print(df.head(3))
        return df
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return None

# 根据CAS号查询化学物质
def search_chemical_by_cas(cas_number, df):
    if df is None:
        print("数据框为空，无法查询")
        return None
    
    # 去除输入中的空格
    cas_number = cas_number.strip()
    print(f"正在查询CAS号: '{cas_number}'")
    
    # 确定CAS号所在列
    cas_col = 'CAS号'  # 正确的CAS号列
    print(f"CAS号所在列: {cas_col}")
    
    # 将数据框的CAS号列转换为字符串并去除空格
    df[cas_col] = df[cas_col].astype(str).str.strip()
    
    # 打印前5个CAS号，进行检查
    # print(f"数据框中前5个CAS号: {df[cas_col].head(5).tolist()}")
    
    # 只进行精确匹配
    exact_match = df[df[cas_col] == cas_number]
    
    if len(exact_match) > 0:
        print(f"找到精确匹配结果: {len(exact_match)}行")
        return exact_match.iloc[0].to_dict()
    else:
        print(f"未找到匹配CAS号: {cas_number}")
        return None

# 获取毒性级别的说明
def get_toxicity_level_description(level):
    descriptions = {
        "1级": "基本无危害物质，可安全使用",
        "2级": "低度危害物质，可在特定条件下使用",
        "3级": "中度危害物质，建议寻找替代方案",
        "4级": "高度危害物质，应优先考虑替代"
    }
    return descriptions.get(level, "未知危害级别")

# 获取毒性级别对应的颜色
def get_toxicity_level_color(level):
    colors = {
        "1级": "#00FF00",  # 绿色
        "2级": "#FFFF00",  # 黄色
        "3级": "#FFA500",  # 橙色
        "4级": "#FF0000"   # 红色
    }
    return colors.get(level, "#CCCCCC")  # 默认灰色

# 处理结构图像数据（如果有）
def process_structure_image(structure_data):
    if pd.isna(structure_data) or structure_data == "":
        return None
    
    try:
        # 检查是否为图像数据
        if isinstance(structure_data, bytes):
            return Image.open(io.BytesIO(structure_data))
        # 检查是否为base64编码的图像
        elif isinstance(structure_data, str) and structure_data.startswith('data:image'):
            img_data = structure_data.split(',')[1]
            return Image.open(io.BytesIO(base64.b64decode(img_data)))
        else:
            return None
    except Exception as e:
        print(f"处理结构图像时出错: {e}")
        return None 