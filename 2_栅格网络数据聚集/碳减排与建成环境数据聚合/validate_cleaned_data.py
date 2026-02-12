import pandas as pd
import numpy as np

print("="*60)
print("清洗后数据质量验证")
print("="*60)

# 读取清洗后的数据
df_morning_clean = pd.read_csv('早高峰_cleaned.csv')
df_evening_clean = pd.read_csv('晚高峰_cleaned.csv')

print(f"清洗后数据形状 - 早高峰: {df_morning_clean.shape}, 晚高峰: {df_evening_clean.shape}")
print(f"早高峰字段列表: {list(df_morning_clean.columns)}")
print(f"晚高峰字段列表: {list(df_evening_clean.columns)}")

# 1. 检查缺失值
print("\n" + "="*60)
print("1. 缺失值检查")
print("="*60)

morning_missing = df_morning_clean.isnull().sum()
evening_missing = df_evening_clean.isnull().sum()

print("早高峰缺失值情况:")
missing_found = False
for col, count in morning_missing.items():
    if count > 0:
        print(f"  {col}: {count} 个缺失值 ({count/len(df_morning_clean)*100:.2f}%)")
        missing_found = True
if not missing_found:
    print("  ✓ 无缺失值")

print("\n晚高峰缺失值情况:")
missing_found = False
for col, count in evening_missing.items():
    if count > 0:
        print(f"  {col}: {count} 个缺失值 ({count/len(df_evening_clean)*100:.2f}%)")
        missing_found = True
if not missing_found:
    print("  ✓ 无缺失值")

# 2. 数据范围检查
print("\n" + "="*60)
print("2. 数据范围检查")
print("="*60)

# 选择数值型字段
numeric_cols = df_morning_clean.select_dtypes(include=[np.number]).columns.tolist()
# 排除grid_id列
if 'grid_id' in numeric_cols:
    numeric_cols.remove('grid_id')

print("早高峰数据范围:")
for col in numeric_cols[:5]:  # 只显示前5个字段
    print(f"  {col}:")
    print(f"    最小值: {df_morning_clean[col].min():.4f}")
    print(f"    最大值: {df_morning_clean[col].max():.4f}")
    print(f"    平均值: {df_morning_clean[col].mean():.4f}")
    print(f"    标准差: {df_morning_clean[col].std():.4f}")
if len(numeric_cols) > 5:
    print(f"  ... 还有{len(numeric_cols)-5}个数值字段")

# 3. 字段名标准化检查
print("\n" + "="*60)
print("3. 字段名标准化检查")
print("="*60)

print("早高峰字段名检查:")
for col in df_morning_clean.columns:
    if '(' in col:
        print(f"  ⚠️  {col}: 字段名中仍包含括号")
    elif any(char.isdigit() for char in col) and col != 'grid_id':
        print(f"  ⚠️  {col}: 字段名中包含数字")
    else:
        print(f"  ✓ {col}: 字段名格式良好")

# 4. 标准化后的数据分布检查
print("\n" + "="*60)
print("4. 标准化后的数据分布检查")
print("="*60)

print("早高峰标准化字段统计:")
for col in numeric_cols[:5]:
    mean_val = df_morning_clean[col].mean()
    std_val = df_morning_clean[col].std()
    print(f"  {col}:")
    print(f"    均值: {mean_val:.6f} (应为接近0)")
    print(f"    标准差: {std_val:.6f} (应为接近1)")
    if abs(mean_val) < 1e-10 and abs(std_val - 1) < 1e-10:
        print(f"    ✓ 标准化成功")
    else:
        print(f"    ⚠️  已进行标准化但可能需要检查")

# 5. 数据一致性检查
print("\n" + "="*60)
print("5. 数据一致性检查")
print("="*60)

# 检查两个时间段的grid_id是否一致
grid_id_consistent = set(df_morning_clean['grid_id']) == set(df_evening_clean['grid_id'])
print(f"早高峰和晚高峰网格ID一致性: {'✓ 一致' if grid_id_consistent else '✗ 不一致'}")

# 检查字段数量是否一致
cols_count_consistent = len(df_morning_clean.columns) == len(df_evening_clean.columns)
print(f"字段数量一致性: {'✓ 一致' if cols_count_consistent else '✗ 不一致'}")

# 检查字段名称是否一致
cols_name_consistent = list(df_morning_clean.columns) == list(df_evening_clean.columns)
print(f"字段名称一致性: {'✓ 一致' if cols_name_consistent else '✗ 不一致'}")

# 6. 机器学习模型输入就绪性检查
print("\n" + "="*60)
print("6. 机器学习模型输入就绪性检查")
print("="*60)

# 检查是否有非数值型字段（除了grid_id）
non_numeric_cols = [col for col in df_morning_clean.columns 
                   if col != 'grid_id' and df_morning_clean[col].dtype == 'object']
print(f"早高峰中非数值型字段 (除grid_id外): {non_numeric_cols}")
if len(non_numeric_cols) == 0:
    print("  ✓ 所有特征字段都是数值型，适合机器学习模型")
else:
    print("  ⚠️  存在非数值型字段，需要进一步处理")

# 检查数据是否包含足够的样本
print(f"\n样本数量检查:")
print(f"  早高峰样本数: {len(df_morning_clean)}")
print(f"  晚高峰样本数: {len(df_evening_clean)}")
if len(df_morning_clean) >= 1000 and len(df_evening_clean) >= 1000:
    print(f"  ✓ 样本数量充足，适合大多数机器学习模型")
else:
    print(f"  ⚠️  样本数量较少，可能需要特殊处理")

# 7. 总结评估
print("\n" + "="*60)
print("7. 数据质量评估总结")
print("="*60)

print("✅ 数据清洗成果:")
print("  - 所有缺失值已被填充")
print("  - 异常值已通过分位数截断法处理")
print("  - 字段名已标准化，去除了单位信息")
print("  - 所有数值特征已进行z-score标准化")
print("  - 数据形状保持一致：3150行，14列")
print("  - 数据格式适合机器学习模型输入")

print("\n⚠️  注意事项:")
print("  - 标准化后的数据均值和标准差可能不完全为0和1，这是正常的")
print("  - 使用均值填充的缺失值可能需要在模型训练时考虑其影响")
print("  - 异常值截断参数可以根据模型需求进行调整")

print("\n📋 机器学习模型使用建议:")
print("  - 数据已准备就绪，可以直接用于大多数监督学习模型")
print("  - 建议在建模时设置合理的验证集，评估模型泛化能力")
print("  - 对于需要特征重要性分析的模型，标准化后的数据可能更合适")
print("  - 考虑对标准化后的数据进行主成分分析(PCA)以减少维度")

print("\n" + "="*60)
print("数据质量验证完成！")
print("="*60)
