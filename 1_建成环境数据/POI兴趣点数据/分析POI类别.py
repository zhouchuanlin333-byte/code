import pandas as pd

# 设置文件路径
file_path = "D:\\Desktop\\项目论文\\POI兴趣点数据\\西安市六大主城区POI数据清洗后.csv"

print("开始分析POI数据中的大类字段...")

try:
    # 读取CSV文件
    df = pd.read_csv(file_path)
    print(f"成功读取文件，共 {len(df)} 条记录")
    
    # 显示数据的基本信息
    print("\n数据基本信息:")
    print(df.info())
    
    # 显示字段名称
    print("\n字段名称:")
    print(df.columns.tolist())
    
    # 获取所有唯一的大类值
    unique_categories = df['大类'].unique()
    print(f"\n发现 {len(unique_categories)} 个不同的POI大类:")
    for i, category in enumerate(sorted(unique_categories), 1):
        print(f"{i}. {category}")
    
    # 统计每个大类的数量
    category_counts = df['大类'].value_counts()
    print("\n各类别数量统计:")
    print(category_counts)
    
    # 保存类别统计结果到文件
    output_file = "D:\\Desktop\\项目论文\\POI兴趣点数据\\POI类别统计.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("西安市六大主城区POI数据类别统计\n")
        f.write("="*50 + "\n\n")
        f.write("各POI大类列表:\n")
        for i, category in enumerate(sorted(unique_categories), 1):
            f.write(f"{i}. {category}\n")
        
        f.write("\n" + "="*50 + "\n\n")
        f.write("各类别数量统计:\n")
        for category, count in category_counts.items():
            f.write(f"{category}: {count}\n")
    
    print(f"\n统计结果已保存到: {output_file}")
    
    # 显示数据样例
    print("\n数据样例:")
    print(df.head(10))
    
except Exception as e:
    print(f"分析过程中出错: {e}")

print("\nPOI类别分析完成！")