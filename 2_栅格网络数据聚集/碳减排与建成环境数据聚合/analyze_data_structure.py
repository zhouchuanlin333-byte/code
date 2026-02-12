import pandas as pd
import numpy as np

# 设置显示选项，确保完整显示
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("="*60)
print("数据分析脚本 - 检查数据结构和质量")
print("="*60)

# 读取两个CSV文件
try:
    df_morning = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
    df_evening = pd.read_csv('d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv')
    print("✓ 文件读取成功")
except Exception as e:
    print(f"✗ 文件读取失败: {e}")
    exit()

# 1. 基本信息分析
print("\n" + "="*60)
print("1. 基本信息对比")
print("="*60)

print(f"早高峰数据: {df_morning.shape[0]} 行, {df_morning.shape[1]} 列")
print(f"晚高峰数据: {df_evening.shape[0]} 行, {df_evening.shape[1]} 列")

# 2. 字段信息分析
print("\n" + "="*60)
print("2. 字段信息")
print("="*60)

print("\n字段名称列表:")
for i, col in enumerate(df_morning.columns):
    print(f"{i+1}. {col}")

print("\n字段数据类型:")
print(df_morning.dtypes)

# 3. 缺失值检查
print("\n" + "="*60)
print("3. 缺失值检查")
print("="*60)

print("早高峰缺失值统计:")
missing_morning = df_morning.isnull().sum()
for col, missing in missing_morning.items():
    if missing > 0:
        print(f"  {col}: {missing} 个缺失值 ({missing/len(df_morning)*100:.2f}%)")

print("\n晚高峰缺失值统计:")
missing_evening = df_evening.isnull().sum()
for col, missing in missing_evening.items():
    if missing > 0:
        print(f"  {col}: {missing} 个缺失值 ({missing/len(df_evening)*100:.2f}%)")

# 4. 数据统计分析
print("\n" + "="*60)
print("4. 数值型字段统计摘要")
print("="*60)

print("早高峰数值型字段统计:")
numeric_cols = df_morning.select_dtypes(include=['float64', 'int64']).columns
for col in numeric_cols:
    print(f"\n{col}:")
    print(f"  最小值: {df_morning[col].min()}")
    print(f"  最大值: {df_morning[col].max()}")
    print(f"  平均值: {df_morning[col].mean():.4f}")
    print(f"  标准差: {df_morning[col].std():.4f}")
    # 检查是否有负值
    if (df_morning[col] < 0).any():
        print(f"  ⚠️  存在负值: {(df_morning[col] < 0).sum()} 个")

# 5. 单位检查和字段名标准化建议
print("\n" + "="*60)
print("5. 数据清洗建议")
print("="*60)

print("字段名标准化建议:")
for col in df_morning.columns:
    # 去除括号和单位信息，简化字段名
    new_col = col.split('(')[0].strip()
    if new_col != col:
        print(f"  '{col}' → '{new_col}'")

print("\n数据清洗注意事项:")
# 检查道路密度字段是否有缺失值
if '道路密度 (KM/KM²)' in df_morning.columns:
    if df_morning['道路密度 (KM/KM²)'].isnull().any():
        print("  ⚠️  道路密度字段存在缺失值，需要处理")

# 检查是否有异常值
print("\n异常值检查:")
for col in numeric_cols:
    # 检查是否有极端大的值
    Q1 = df_morning[col].quantile(0.25)
    Q3 = df_morning[col].quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df_morning[col] < (Q1 - 1.5 * IQR)) | (df_morning[col] > (Q3 + 1.5 * IQR)))
    if outliers.any():
        print(f"  {col}: 检测到 {outliers.sum()} 个异常值")

print("\n" + "="*60)
print("数据分析完成！")
print("="*60)
