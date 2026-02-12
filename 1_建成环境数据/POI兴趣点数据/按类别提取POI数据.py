import pandas as pd
import os
import time

# 设置文件路径
input_file = "D:\\Desktop\\项目论文\\POI兴趣点数据\\西安市六大主城区POI数据清洗后.csv"
output_dir = "D:\\Desktop\\项目论文\\POI兴趣点数据\\5类兴趣点"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

print("开始按类别提取POI数据...")
start_time = time.time()

# 定义POI分类映射规则
poi_categories = {
    "休闲POI": ["餐饮服务", "购物服务", "体育休闲服务"],
    "办公POI": ["公司企业", "政府机构及社会团体"],
    "公共服务POI": ["生活服务", "汽车服务", "医疗保健服务", "公共设施"],
    "交通设施POI": ["交通设施服务", "通行设施"],
    "居住POI": ["住宿服务", "商务住宅"]
}

print("POI分类规则:")
for category, subcategories in poi_categories.items():
    print(f"- {category}: {', '.join(subcategories)}")

try:
    # 读取CSV文件
    print("\n读取POI数据文件...")
    df = pd.read_csv(input_file)
    print(f"成功读取文件，共 {len(df)} 条记录")
    
    # 验证必要字段是否存在
    required_columns = ['adName', '大类', 'wgs84_lng', 'wgs84_lat']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"文件中缺少必要字段: {col}")
    
    # 创建结果字典
    results = {}
    stats = []
    
    # 提取各类别数据
    for category_name, subcategories in poi_categories.items():
        print(f"\n提取{category_name}数据...")
        
        # 筛选属于当前类别的数据
        filtered_df = df[df['大类'].isin(subcategories)]
        
        # 只保留需要的字段
        result_df = filtered_df[['adName', '大类', 'wgs84_lng', 'wgs84_lat']]
        
        # 保存结果
        output_file = os.path.join(output_dir, f"{category_name}_数据.csv")
        result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        results[category_name] = result_df
        
        # 统计信息
        count = len(result_df)
        stats.append({
            '类别名称': category_name,
            '包含子类': ', '.join(subcategories),
            '数据量': count,
            '文件路径': output_file
        })
        
        print(f"{category_name}数据提取完成，共 {count} 条记录，已保存到: {output_file}")
    
    # 打印总体统计信息
    print("\n" + "="*60)
    print("POI数据分类提取统计信息")
    print("="*60)
    total_extracted = 0
    for stat in stats:
        print(f"类别: {stat['类别名称']}")
        print(f"  子类: {stat['包含子类']}")
        print(f"  数量: {stat['数据量']}")
        print(f"  文件: {stat['文件路径']}")
        print("-" * 60)
        total_extracted += stat['数据量']
    
    # 计算未分类数据
    total_original = len(df)
    unclassified = total_original - total_extracted
    print(f"\n原始数据总数: {total_original}")
    print(f"已分类数据总数: {total_extracted}")
    print(f"未分类数据数量: {unclassified}")
    
    # 如果有未分类数据，分析未分类的类别
    if unclassified > 0:
        classified_subcategories = []
        for sublist in poi_categories.values():
            classified_subcategories.extend(sublist)
        
        unclassified_df = df[~df['大类'].isin(classified_subcategories)]
        unclassified_categories = unclassified_df['大类'].value_counts()
        
        print(f"\n未分类的POI类别:")
        for category, count in unclassified_categories.items():
            print(f"  - {category}: {count}")
        
        # 保存未分类数据（可选）
        unclassified_file = os.path.join(output_dir, "未分类POI数据.csv")
        unclassified_df.to_csv(unclassified_file, index=False, encoding='utf-8-sig')
        print(f"\n未分类数据已保存到: {unclassified_file}")
    
    # 保存分类规则和统计信息
    stats_file = os.path.join(output_dir, "POI分类规则与统计信息.txt")
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("西安市六大主城区POI数据分类规则与统计信息\n")
        f.write("="*80 + "\n\n")
        
        f.write("一、POI分类规则\n")
        f.write("="*80 + "\n")
        for category, subcategories in poi_categories.items():
            f.write(f"{category}:\n")
            for subcategory in subcategories:
                f.write(f"  - {subcategory}\n")
            f.write("\n")
        
        f.write("二、分类统计信息\n")
        f.write("="*80 + "\n")
        for stat in stats:
            f.write(f"类别: {stat['类别名称']}\n")
            f.write(f"子类: {stat['包含子类']}\n")
            f.write(f"数量: {stat['数据量']}\n")
            f.write(f"文件: {stat['文件路径']}\n")
            f.write("-" * 80 + "\n")
        
        f.write(f"\n原始数据总数: {total_original}\n")
        f.write(f"已分类数据总数: {total_extracted}\n")
        f.write(f"未分类数据数量: {unclassified}\n")
    
    print(f"\n分类规则和统计信息已保存到: {stats_file}")
    
    end_time = time.time()
    print(f"\nPOI数据分类提取完成！总耗时: {end_time - start_time:.2f} 秒")
    
except Exception as e:
    print(f"处理过程中出错: {e}")
    import traceback
    traceback.print_exc()

print("\n程序执行结束！")