import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# 设置文件路径
input_file = 'D:/Desktop/项目论文/全天时段订单趋势分析/全天时段轨迹数据/西安市主城区共享单车轨迹数据（部分截取）.csv'
output_dir = 'D:/Desktop/项目论文/全天时段订单趋势分析/全天时段轨迹数据'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("="*60)
print("开始清洗共享单车轨迹数据")
print("="*60)

# 1. 加载数据
print("\n[1/5] 加载原始数据...")
df = pd.read_csv(input_file)
print(f"原始数据行数: {len(df)}")
print(f"原始数据列名: {list(df.columns)}")

# 2. 修正列名错别字（维度 -> 纬度）
df = df.rename(columns={'维度': '纬度'})
print(f"\n修正后列名: {list(df.columns)}")

# 3. 剔除缺失坐标的记录
print("\n[2/5] 剔除缺失坐标的记录...")
original_count = len(df)
df = df.dropna(subset=['经度', '纬度'])
missing_coords_removed = original_count - len(df)
print(f"剔除缺失坐标记录数: {missing_coords_removed}")
print(f"剩余数据行数: {len(df)}")

# 4. 转换时间列格式
print("\n[3/5] 转换时间格式...")
df['获取时间'] = pd.to_datetime(df['获取时间'])
print("时间格式转换完成")

# 5. 按共享单车分组并检查轨迹中断
print("\n[4/5] 检查并剔除轨迹中断超过10分钟的记录...")
bike_groups = df.groupby('共享单车编号')

valid_records = []
total_interrupted_removed = 0

for bike_id, group in bike_groups:
    # 按时间排序
    group_sorted = group.sort_values('获取时间')
    
    # 计算相邻记录的时间差
    group_sorted['时间差'] = group_sorted['获取时间'].diff()
    
    # 标记需要保留的记录
    # 第一条记录总是保留
    group_sorted['保留'] = True
    
    # 检查后续记录，如果与前一条记录的时间差超过10分钟，则不保留
    for i in range(1, len(group_sorted)):
        time_diff = group_sorted.iloc[i]['时间差']
        if pd.notna(time_diff) and time_diff > timedelta(minutes=10):
            group_sorted.iloc[i, group_sorted.columns.get_loc('保留')] = False
            total_interrupted_removed += 1
    
    # 只保留标记为True的记录
    valid_group = group_sorted[group_sorted['保留']].copy()
    valid_records.append(valid_group)

# 合并所有有效记录
df_cleaned = pd.concat(valid_records, ignore_index=True)

# 删除辅助列
df_cleaned = df_cleaned.drop(['时间差', '保留'], axis=1)

print(f"剔除轨迹中断记录数: {total_interrupted_removed}")
print(f"清洗后数据行数: {len(df_cleaned)}")

# 6. 保存清洗后的数据
print("\n[5/5] 保存清洗后的数据...")
output_file = os.path.join(output_dir, '西安市主城区共享单车轨迹数据_清洗后.csv')
df_cleaned.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"清洗后的数据已保存到: {output_file}")

# 7. 生成清洗报告
print("\n" + "="*60)
print("数据清洗完成报告")
print("="*60)
print(f"原始数据行数: {original_count}")
print(f"剔除缺失坐标记录: {missing_coords_removed}")
print(f"剔除轨迹中断记录: {total_interrupted_removed}")
print(f"最终保留记录: {len(df_cleaned)}")
print(f"数据保留率: {(len(df_cleaned)/original_count*100):.2f}%")
print("="*60)

# 保存清洗报告
report_file = os.path.join(output_dir, '数据清洗报告.txt')
with open(report_file, 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("数据清洗完成报告\n")
    f.write("="*60 + "\n\n")
    f.write(f"原始数据行数: {original_count}\n")
    f.write(f"剔除缺失坐标记录: {missing_coords_removed}\n")
    f.write(f"剔除轨迹中断记录: {total_interrupted_removed}\n")
    f.write(f"最终保留记录: {len(df_cleaned)}\n")
    f.write(f"数据保留率: {(len(df_cleaned)/original_count*100):.2f}%\n")
    f.write("="*60 + "\n")

print(f"\n清洗报告已保存到: {report_file}")
