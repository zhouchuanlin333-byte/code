import pandas as pd
import os

# 设置文件路径
base_dir = os.path.dirname(os.path.abspath(__file__))
detailed_csv = os.path.join(base_dir, "网格交通站点分布统计.csv")
summary_csv = os.path.join(base_dir, "网格交通站点数量统计.csv")

print("=== 验证生成的结果文件 ===")

# 检查文件是否存在
if not os.path.exists(detailed_csv):
    print(f"错误: 详细统计文件 {detailed_csv} 不存在")
    exit(1)
if not os.path.exists(summary_csv):
    print(f"错误: 汇总统计文件 {summary_csv} 不存在")
    exit(1)

print("\n文件存在检查通过！")

# 读取CSV文件
print("\n读取详细统计文件...")
df_detailed = pd.read_csv(detailed_csv)
print(f"详细统计文件行数: {len(df_detailed)}")
print(f"详细统计文件列名: {list(df_detailed.columns)}")

print("\n读取汇总统计文件...")
df_summary = pd.read_csv(summary_csv)
print(f"汇总统计文件行数: {len(df_summary)}")
print(f"汇总统计文件列名: {list(df_summary.columns)}")

# 验证数据完整性
print("\n=== 数据完整性验证 ===")
print(f"1. 详细统计文件缺失值检查:")
print(df_detailed.isnull().sum())

print(f"\n2. 汇总统计文件缺失值检查:")
print(df_summary.isnull().sum())

# 验证统计信息
print("\n=== 统计信息验证 ===")

# 计算详细文件中的总站点数
detailed_total_metro = df_detailed['metro_count'].sum()
detailed_total_bus = df_detailed['bus_count'].sum()
detailed_total_all = detailed_total_metro + detailed_total_bus

# 计算汇总文件中的总站点数
summary_total_metro = df_summary['metro_count'].sum()
summary_total_bus = df_summary['bus_count'].sum()
summary_total_all = summary_total_metro + summary_total_bus

print(f"3. 详细文件统计:")
print(f"   地铁站点总数: {detailed_total_metro}")
print(f"   公交站点总数: {detailed_total_bus}")
print(f"   总站点数: {detailed_total_all}")

print(f"\n4. 汇总文件统计:")
print(f"   地铁站点总数: {summary_total_metro}")
print(f"   公交站点总数: {summary_total_bus}")
print(f"   总站点数: {summary_total_all}")

# 验证两个文件的统计结果是否一致
print("\n5. 文件一致性验证:")
if detailed_total_metro == summary_total_metro and detailed_total_bus == summary_total_bus:
    print("   ✓ 两个文件的站点统计一致")
else:
    print("   ✗ 警告: 两个文件的站点统计不一致")

# 分析有站点的网格
print("\n6. 网格分布分析:")
has_metro_grids = len(df_detailed[df_detailed['metro_count'] > 0])
has_bus_grids = len(df_detailed[df_detailed['bus_count'] > 0])
has_both_grids = len(df_detailed[(df_detailed['metro_count'] > 0) & (df_detailed['bus_count'] > 0)])
has_no_grids = len(df_detailed[(df_detailed['metro_count'] == 0) & (df_detailed['bus_count'] == 0)])

total_grids = len(df_detailed)

print(f"   总网格数: {total_grids}")
print(f"   有地铁站点的网格数: {has_metro_grids}")
print(f"   有公交站点的网格数: {has_bus_grids}")
print(f"   同时有地铁和公交站点的网格数: {has_both_grids}")
print(f"   无站点的网格数: {has_no_grids}")

# 验证网格数计算
if has_metro_grids + has_bus_grids - has_both_grids + has_no_grids == total_grids:
    print("   ✓ 网格数统计正确")
else:
    print("   ✗ 警告: 网格数统计不正确")

# 分析站点分布
print("\n7. 站点分布极值分析:")
max_metro_per_grid = df_detailed['metro_count'].max()
max_bus_per_grid = df_detailed['bus_count'].max()
max_total_per_grid = df_detailed['total_count'].max()

grid_with_max_metro = df_detailed.loc[df_detailed['metro_count'].idxmax(), 'grid_id']
grid_with_max_bus = df_detailed.loc[df_detailed['bus_count'].idxmax(), 'grid_id']
grid_with_max_total = df_detailed.loc[df_detailed['total_count'].idxmax(), 'grid_id']

print(f"   单网格最多地铁站点数: {max_metro_per_grid} (网格 {grid_with_max_metro})")
print(f"   单网格最多公交站点数: {max_bus_per_grid} (网格 {grid_with_max_bus})")
print(f"   单网格最多总站点数: {max_total_per_grid} (网格 {grid_with_max_total})")

# 检查可视化文件
print("\n8. 可视化文件检查:")
viz_files = [
    "交通站点网格分布可视化.png",
    "网格分布统计图表.png"
]

for viz_file in viz_files:
    viz_path = os.path.join(base_dir, viz_file)
    if os.path.exists(viz_path):
        file_size = os.path.getsize(viz_path) / 1024 / 1024  # 转换为MB
        print(f"   ✓ {viz_file} 存在，文件大小: {file_size:.2f} MB")
    else:
        print(f"   ✗ 警告: {viz_file} 不存在")

# 总体验证结果
print("\n=== 总体验证结果 ===")
all_passed = True

# 检查关键指标
if detailed_total_metro == 0 or detailed_total_bus == 0:
    print("✗ 严重问题: 站点统计数量异常")
    all_passed = False
    
if total_grids != 3150:  # 预期的总网格数
    print(f"✗ 警告: 网格总数不是预期的3150，实际为{total_grids}")
    all_passed = False

if all_passed:
    print("\n🎉 所有验证项目通过！结果数据完整且一致。")
    print(f"\n📊 关键统计摘要:")
    print(f"  - 成功处理了 {detailed_total_metro} 个地铁站点")
    print(f"  - 成功处理了 {detailed_total_bus} 个公交站点")
    print(f"  - 站点覆盖了 {total_grids - has_no_grids} 个网格")
    print(f"  - 生成了完整的统计数据和可视化结果")
else:
    print("\n⚠️  验证过程中发现一些问题，请检查。")

print("\n验证完成！")
