import pandas as pd
import os

print("="*60)
print("修复道路密度数据标准化问题")
print("="*60)

# 设置文件路径
input_dir = 'd:/Desktop/项目论文/建模/特征工程'
output_dir = 'd:/Desktop/项目论文/建模/特征工程'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 修复数据的函数
def fix_standardization(file_path):
    """修复数据文件中的标准化问题，删除空值列"""
    print(f"\n处理文件: {os.path.basename(file_path)}")
    
    # 读取数据
    df = pd.read_csv(file_path, encoding='utf-8')
    print(f"原始列数: {len(df.columns)}")
    print(f"原始列名: {list(df.columns)}")
    
    # 检查空值列
    empty_cols = []
    for col in df.columns:
        if df[col].isnull().all():
            empty_cols.append(col)
            print(f"发现空值列: {col}")
    
    # 删除空值列
    if empty_cols:
        df_fixed = df.drop(columns=empty_cols)
        print(f"删除空值列后列数: {len(df_fixed.columns)}")
        print(f"删除空值列后列名: {list(df_fixed.columns)}")
    else:
        df_fixed = df
        print("未发现空值列")
    
    # 验证道路密度是否已标准化
    road_density_col = None
    for col in df_fixed.columns:
        if '道路密度' in col:
            road_density_col = col
            break
    
    if road_density_col:
        mean_val = df_fixed[road_density_col].mean()
        std_val = df_fixed[road_density_col].std()
        min_val = df_fixed[road_density_col].min()
        max_val = df_fixed[road_density_col].max()
        print(f"\n道路密度数据统计:")
        print(f"  均值: {mean_val:.6f}")
        print(f"  标准差: {std_val:.6f}")
        print(f"  最小值: {min_val:.6f}")
        print(f"  最大值: {max_val:.6f}")
        
        # 检查是否已标准化（均值接近0，标准差接近1）
        is_standardized = abs(mean_val) < 0.1 and 0.9 < std_val < 1.1
        print(f"  是否已标准化: {'是' if is_standardized else '否'}")
    
    return df_fixed

# 修复早高峰数据
early_peak_file = os.path.join(input_dir, '优化后_早高峰_标准化_utf8.csv')
if os.path.exists(early_peak_file):
    early_peak_fixed = fix_standardization(early_peak_file)
    output_file = os.path.join(output_dir, '修复后_早高峰_标准化_utf8.csv')
    early_peak_fixed.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n早高峰数据已修复并保存到: {output_file}")
else:
    print(f"\n早高峰数据文件不存在: {early_peak_file}")

# 修复晚高峰数据
late_peak_file = os.path.join(input_dir, '优化后_晚高峰_标准化_utf8.csv')
if os.path.exists(late_peak_file):
    late_peak_fixed = fix_standardization(late_peak_file)
    output_file = os.path.join(output_dir, '修复后_晚高峰_标准化_utf8.csv')
    late_peak_fixed.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n晚高峰数据已修复并保存到: {output_file}")
else:
    print(f"\n晚高峰数据文件不存在: {late_peak_file}")

print("\n" + "="*60)
print("数据修复完成！")
print("="*60)