import pandas as pd
import os

# 设置文件路径
input_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点"
input_file = os.path.join(input_dir, "网格POI数量统计.csv")
output_file = os.path.join(input_dir, "网格POI密度统计.csv")

print("开始计算POI密度...")
print(f"输入文件: {input_file}")

# 网格面积（平方千米）
grid_area_km2 = 0.25
print(f"每个网格面积: {grid_area_km2} km²")

# 读取之前的统计结果
try:
    print("\n读取网格POI数量统计数据...")
    grid_stats = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"数据读取成功，共{len(grid_stats)}个网格")
    print(f"数据字段: {list(grid_stats.columns)}")
    
    # 显示前5行数据
    print("\n原始统计数据样例:")
    print(grid_stats.head())
    
except Exception as e:
    print(f"读取数据时出错: {e}")
    exit(1)

# 定义POI类型列表
poi_types = ["休闲POI", "办公POI", "公共服务POI", "交通设施POI", "居住POI"]

# 计算密度
density_results = grid_stats.copy()
print("\n计算各类POI密度...")

# 计算每类POI的密度
for poi_type in poi_types:
    if poi_type in density_results.columns:
        # 密度 = 数量 / 面积
        density_col = f"{poi_type}_密度"
        density_results[density_col] = density_results[poi_type] / grid_area_km2
        print(f"计算 {poi_type} 密度")

# 计算总POI密度
if '总POI数量' in density_results.columns:
    density_results['总POI密度'] = density_results['总POI数量'] / grid_area_km2
    print("计算总POI密度")

# 重新排序列，将ID放在前面
columns_order = ['grid_id'] + poi_types + [f"{pt}_密度" for pt in poi_types] + ['总POI数量', '总POI密度']
# 过滤掉不存在的列
columns_order = [col for col in columns_order if col in density_results.columns]

density_results = density_results[columns_order]

# 显示密度计算结果样例
print("\n密度计算结果样例:")
print(density_results[['grid_id', '总POI数量', '总POI密度'] + [f"{pt}_密度" for pt in poi_types]].head())

# 统计密度分布情况
print("\n密度分布统计:")
print(f"平均总POI密度: {density_results['总POI密度'].mean():.2f} 个/km²")
print(f"最大总POI密度: {density_results['总POI密度'].max():.2f} 个/km²")
print(f"最小总POI密度: {density_results['总POI密度'].min():.2f} 个/km²")
print(f"中位数总POI密度: {density_results['总POI密度'].median():.2f} 个/km²")

# 统计每类POI的平均密度
for poi_type in poi_types:
    density_col = f"{poi_type}_密度"
    if density_col in density_results.columns:
        avg_density = density_results[density_col].mean()
        print(f"平均{poi_type}密度: {avg_density:.2f} 个/km²")

# 保存密度统计结果
print(f"\n保存密度统计结果到: {output_file}")
density_results.to_csv(output_file, index=False, encoding='utf-8-sig')

# 生成只包含密度信息的简化版本
density_only = density_results[['grid_id'] + [f"{pt}_密度" for pt in poi_types] + ['总POI密度']]
density_only_file = os.path.join(input_dir, "网格POI密度_only.csv")
density_only.to_csv(density_only_file, index=False, encoding='utf-8-sig')
print(f"密度信息简化版本保存到: {density_only_file}")

print("\nPOI密度计算任务完成！")
