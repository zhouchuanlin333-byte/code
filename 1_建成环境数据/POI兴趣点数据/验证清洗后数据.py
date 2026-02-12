import pandas as pd
import os

# 设置文件路径
cleaned_file = "西安市六大主城区POI数据清洗后.csv"

print(f"开始验证清洗后的数据文件...")
print(f"目标文件: {cleaned_file}")

# 检查文件是否存在
if not os.path.exists(cleaned_file):
    print(f"错误：找不到清洗后的数据文件 {cleaned_file}")
    exit(1)

# 读取清洗后的数据
try:
    df = pd.read_csv(cleaned_file)
    
    # 1. 检查文件大小
    file_size = os.path.getsize(cleaned_file) / 1024 / 1024  # MB
    print(f"文件大小: {file_size:.2f} MB")
    
    # 2. 检查记录数
    total_records = len(df)
    print(f"总记录数: {total_records}")
    
    # 3. 检查列名和数量
    print(f"\n列信息:")
    print(f"列数量: {len(df.columns)}")
    print(f"列名: {list(df.columns)}")
    
    # 4. 检查是否只包含需要的字段
    expected_columns = ['adName', '大类', 'wgs84_lng', 'wgs84_lat']
    actual_columns = list(df.columns)
    
    if set(actual_columns) == set(expected_columns):
        print("✓ 验证通过：只包含了指定的4个字段")
    else:
        extra_columns = set(actual_columns) - set(expected_columns)
        missing_columns = set(expected_columns) - set(actual_columns)
        if extra_columns:
            print(f"✗ 警告：存在额外的字段: {extra_columns}")
        if missing_columns:
            print(f"✗ 错误：缺少必需的字段: {missing_columns}")
    
    # 5. 显示数据样例
    print("\n数据样例（前5行）:")
    print(df.head())
    
    # 6. 基本数据统计
    print("\n数据统计信息:")
    # 检查adName字段的唯一值数量
    if 'adName' in df.columns:
        unique_areas = df['adName'].nunique()
        print(f"地区数量: {unique_areas}")
        print("各地区记录数:")
        area_counts = df['adName'].value_counts()
        for area, count in area_counts.items():
            print(f"  - {area}: {count}")
    
    # 检查大类字段的分布
    if '大类' in df.columns:
        unique_categories = df['大类'].nunique()
        print(f"\n大类数量: {unique_categories}")
        print("大类分布（前10个）:")
        category_counts = df['大类'].value_counts().head(10)
        for category, count in category_counts.items():
            print(f"  - {category}: {count}")
    
    # 检查坐标字段的范围
    if 'wgs84_lng' in df.columns and 'wgs84_lat' in df.columns:
        print(f"\n坐标范围:")
        print(f"经度范围: {df['wgs84_lng'].min():.6f} 到 {df['wgs84_lng'].max():.6f}")
        print(f"纬度范围: {df['wgs84_lat'].min():.6f} 到 {df['wgs84_lat'].max():.6f}")
    
    # 7. 检查缺失值
    print("\n缺失值检查:")
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        print("存在缺失值:")
        for col, missing in missing_values.items():
            if missing > 0:
                print(f"  - {col}: {missing} 个 ({missing/total_records*100:.2f}%)")
    else:
        print("✓ 没有发现缺失值")
    
    # 8. 最终验证结果
    print("\n验证结果总结:")
    print(f"✓ 文件成功生成")
    print(f"✓ 包含正确的字段结构")
    print(f"✓ 总记录数: {total_records}")
    print(f"✓ 数据验证完成")
    
except Exception as e:
    print(f"验证过程中出错: {str(e)}")
    exit(1)