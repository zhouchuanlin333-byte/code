import pandas as pd
import os

# 设置文件路径
input_file = "西安市六大主城区POI数据汇总.csv"
output_file = "西安市六大主城区POI数据清洗后.csv"

print(f"开始清洗POI数据，只保留指定字段...")
print(f"输入文件: {input_file}")

# 检查输入文件是否存在
if not os.path.exists(input_file):
    print(f"错误：找不到输入文件 {input_file}")
    exit(1)

# 读取原始数据
try:
    # 先读取少量数据来检查列名
    sample_data = pd.read_csv(input_file, nrows=5)
    print(f"原始数据列名: {list(sample_data.columns)}")
    
    # 读取完整数据
    df = pd.read_csv(input_file)
    print(f"成功读取数据，总记录数: {len(df)}")
    
    # 检查所需字段是否存在
    required_columns = ['adName', '大类', 'wgs84_lng', 'wgs84_lat']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"错误：缺少以下必需字段: {missing_columns}")
        # 尝试使用备用列名（例如adname的小写形式）
        if 'adName' in missing_columns:
            if 'adname' in df.columns:
                print("注意：使用小写的'adname'替代'adName'")
                df = df.rename(columns={'adname': 'adName'})
                required_columns = ['adName', '大类', 'wgs84_lng', 'wgs84_lat']
            else:
                print("错误：找不到'adName'或'adname'字段")
                exit(1)
    
    # 选择需要保留的字段
    df_cleaned = df[required_columns]
    print(f"成功筛选数据，保留字段: {required_columns}")
    print(f"清洗后数据记录数: {len(df_cleaned)}")
    
    # 保存清洗后的数据
    df_cleaned.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"清洗完成！结果已保存至: {output_file}")
    
    # 显示清洗后数据的前几行
    print("\n清洗后数据的前5行:")
    print(df_cleaned.head())
    
    # 显示文件大小
    file_size = os.path.getsize(output_file) / 1024 / 1024  # MB
    print(f"\n输出文件大小: {file_size:.2f} MB")
    
    # 统计每个区的数据量
    if 'adName' in df_cleaned.columns:
        print("\n各区域数据统计:")
        area_counts = df_cleaned['adName'].value_counts()
        for area, count in area_counts.items():
            print(f"{area}: {count} 条")
            
except Exception as e:
    print(f"处理数据时出错: {str(e)}")
    exit(1)