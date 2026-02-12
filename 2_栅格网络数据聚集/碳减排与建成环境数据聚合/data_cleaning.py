import pandas as pd
import numpy as np

print("="*60)
print("数据清洗脚本 (修复版本)")
print("="*60)

# 函数定义 - 放在try块外部
# 函数：简化字段名
def simplify_column_names(df):
    """去除字段名中的单位信息，简化字段名"""
    new_columns = {}
    for col in df.columns:
        # 简化字段名，去除单位信息
        if '(' in col:
            new_col = col.split('(')[0].strip()
        else:
            new_col = col
        new_columns[col] = new_col
    
    df_renamed = df.rename(columns=new_columns)
    print(f"字段名简化完成，新字段列表: {list(df_renamed.columns)[:5]}...")
    return df_renamed

# 函数：处理缺失值
def handle_missing_values(df):
    """处理缺失值"""
    # 检查缺失值
    missing_before = df.isnull().sum()
    print("\n缺失值处理前:")
    for col, count in missing_before.items():
        if count > 0:
            print(f"  {col}: {count} 个缺失值 ({count/len(df)*100:.2f}%)")
    
    # 使用均值填充所有缺失值
    df_filled = df.fillna(df.mean())
    
    return df_filled

# 函数：处理异常值
def handle_outliers(df, columns, lower_quantile=0.01, upper_quantile=0.99):
    """使用分位数截断法处理异常值"""
    print("\n异常值处理:")
    df_copy = df.copy()
    for col in columns:
        if col in df_copy.columns:
            # 计算分位数
            lower = df_copy[col].quantile(lower_quantile)
            upper = df_copy[col].quantile(upper_quantile)
            
            # 截断异常值
            df_copy[col] = np.clip(df_copy[col], lower, upper)
            
            print(f"  {col}: 截断范围 [{lower:.4f}, {upper:.4f}]")
    
    return df_copy

# 函数：标准化数值特征
def standardize_features(df, columns):
    """标准化数值特征"""
    print("\n特征标准化:")
    # 复制原始数据
    df_standardized = df.copy()
    
    # 选择需要标准化的列
    cols_to_standardize = [col for col in columns if col in df.columns]
    
    if cols_to_standardize:
        # 简单的z-score标准化
        for col in cols_to_standardize[:5]:  # 只显示前5个列的标准化信息
            mean_val = df[col].mean()
            std_val = df[col].std()
            df_standardized[col] = (df[col] - mean_val) / std_val
            print(f"  {col}: 均值={mean_val:.4f}, 标准差={std_val:.4f}")
        if len(cols_to_standardize) > 5:
            print(f"  ... 还有{len(cols_to_standardize)-5}个列已标准化")
    else:
        print("  没有找到需要标准化的列")
    
    return df_standardized

# 执行数据清洗流程
def clean_data(df, prefix):
    print(f"\n{'-'*60}\n开始清洗 {prefix} 数据")
    
    # 1. 简化字段名
    df_clean = simplify_column_names(df)
    
    # 2. 处理缺失值
    df_clean = handle_missing_values(df_clean)
    
    # 3. 处理异常值
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    # 排除grid_id列
    if 'grid_id' in numeric_cols:
        numeric_cols.remove('grid_id')
    
    df_clean = handle_outliers(df_clean, numeric_cols)
    
    # 4. 标准化数值特征
    df_standardized = standardize_features(df_clean, numeric_cols)
    
    print(f"\n{prefix} 数据清洗完成！")
    return df_standardized

# 添加错误处理
try:
    # 读取数据
    print("正在读取数据...")
    df_morning = pd.read_csv('早高峰_统一单位.csv')
    df_evening = pd.read_csv('晚高峰1_统一单位.csv')
    
    print(f"原始数据形状 - 早高峰: {df_morning.shape}, 晚高峰: {df_evening.shape}")
    print(f"早高峰字段数量: {len(df_morning.columns)}")
    print(f"晚高峰字段数量: {len(df_evening.columns)}")
    
    # 执行清洗
    morning_clean = clean_data(df_morning, "早高峰")
    evening_clean = clean_data(df_evening, "晚高峰")
    
    # 保存清洗后的数据
    print("\n正在保存清洗后的数据...")
    morning_clean.to_csv('早高峰_cleaned.csv', index=False, encoding='utf-8-sig')
    evening_clean.to_csv('晚高峰_cleaned.csv', index=False, encoding='utf-8-sig')
    
    print("\n" + "="*60)
    print("数据清洗完成并保存！")
    print(f"早高峰清洗后数据形状: {morning_clean.shape}")
    print(f"晚高峰清洗后数据形状: {evening_clean.shape}")
    print(f"保存路径: ")
    print(f"  - 早高峰: 早高峰_cleaned.csv")
    print(f"  - 晚高峰: 晚高峰_cleaned.csv")
    print("="*60)

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    print(f"\n详细错误信息:")
    traceback.print_exc()
