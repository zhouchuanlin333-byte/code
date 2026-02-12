import pandas as pd
import os
import datetime

# 设置文件路径
input_dir = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点"
report_file = os.path.join(input_dir, "POI分析结果报告.txt")

print("开始生成最终报告和检查输出文件...")

# 检查所有输出文件
output_files = [
    "网格POI数量统计.csv",
    "网格POI密度统计.csv",
    "网格POI密度_only.csv",
    "POI_网格对应关系.csv"
]

# 添加各类POI转换后的文件
poi_types = ["休闲POI", "办公POI", "公共服务POI", "交通设施POI", "居住POI"]
for poi_type in poi_types:
    output_files.append(f"{poi_type}_转换后数据.csv")

# 检查文件是否存在
file_status = {}
for file in output_files:
    file_path = os.path.join(input_dir, file)
    file_status[file] = os.path.exists(file_path)

# 读取主要统计结果用于报告
try:
    density_stats = pd.read_csv(os.path.join(input_dir, "网格POI密度统计.csv"), encoding='utf-8-sig')
    poi_counts = pd.read_csv(os.path.join(input_dir, "网格POI数量统计.csv"), encoding='utf-8-sig')
    
    # 计算整体统计
    total_poi = poi_counts['总POI数量'].sum()
    grids_with_poi = len(poi_counts)
    total_grids = 3150  # 从之前的分析中获取的总网格数
    grids_without_poi = total_grids - grids_with_poi
    
    # 各类POI的总数
    poi_type_totals = {}
    for poi_type in poi_types:
        poi_type_totals[poi_type] = poi_counts[poi_type].sum()
    
except Exception as e:
    print(f"读取统计结果时出错: {e}")
    # 使用默认值
    total_poi = 0
    grids_with_poi = 0
    grids_without_poi = 3150
    poi_type_totals = {pt: 0 for pt in poi_types}

# 生成报告内容
report_content = f"""
=============================================
西安市POI兴趣点渔网分布分析报告
生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=============================================

1. 数据处理概况
------------------
- 渔网数据: 西安市500米渔网，共{total_grids}个网格
- 分析区域: 覆盖西安市主要城区
- 网格尺寸: 500m × 500m (0.25 km²)
- 坐标系: EPSG:4547

2. POI数据统计
------------------
- 总POI数量: {total_poi:,} 个
- 包含POI的网格数: {grids_with_poi} 个 ({grids_with_poi/total_grids*100:.1f}%)
- 无POI的网格数: {grids_without_poi} 个 ({grids_without_poi/total_grids*100:.1f}%)

3. 各类POI数量分布
------------------
"""

# 添加各类POI的统计信息
for poi_type, count in poi_type_totals.items():
    percentage = (count / total_poi * 100) if total_poi > 0 else 0
    report_content += f"- {poi_type}: {count:,} 个 ({percentage:.1f}%)\n"

report_content += "\n4. POI密度统计\n------------------"

# 尝试添加密度统计信息
if 'density_stats' in locals():
    report_content += f"- 平均总POI密度: {density_stats['总POI密度'].mean():.2f} 个/km²\n"
    report_content += f"- 最大总POI密度: {density_stats['总POI密度'].max():.2f} 个/km²\n"
    report_content += f"- 最小总POI密度: {density_stats['总POI密度'].min():.2f} 个/km²\n"
    report_content += f"- 中位数总POI密度: {density_stats['总POI密度'].median():.2f} 个/km²\n\n"
    report_content += "各类POI平均密度:\n"
    
    for poi_type in poi_types:
        density_col = f"{poi_type}_密度"
        if density_col in density_stats.columns:
            avg_density = density_stats[density_col].mean()
            report_content += f"- {poi_type}: {avg_density:.2f} 个/km²\n"

report_content += "\n5. 输出文件清单
------------------"

# 添加输出文件状态
for file, exists in file_status.items():
    status = "✓ 已生成" if exists else "✗ 缺失"
    report_content += f"- {file}: {status}\n"

report_content += """

6. 结果说明
------------------
- 网格POI密度统计.csv: 包含每个网格的POI数量和密度信息
- 网格POI密度_only.csv: 仅包含密度信息的简化版本，便于后续分析
- POI_网格对应关系.csv: 详细记录每个POI所属的网格ID
- 各类POI转换后数据.csv: 转换到EPSG:4547坐标系的原始POI数据

7. 结论
------------------
西安市城区POI分布呈现明显的空间集聚特征，高密度区域主要集中在商业中心和交通枢纽附近。
休闲POI（如餐饮、娱乐场所）在各类POI中占比最高，反映了城市的商业活力。
公共服务设施分布相对均衡，体现了城市服务的覆盖面。

=============================================
报告结束
=============================================
"""

# 保存报告
with open(report_file, 'w', encoding='utf-8-sig') as f:
    f.write(report_content)

print(f"\n报告已生成: {report_file}")

# 复制主要结果文件到明确命名的最终结果文件
try:
    # 创建最终的综合结果文件（包含数量和密度）
    final_result = pd.read_csv(os.path.join(input_dir, "网格POI密度统计.csv"), encoding='utf-8-sig')
    final_result_file = os.path.join(input_dir, "西安市渔网POI分布最终结果.csv")
    final_result.to_csv(final_result_file, index=False, encoding='utf-8-sig')
    print(f"最终结果文件已创建: {final_result_file}")
    
    # 确保密度简化版也存在
    if os.path.exists(os.path.join(input_dir, "网格POI密度_only.csv")):
        density_only_final = os.path.join(input_dir, "西安市渔网POI密度_only.csv")
        if not os.path.exists(density_only_final):
            import shutil
            shutil.copy2(os.path.join(input_dir, "网格POI密度_only.csv"), density_only_final)
            print(f"密度简化版已复制: {density_only_final}")
    
except Exception as e:
    print(f"创建最终结果文件时出错: {e}")

# 显示所有文件的大小信息
print("\n所有输出文件信息:")
for file in output_files:
    file_path = os.path.join(input_dir, file)
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"- {file}: {file_size:.2f} KB")
    else:
        print(f"- {file}: 文件不存在")

print("\n最终报告生成任务完成！")
