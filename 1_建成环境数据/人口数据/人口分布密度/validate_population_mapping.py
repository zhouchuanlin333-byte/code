import pandas as pd
import numpy as np
import os

# 文件路径
original_pop_path = r"D:\Desktop\项目论文\人口数据\人口分布密度\global_landsat_processing\tmp\fishnet_population.csv"
mapped_pop_path = r"D:\Desktop\项目论文\人口数据\人口分布密度\gridid_population_density.csv"

print("开始验证人口密度数据匹配的准确性和合理性...")

# 读取原始数据
print(f"读取原始人口密度数据: {os.path.basename(original_pop_path)}")
original_data = pd.read_csv(original_pop_path)

# 读取映射后的数据
print(f"读取映射后人口密度数据: {os.path.basename(mapped_pop_path)}")
mapped_data = pd.read_csv(mapped_pop_path)

# 1. 基本信息验证
print("\n=== 基本信息验证 ===")
print(f"原始数据记录数: {len(original_data)}")
print(f"映射后数据记录数: {len(mapped_data)}")
print(f"渔网网格数量: {mapped_data['grid_id'].nunique()}")

# 2. 人口密度统计对比
print("\n=== 人口密度统计对比 ===")

# 原始数据统计
orig_density_stats = {
    '最大值': original_data['人口密度'].max(),
    '最小值': original_data['人口密度'].min(),
    '平均值': original_data['人口密度'].mean(),
    '非零网格数': (original_data['人口密度'] > 0).sum(),
    '总人口数': original_data['总人口数'].sum()
}

# 映射后数据统计
mapped_density_stats = {
    '最大值': mapped_data['population_density'].max(),
    '最小值': mapped_data['population_density'].min(),
    '平均值': mapped_data['population_density'].mean(),
    '非零网格数': (mapped_data['population_density'] > 0).sum(),
    '总人口数': mapped_data['total_population'].sum()
}

# 打印统计信息
print("原始数据统计:")
for key, value in orig_density_stats.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.2f}")
    else:
        print(f"  {key}: {value}")

print("\n映射后数据统计:")
for key, value in mapped_density_stats.items():
    if isinstance(value, float):
        print(f"  {key}: {value:.2f}")
    else:
        print(f"  {key}: {value}")

# 3. 检查映射关系正确性（抽样检查）
print("\n=== 映射关系抽样检查 ===")
# 随机抽取5个网格ID进行检查
sample_grid_ids = np.random.choice(mapped_data['grid_id'], size=min(5, len(mapped_data)), replace=False)

print("抽样检查结果:")
for grid_id in sample_grid_ids:
    fid = grid_id - 1
    if fid < len(original_data):
        orig_density = original_data.iloc[fid]['人口密度']
        mapped_density = mapped_data[mapped_data['grid_id'] == grid_id]['population_density'].values[0]
        match = "✓ 匹配" if abs(orig_density - mapped_density) < 1e-6 else "✗ 不匹配"
        print(f"  grid_id={grid_id}, FID={fid}: 原始密度={orig_density}, 映射密度={mapped_density} {match}")

# 4. 人口分布合理性分析
print("\n=== 人口分布合理性分析 ===")

# 计算人口密度分布的分位数
percentiles = [5, 25, 50, 75, 95, 99]
mapped_percentiles = np.percentile(mapped_data['population_density'], percentiles)

print("映射后人口密度分位数分布:")
for p, v in zip(percentiles, mapped_percentiles):
    print(f"  {p}%分位数: {v:.2f}")

# 分析非零人口密度网格的空间分布
non_zero_grids = mapped_data[mapped_data['population_density'] > 0]
high_density_grids = mapped_data[mapped_data['population_density'] > mapped_data['population_density'].mean()]
very_high_density_grids = mapped_data[mapped_data['population_density'] > mapped_data['population_density'].quantile(0.9)]

print(f"\n高密度网格分布:")
print(f"  非零人口密度网格数: {len(non_zero_grids)} ({len(non_zero_grids)/len(mapped_data)*100:.1f}%)")
print(f"  高于平均密度网格数: {len(high_density_grids)} ({len(high_density_grids)/len(mapped_data)*100:.1f}%)")
print(f"  高于90%分位数密度网格数: {len(very_high_density_grids)} ({len(very_high_density_grids)/len(mapped_data)*100:.1f}%)")

# 5. 总人口合理性检查
print("\n=== 总人口合理性检查 ===")
print(f"映射后总人口数: {mapped_density_stats['总人口数']:.2f}")
print(f"按照500米网格面积(0.25平方公里)计算的平均人口密度: {mapped_density_stats['总人口数']/(len(mapped_data)*0.25):.2f} 人/平方公里")

# 6. 总结评估
print("\n=== 总结评估 ===")
if len(mapped_data) == 3150:
    print("✓ 渔网网格数量正确，共3150个网格")
else:
    print("✗ 渔网网格数量不正确")

if abs(mapped_density_stats['总人口数'] - orig_density_stats['总人口数'] * (len(mapped_data)/len(original_data))) / orig_density_stats['总人口数'] < 0.05:
    print("✓ 总人口数在合理范围内")
else:
    print("! 总人口数存在较大偏差")

if mapped_density_stats['非零网格数'] > 0:
    print("✓ 存在非零人口密度网格，数据分布合理")
else:
    print("✗ 没有非零人口密度网格，数据异常")

print("\n数据验证完成！")