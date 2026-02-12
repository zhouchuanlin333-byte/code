import pandas as pd
import os

# 设置文件路径
input_dir = 'd:/Desktop/项目论文/建模'
output_dir = 'd:/Desktop/项目论文/建模/特征工程'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 定义要删除的列
drop_columns = ['grid_id', '休闲POI数量 (个)', '公共服务POI数量 (个)', '交通设施POI数量 (个)']

def process_data(file_name):
    """处理数据文件，删除指定列"""
    input_path = os.path.join(input_dir, file_name)
    
    # 读取数据
    df = pd.read_csv(input_path, encoding='utf-8')
    print(f"读取文件 {file_name}，原始列数：{len(df.columns)}")
    print(f"原始列名：{list(df.columns)}")
    
    # 删除指定列
    df_cleaned = df.drop(columns=drop_columns, errors='ignore')
    print(f"处理后列数：{len(df_cleaned.columns)}")
    print(f"处理后列名：{list(df_cleaned.columns)}")
    print(f"数据行数：{len(df_cleaned)}")
    
    # 保存处理后的数据
    output_file_name = f"优化后_{file_name}"
    output_path = os.path.join(output_dir, output_file_name)
    df_cleaned.to_csv(output_path, index=False, encoding='utf-8')
    print(f"保存优化后的数据到：{output_path}")
    
    return df_cleaned

# 处理早高峰数据
early_peak = process_data('早高峰_标准化_utf8.csv')
print("\n" + "="*50 + "\n")

# 处理晚高峰数据
late_peak = process_data('晚高峰_标准化_utf8.csv')

print("\n" + "="*50)
print("数据处理完成！")
print(f"早高峰数据处理后特征数：{len(early_peak.columns) - 1}（不包括目标变量）")
print(f"晚高峰数据处理后特征数：{len(late_peak.columns) - 1}（不包括目标变量）")
