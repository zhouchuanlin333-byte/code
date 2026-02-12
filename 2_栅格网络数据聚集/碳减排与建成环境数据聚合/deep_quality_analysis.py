import pandas as pd
import numpy as np

print("="*60)
print("深入数据质量分析")
print("="*60)

# 读取数据
df_morning = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
df_evening = pd.read_csv('d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv')

# 1. 缺失值详细分析
print("\n" + "="*60)
print("1. 缺失值详细分析")
print("="*60)

# 找出所有含有缺失值的行
morning_missing_rows = df_morning[df_morning.isnull().any(axis=1)]
evening_missing_rows = df_evening[df_evening.isnull().any(axis=1)]

print(f"早高峰数据中缺失值行数: {len(morning_missing_rows)}")
print(f"晚高峰数据中缺失值行数: {len(evening_missing_rows)}")

# 具体哪些字段缺失
print("\n早高峰缺失值字段详情:")
for col in df_morning.columns:
    missing_count = df_morning[col].isnull().sum()
    if missing_count > 0:
        print(f"  {col}: {missing_count} 个缺失值")
        # 显示前5个缺失值的grid_id
        missing_grid_ids = df_morning[df_morning[col].isnull()]['grid_id'].head(5).tolist()
        print(f"    前5个缺失值的网格ID: {missing_grid_ids}")

print("\n晚高峰缺失值字段详情:")
for col in df_evening.columns:
    missing_count = df_evening[col].isnull().sum()
    if missing_count > 0:
        print(f"  {col}: {missing_count} 个缺失值")
        # 显示前5个缺失值的grid_id
        missing_grid_ids = df_evening[df_evening[col].isnull()]['grid_id'].head(5).tolist()
        print(f"    前5个缺失值的网格ID: {missing_grid_ids}")

# 2. 异常值详细分析
print("\n" + "="*60)
print("2. 异常值详细分析 (使用IQR方法)")
print("="*60)

# 选择需要分析的数值字段
numeric_cols = ['碳排放_carbon_emission_kg (kgCO2/KM/d)', '人口密度 (千人/km²)', 
               '道路密度 (KM/KM²)', '到市中心距离 (km)', '到最近公交距离 (km)']

for col in numeric_cols:
    print(f"\n{col}:")
    
    # 早高峰异常值
    Q1_morning = df_morning[col].quantile(0.25)
    Q3_morning = df_morning[col].quantile(0.75)
    IQR_morning = Q3_morning - Q1_morning
    lower_bound_morning = Q1_morning - 1.5 * IQR_morning
    upper_bound_morning = Q3_morning + 1.5 * IQR_morning
    
    outliers_morning = df_morning[(df_morning[col] < lower_bound_morning) | (df_morning[col] > upper_bound_morning)]
    
    print(f"  早高峰:")
    print(f"    正常值范围: [{lower_bound_morning:.4f}, {upper_bound_morning:.4f}]")
    print(f"    异常值数量: {len(outliers_morning)}")
    print(f"    异常值比例: {len(outliers_morning)/len(df_morning)*100:.2f}%")
    if len(outliers_morning) > 0:
        print(f"    最小异常值: {outliers_morning[col].min():.4f}")
        print(f"    最大异常值: {outliers_morning[col].max():.4f}")
    
    # 晚高峰异常值
    Q1_evening = df_evening[col].quantile(0.25)
    Q3_evening = df_evening[col].quantile(0.75)
    IQR_evening = Q3_evening - Q1_evening
    lower_bound_evening = Q1_evening - 1.5 * IQR_evening
    upper_bound_evening = Q3_evening + 1.5 * IQR_evening
    
    outliers_evening = df_evening[(df_evening[col] < lower_bound_evening) | (df_evening[col] > upper_bound_evening)]
    
    print(f"  晚高峰:")
    print(f"    正常值范围: [{lower_bound_evening:.4f}, {upper_bound_evening:.4f}]")
    print(f"    异常值数量: {len(outliers_evening)}")
    print(f"    异常值比例: {len(outliers_evening)/len(df_evening)*100:.2f}%")
    if len(outliers_evening) > 0:
        print(f"    最小异常值: {outliers_evening[col].min():.4f}")
        print(f"    最大异常值: {outliers_evening[col].max():.4f}")

# 3. 零值分析
print("\n" + "="*60)
print("3. 零值分析")
print("="*60)

print("早高峰零值统计:")
for col in numeric_cols:
    zero_count = (df_morning[col] == 0).sum()
    if zero_count > 0:
        print(f"  {col}: {zero_count} 个零值 ({zero_count/len(df_morning)*100:.2f}%)")

print("\n晚高峰零值统计:")
for col in numeric_cols:
    zero_count = (df_evening[col] == 0).sum()
    if zero_count > 0:
        print(f"  {col}: {zero_count} 个零值 ({zero_count/len(df_evening)*100:.2f}%)")

# 4. 数据分布偏态性分析
print("\n" + "="*60)
print("4. 数据分布偏态性分析")
print("="*60)

print("早高峰数据偏态性:")
for col in numeric_cols:
    skewness = df_morning[col].skew()
    print(f"  {col}: 偏度 = {skewness:.4f}")
    if abs(skewness) > 2:
        print(f"    ⚠️  高度偏态分布")
    elif abs(skewness) > 1:
        print(f"    ⚠️  中度偏态分布")
    elif abs(skewness) > 0.5:
        print(f"    ⚠️  轻度偏态分布")
    else:
        print(f"    ✓ 近似正态分布")

# 5. 数据一致性检查
print("\n" + "="*60)
print("5. 数据一致性检查")
print("="*60)

# 检查两个时间段的网格ID是否一致
grid_id_consistent = set(df_morning['grid_id']) == set(df_evening['grid_id'])
print(f"早高峰和晚高峰网格ID一致性: {'✓ 一致' if grid_id_consistent else '✗ 不一致'}")

# 检查两个时间段的特征字段是否一致
cols_consistent = list(df_morning.columns) == list(df_evening.columns)
print(f"早高峰和晚高峰字段一致性: {'✓ 一致' if cols_consistent else '✗ 不一致'}")

# 6. 数据清洗建议总结
print("\n" + "="*60)
print("6. 数据清洗建议总结")
print("="*60)

print("需要处理的问题:")
print("1. 缺失值处理:")
print("   - 对道路密度字段的缺失值，建议使用KNN或基于地理位置的插值方法")
print("   - 检查缺失值是否集中在特定区域")

print("\n2. 异常值处理:")
print("   - 碳排放在早高峰和晚高峰都有较多异常值，建议使用分位数截断或 Winsorization 方法")
print("   - 人口密度存在异常值，可能需要结合实际情况判断是否为有效数据")
print("   - 到最近公交距离的异常值可能表示公交覆盖较少的区域，需谨慎处理")

print("\n3. 字段标准化:")
print("   - 去除字段名中的单位信息，简化字段名")
print("   - 对偏态分布的数据考虑进行对数转换或标准化处理")

print("\n4. 数据转换建议:")
print("   - 对计数类数据(POI数量)考虑使用归一化或标准化")
print("   - 距离类特征可能需要进行标准化以平衡特征权重")
print("   - 对于机器学习模型，建议对所有数值特征进行标准化处理")

print("\n" + "="*60)
print("深入质量分析完成！")
print("="*60)
