import pandas as pd
import numpy as np

# 定义文件路径
morning_file = 'd:/Desktop/项目论文/建模/早高峰_cleaned.csv'
evening_file = 'd:/Desktop/项目论文/建模/晚高峰_cleaned.csv'

print("开始验证数据标准化状态...\n")

# 加载数据
print(f"加载早高峰数据: {morning_file}")
morning_df = pd.read_csv(morning_file)
print(f"加载晚高峰数据: {evening_file}")
evening_df = pd.read_csv(evening_file)

print(f"\n早高峰数据形状: {morning_df.shape}")
print(f"晚高峰数据形状: {evening_df.shape}")

# 检查列名
print(f"\n数据列名: {list(morning_df.columns)}")

# 检查缺失值
print("\n=== 缺失值检查 ===")
print("早高峰数据缺失值:")
print(morning_df.isnull().sum())
print("\n晚高峰数据缺失值:")
print(evening_df.isnull().sum())

# 检查数据类型
print("\n=== 数据类型检查 ===")
print("早高峰数据类型:")
print(morning_df.dtypes)

# 检查标准化状态（排除grid_id）
feature_cols = [col for col in morning_df.columns if col != 'grid_id']

print("\n=== 标准化状态检查 ===")
print("早高峰数据统计信息:")
morning_stats = morning_df[feature_cols].describe()
print(morning_stats)

print("\n晚高峰数据统计信息:")
evening_stats = evening_df[feature_cols].describe()
print(evening_stats)

# 检查每个特征的标准化情况
print("\n=== 各特征标准化状态分析 ===")
print("早高峰数据:")
for col in feature_cols:
    mean_val = morning_df[col].mean()
    std_val = morning_df[col].std()
    min_val = morning_df[col].min()
    max_val = morning_df[col].max()
    # 标准化特征通常均值接近0，标准差接近1
    is_standardized = abs(mean_val) < 0.1 and 0.9 < std_val < 1.1
    print(f"{col}: 均值={mean_val:.4f}, 标准差={std_val:.4f}, 范围=[{min_val:.4f}, {max_val:.4f}], 标准化={is_standardized}")

print("\n晚高峰数据:")
for col in feature_cols:
    mean_val = evening_df[col].mean()
    std_val = evening_df[col].std()
    min_val = evening_df[col].min()
    max_val = evening_df[col].max()
    is_standardized = abs(mean_val) < 0.1 and 0.9 < std_val < 1.1
    print(f"{col}: 均值={mean_val:.4f}, 标准差={std_val:.4f}, 范围=[{min_val:.4f}, {max_val:.4f}], 标准化={is_standardized}")

# 检查特征间的相关性
print("\n=== 特征相关性检查（前5个特征）===")
morning_corr = morning_df[feature_cols[:5]].corr()
print("早高峰特征相关性（前5个）:")
print(morning_corr.round(4))

# 评估是否适合机器学习输入
print("\n=== 机器学习输入适合性评估 ===")
issues = []

# 检查缺失值
if morning_df.isnull().sum().sum() > 0:
    issues.append("早高峰数据存在缺失值")
if evening_df.isnull().sum().sum() > 0:
    issues.append("晚高峰数据存在缺失值")

# 检查标准化一致性
standardized_cols_morning = [col for col in feature_cols 
                           if abs(morning_df[col].mean()) < 0.1 and 0.9 < morning_df[col].std() < 1.1]
non_standardized_cols_morning = [col for col in feature_cols if col not in standardized_cols_morning]

standardized_cols_evening = [col for col in feature_cols 
                           if abs(evening_df[col].mean()) < 0.1 and 0.9 < evening_df[col].std() < 1.1]
non_standardized_cols_evening = [col for col in feature_cols if col not in standardized_cols_evening]

if non_standardized_cols_morning:
    issues.append(f"早高峰数据中以下特征未标准化: {non_standardized_cols_morning}")
if non_standardized_cols_evening:
    issues.append(f"晚高峰数据中以下特征未标准化: {non_standardized_cols_evening}")

# 检查数据范围合理性
for col in feature_cols:
    if morning_df[col].max() > 10 or morning_df[col].min() < -10:
        issues.append(f"早高峰数据中{col}的范围异常大，可能需要额外处理")
    if evening_df[col].max() > 10 or evening_df[col].min() < -10:
        issues.append(f"晚高峰数据中{col}的范围异常大，可能需要额外处理")

# 输出评估结果
print("\n评估结果:")
if issues:
    print("发现以下需要注意的问题:")
    for issue in issues:
        print(f"- {issue}")
    print("\n建议在使用数据前解决上述问题。")
else:
    print("数据质量良好，所有特征已标准化，适合作为机器学习模型输入。")
    print(f"早高峰数据标准化特征数: {len(standardized_cols_morning)}/{len(feature_cols)}")
    print(f"晚高峰数据标准化特征数: {len(standardized_cols_evening)}/{len(feature_cols)}")

print("\n验证完成！")
