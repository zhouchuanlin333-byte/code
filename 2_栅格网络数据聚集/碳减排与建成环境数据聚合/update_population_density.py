import pandas as pd
import os

# 设置文件路径
morning_cleaned_path = 'd:/Desktop/项目论文/建模/早高峰_cleaned.csv'
morning_normalized_path = 'd:/Desktop/项目论文/建模/早高峰_标准化.csv'
evening_cleaned_path = 'd:/Desktop/项目论文/建模/晚高峰_cleaned.csv'
evening_normalized_path = 'd:/Desktop/项目论文/建模/晚高峰_标准化.csv'

# 定义更新人口密度的函数
def update_population_density(cleaned_path, normalized_path):
    print(f"正在处理: {os.path.basename(cleaned_path)} -> {os.path.basename(normalized_path)}")
    
    # 读取cleaned文件，只保留grid_id和人口密度列
    cleaned_df = pd.read_csv(cleaned_path)[['grid_id', '人口密度']]
    print(f"读取了 {len(cleaned_df)} 行cleaned数据")
    
    # 读取标准化文件
    normalized_df = pd.read_csv(normalized_path)
    print(f"读取了 {len(normalized_df)} 行标准化数据")
    
    # 创建grid_id到人口密度的映射字典
    pop_density_map = dict(zip(cleaned_df['grid_id'], cleaned_df['人口密度']))
    
    # 检查grid_id是否匹配
    cleaned_grid_ids = set(cleaned_df['grid_id'])
    normalized_grid_ids = set(normalized_df['grid_id'])
    
    if cleaned_grid_ids != normalized_grid_ids:
        print("警告: grid_id集合不匹配!")
        missing_in_cleaned = normalized_grid_ids - cleaned_grid_ids
        missing_in_normalized = cleaned_grid_ids - normalized_grid_ids
        if missing_in_cleaned:
            print(f"在标准化文件中但不在cleaned文件中的grid_id数量: {len(missing_in_cleaned)}")
        if missing_in_normalized:
            print(f"在cleaned文件中但不在标准化文件中的grid_id数量: {len(missing_in_normalized)}")
    else:
        print("grid_id集合完全匹配")
    
    # 更新人口密度列
    normalized_df['人口密度 (千人/km²)'] = normalized_df['grid_id'].map(pop_density_map)
    
    # 检查是否有任何NaN值（表示映射失败）
    na_count = normalized_df['人口密度 (千人/km²)'].isna().sum()
    if na_count > 0:
        print(f"警告: 有 {na_count} 行人口密度更新失败")
    else:
        print("所有人口密度数据更新成功")
    
    # 保存更新后的标准化文件
    normalized_df.to_csv(normalized_path, index=False)
    print(f"已保存更新后的文件: {os.path.basename(normalized_path)}")
    
    # 验证前几行数据
    print("验证更新后的前5行数据:")
    print(normalized_df[['grid_id', '人口密度 (千人/km²)']].head())
    print("\n" + "="*50 + "\n")

# 执行更新
print("开始更新人口密度数据...\n")
update_population_density(morning_cleaned_path, morning_normalized_path)
update_population_density(evening_cleaned_path, evening_normalized_path)
print("所有文件更新完成!")