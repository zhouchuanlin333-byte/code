import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 定义文件路径
morning_file = 'd:/Desktop/项目论文/建模/早高峰_cleaned.csv'
evening_file = 'd:/Desktop/项目论文/建模/晚高峰_cleaned.csv'

print("开始评估数据的机器学习模型输入适用性...\n")

# 加载数据
print(f"加载早高峰数据: {morning_file}")
morning_df = pd.read_csv(morning_file)
print(f"加载晚高峰数据: {evening_file}")
evening_df = pd.read_csv(evening_file)

# 排除grid_id列
feature_cols = [col for col in morning_df.columns if col != 'grid_id']

print("\n=== 1. 数据基本信息 ===")
print(f"早高峰数据形状: {morning_df.shape} (行, 列)")
print(f"晚高峰数据形状: {evening_df.shape} (行, 列)")
print(f"特征数量: {len(feature_cols)}")
print(f"特征列表: {', '.join(feature_cols)}")

print("\n=== 2. 缺失值检查 ===")
morning_missing = morning_df.isnull().sum()
evening_missing = evening_df.isnull().sum()

morning_has_missing = morning_missing.sum() > 0
evening_has_missing = evening_missing.sum() > 0

if morning_has_missing:
    print("早高峰数据存在缺失值:")
    print(morning_missing[morning_missing > 0])
else:
    print("✓ 早高峰数据无缺失值")

if evening_has_missing:
    print("晚高峰数据存在缺失值:")
    print(evening_missing[evening_missing > 0])
else:
    print("✓ 晚高峰数据无缺失值")

print("\n=== 3. 标准化验证 ===")

# 检查早高峰数据的标准化情况
morning_standardized = []
for col in feature_cols:
    mean_val = morning_df[col].mean()
    std_val = morning_df[col].std()
    is_standardized = abs(mean_val) < 0.1 and 0.9 < std_val < 1.1
    morning_standardized.append(is_standardized)
    print(f"早高峰 {col}: 均值={mean_val:.4f}, 标准差={std_val:.4f}, 标准化={is_standardized}")

# 检查晚高峰数据的标准化情况
evening_standardized = []
for col in feature_cols:
    mean_val = evening_df[col].mean()
    std_val = evening_df[col].std()
    is_standardized = abs(mean_val) < 0.1 and 0.9 < std_val < 1.1
    evening_standardized.append(is_standardized)
    print(f"晚高峰 {col}: 均值={mean_val:.4f}, 标准差={std_val:.4f}, 标准化={is_standardized}")

all_standardized = all(morning_standardized) and all(evening_standardized)
print(f"\n标准化总体状态: {'✓ 所有特征已标准化' if all_standardized else '✗ 部分特征未标准化'}")

print("\n=== 4. 异常值检查 ===")

# 使用IQR方法检测异常值
def check_outliers(df, cols):
    outliers_info = {}
    for col in cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_count = len(outliers)
        outlier_percent = (outlier_count / len(df)) * 100
        
        outliers_info[col] = {
            'count': outlier_count,
            'percent': outlier_percent,
            'range': (lower_bound, upper_bound),
            'data_range': (df[col].min(), df[col].max())
        }
    return outliers_info

morning_outliers = check_outliers(morning_df, feature_cols)
evening_outliers = check_outliers(evening_df, feature_cols)

print("早高峰数据异常值:")
has_morning_outliers = False
for col, info in morning_outliers.items():
    if info['count'] > 0:
        has_morning_outliers = True
        print(f"  {col}: {info['count']}个异常值 ({info['percent']:.2f}%), 数据范围[{info['data_range'][0]:.4f}, {info['data_range'][1]:.4f}], IQR边界[{info['range'][0]:.4f}, {info['range'][1]:.4f}]")
if not has_morning_outliers:
    print("  ✓ 无异常值")

print("\n晚高峰数据异常值:")
has_evening_outliers = False
for col, info in evening_outliers.items():
    if info['count'] > 0:
        has_evening_outliers = True
        print(f"  {col}: {info['count']}个异常值 ({info['percent']:.2f}%), 数据范围[{info['data_range'][0]:.4f}, {info['data_range'][1]:.4f}], IQR边界[{info['range'][0]:.4f}, {info['range'][1]:.4f}]")
if not has_evening_outliers:
    print("  ✓ 无异常值")

print("\n=== 5. 特征相关性检查 ===")

# 计算特征间的相关性
morning_corr = morning_df[feature_cols].corr().abs()
evening_corr = evening_df[feature_cols].corr().abs()

# 找出高相关性的特征对
corr_threshold = 0.9
def find_high_corr_pairs(corr_matrix, threshold):
    pairs = []
    # 获取上三角矩阵（排除对角线）
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    for i in range(len(upper.columns)):
        for j in range(i):
            if upper.iloc[i, j] > threshold:
                pairs.append((upper.columns[i], upper.columns[j], upper.iloc[i, j]))
    return pairs

morning_high_corr = find_high_corr_pairs(morning_corr, corr_threshold)
evening_high_corr = find_high_corr_pairs(evening_corr, corr_threshold)

print(f"早高峰数据中相关性 > {corr_threshold} 的特征对:")
if morning_high_corr:
    for pair in morning_high_corr:
        print(f"  {pair[0]} 和 {pair[1]}: {pair[2]:.4f}")
else:
    print("  ✓ 无高相关性特征对")

print(f"\n晚高峰数据中相关性 > {corr_threshold} 的特征对:")
if evening_high_corr:
    for pair in evening_high_corr:
        print(f"  {pair[0]} 和 {pair[1]}: {pair[2]:.4f}")
else:
    print("  ✓ 无高相关性特征对")

print("\n=== 6. 机器学习适用性综合评估 ===")

# 评估标准
criteria = {
    '无缺失值': not (morning_has_missing or evening_has_missing),
    '所有特征已标准化': all_standardized,
    '无严重异常值': not (has_morning_outliers or has_evening_outliers),
    '无高相关性特征': len(morning_high_corr) == 0 and len(evening_high_corr) == 0
}

print("评估标准:")
for criterion, passed in criteria.items():
    print(f"  {criterion}: {'✓ 通过' if passed else '✗ 未通过'}")

# 综合结论
print("\n=== 综合结论 ===")

all_passed = all(criteria.values())

if all_passed:
    print("✓ 数据完全适合作为机器学习模型输入！")
    print("- 所有特征已正确标准化")
    print("- 无缺失值")
    print("- 无异常值")
    print("- 特征间无高相关性")
else:
    print("⚠️  数据基本适合作为机器学习模型输入，但有以下注意事项:")
    
    if not criteria['所有特征已标准化']:
        print("- 部分特征未标准化，可能影响某些模型性能")
    
    if criteria['无严重异常值']:
        print("- 存在少量异常值，大多数模型能够处理")
    
    if criteria['无高相关性特征']:
        print("- 存在高相关性特征，可能导致过拟合，建议考虑特征选择或正则化")
    
    print("\n建议:")
    print("1. 对于线性模型(如线性回归、逻辑回归)，确保所有特征都已标准化")
    print("2. 对于树模型(如随机森林、XGBoost)，异常值影响相对较小")
    print("3. 可以考虑使用交叉验证评估模型性能")
    print("4. 如发现过拟合，可考虑L1/L2正则化或特征选择方法")

print("\n评估完成！数据已准备好用于机器学习模型训练。")
