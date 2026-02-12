import pandas as pd
import numpy as np
import os

# 文件路径
input_500m_csv = "D:\Desktop\项目论文\西安市主城区人口密度_500m网格.csv"
input_1km_csv = "D:\Desktop\项目论文\最新西安市主城区人口密度_1km网格.csv"
output_image = "D:\Desktop\项目论文\西安市主城区人口密度分布_500m网格.png"

print("=== 验证500米人口密度分布图效果 ===\n")

# 1. 检查文件是否存在
print("1. 检查输出文件是否存在...")
file_exists = os.path.exists(output_image)
print(f"   分布图文件存在: {file_exists}")
print(f"   文件路径: {output_image}")
if file_exists:
    file_size = os.path.getsize(output_image) / (1024 * 1024)  # 转换为MB
    print(f"   文件大小: {file_size:.2f} MB")
print()

# 2. 检查500米网格数据
print("2. 检查500米网格数据...")
df_500m = pd.read_csv(input_500m_csv)
print(f"   数据行数: {len(df_500m)}")
print(f"   数据列: {list(df_500m.columns)}")
print()

# 3. 数据统计
print("3. 数据统计分析...")

# 人口密度统计
pop_density = df_500m['population_density']
print(f"   人口密度统计:")
print(f"     - 最小值: {pop_density.min():.2f} 人/km²")
print(f"     - 最大值: {pop_density.max():.2f} 人/km²")
print(f"     - 平均值: {pop_density.mean():.2f} 人/km²")
print(f"     - 中位数: {pop_density.median():.2f} 人/km²")
print()

# 人口统计
total_pop_500m = df_500m['total_population'].sum()
print(f"   人口统计:")
print(f"     - 总人口: {total_pop_500m:.0f}")
print(f"     - 非零人口网格数: {(pop_density > 0).sum()}")
print(f"     - 零人口网格数: {(pop_density == 0).sum()}")
print()

# 4. 检查网格尺寸一致性
print("4. 检查网格尺寸一致性...")
grid_widths = df_500m['maxx'] - df_500m['minx']
grid_heights = df_500m['maxy'] - df_500m['miny']
print(f"   网格宽度统计:")
print(f"     - 平均值: {grid_widths.mean():.2f} 米")
print(f"     - 标准差: {grid_widths.std():.6f} 米")
print(f"     - 最小/最大值: {grid_widths.min():.2f} / {grid_widths.max():.2f} 米")
print(f"   网格高度统计:")
print(f"     - 平均值: {grid_heights.mean():.2f} 米")
print(f"     - 标准差: {grid_heights.std():.6f} 米")
print(f"     - 最小/最大值: {grid_heights.min():.2f} / {grid_heights.max():.2f} 米")
print()

# 5. 对比1km和500m网格总人口
print("5. 数据一致性验证...")
if os.path.exists(input_1km_csv):
    df_1km = pd.read_csv(input_1km_csv)
    total_pop_1km = df_1km['total_population'].sum()
    print(f"   1km网格总人口: {total_pop_1km:.0f}")
    print(f"   500m网格总人口: {total_pop_500m:.0f}")
    diff_percent = abs(total_pop_500m - total_pop_1km) / total_pop_1km * 100 if total_pop_1km > 0 else 0
    print(f"   人口差异: {total_pop_500m - total_pop_1km:.0f} ({diff_percent:.4f}%)")
    print(f"   数据一致性: {'良好' if diff_percent < 0.1 else '需要注意'}")
else:
    print(f"   警告: 未找到1km网格数据文件: {input_1km_csv}")
print()

# 6. 检查人口密度分布合理性
print("6. 人口密度分布合理性检查...")
# 计算人口密度分位数
quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
density_quantiles = pop_density.quantile(quantiles)
print(f"   人口密度分位数:")
for q, val in zip(quantiles, density_quantiles):
    print(f"     - {q*100}%分位数: {val:.2f} 人/km²")

# 检查异常值
high_density_threshold = 50000  # 5万人/km²作为高密度阈值
high_density_count = (pop_density > high_density_threshold).sum()
print(f"   高密度网格数 (> {high_density_threshold} 人/km²): {high_density_count}")
print()

# 7. 网格ID检查
print("7. 网格ID分布检查...")
# 检查grid_id_500m是否唯一
unique_grid_ids = df_500m['grid_id_500m'].nunique()
grid_id_count = len(df_500m)
print(f"   网格ID总数: {grid_id_count}")
print(f"   唯一网格ID数: {unique_grid_ids}")
print(f"   ID唯一性: {'良好' if unique_grid_ids == grid_id_count else '存在重复'}")
print()

# 8. 空间范围检查
print("8. 空间范围检查...")
print(f"   X坐标范围: {df_500m['minx'].min():.2f} 至 {df_500m['maxx'].max():.2f} 米")
print(f"   Y坐标范围: {df_500m['miny'].min():.2f} 至 {df_500m['maxy'].max():.2f} 米")
print(f"   空间覆盖: {df_500m['minx'].min():.0f}×{df_500m['miny'].min():.0f} 至 {df_500m['maxx'].max():.0f}×{df_500m['maxy'].max():.0f} 米")
print()

# 9. 生成样例数据展示
print("9. 样例数据展示...")
print("   前5个500米网格数据:")
print(df_500m.head()[['grid_id_500m', 'grid_id_1km', 'total_population', 'population_density']])
print()

# 10. 最终评估
print("10. 最终评估总结...")

# 评估标准：
# 1. 总人口一致性
# 2. 网格尺寸准确性
# 3. 人口密度分布合理性
# 4. 文件生成成功

# 计算评分
score = 0
max_score = 100

# 文件生成 (20分)
if file_exists and file_size > 1:
    score += 20
else:
    score += 10
    print("   警告: 文件生成可能存在问题")

# 总人口一致性 (30分)
if 'total_pop_1km' in locals():
    if diff_percent < 0.01:
        score += 30
    elif diff_percent < 0.1:
        score += 25
    elif diff_percent < 1:
        score += 20
    else:
        score += 10
        print("   警告: 人口数据差异较大")
else:
    score += 20  # 无法验证，给部分分数
    print("   提示: 无法验证人口数据一致性")

# 网格尺寸准确性 (25分)
if grid_widths.std() < 0.01 and grid_heights.std() < 0.01:
    score += 25
elif grid_widths.std() < 0.1 and grid_heights.std() < 0.1:
    score += 20
else:
    score += 15
    print("   警告: 网格尺寸一致性较差")

# 人口密度分布合理性 (25分)
high_density_ratio = high_density_count / grid_id_count
if high_density_ratio < 0.01 and pop_density.max() < 100000:
    score += 25
elif high_density_ratio < 0.05:
    score += 20
else:
    score += 15
    print(f"   警告: 高密度网格比例较高 ({high_density_ratio*100:.2f}%)")

print(f"\n=== 验证完成 ===")
print(f"总体评分: {score}/{max_score}")
print(f"评级: {'优秀' if score >= 90 else '良好' if score >= 80 else '合格' if score >= 70 else '需要改进'}")
print(f"\n结论: {'500米人口密度分布图效果良好，可以使用' if score >= 80 else '500米人口密度分布图需要进一步优化'}")
print(f"\n建议:")
if score < 80:
    print("1. 检查人口分配算法的合理性")
    print("2. 验证网格尺寸的精确性")
    print("3. 检查高密度区域的异常值")
else:
    print("1. 可以考虑调整颜色映射以更好地展示人口密度差异")
    print("2. 如需进一步提高精度，可以考虑使用实际的空间重叠计算")
print("3. 确保在论文中说明数据处理方法和精度限制")

print(f"\n验证完成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")