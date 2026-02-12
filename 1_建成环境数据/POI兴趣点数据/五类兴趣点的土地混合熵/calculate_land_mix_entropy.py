import pandas as pd
import numpy as np
import os

# 设置输入和输出路径
input_file = "D:/Desktop/项目论文/POI兴趣点数据/5类兴趣点/重新_网格POI数量统计.csv"
output_dir = "D:/Desktop/项目论文/POI兴趣点数据/五类兴趣点的土地混合熵"
output_file = os.path.join(output_dir, "网格土地利用混合熵.csv")

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 读取CSV数据
print("正在读取POI数据...")
df = pd.read_csv(input_file)
print(f"成功读取数据，共{len(df)}个网格")

# 定义计算混合熵的函数
def calculate_entropy(row):
    # 获取五类兴趣点的数量
    categories = ['休闲_count', '办公_count', '公共服务_count', '交通设施_count', '居住_count']
    counts = row[categories].values
    
    # 计算总数量
    total = counts.sum()
    
    # 避免除以零错误，如果总数量为0，则熵为0
    if total == 0:
        return 0
    
    # 计算每个类别的比例
    proportions = counts / total
    
    # 过滤掉比例为0的值，避免log(0)错误
    proportions = proportions[proportions > 0]
    
    # 计算熵
    entropy = -np.sum(proportions * np.log(proportions))
    
    return entropy

# 计算每个网格的混合熵
print("正在计算每个网格的土地利用混合熵...")
df['land_mix_entropy'] = df.apply(calculate_entropy, axis=1)

# 计算理论最大熵（当所有类别均匀分布时）
max_entropy = -np.log(1/5)  # 5个类别，均匀分布时每个类别的比例为1/5
print(f"理论最大熵值: {max_entropy:.6f}")

# 添加标准化混合熵 (除以理论最大熵)
df['normalized_entropy'] = df['land_mix_entropy'] / max_entropy

# 生成结果数据框，包含网格ID、原始混合熵和标准化混合熵
result_df = df[['grid_id', 'land_mix_entropy', 'normalized_entropy']]

# 保存结果
result_df.to_csv(output_file, index=False)
print(f"计算完成！结果已保存至: {output_file}")

# 原始混合熵统计信息
print("\n原始混合熵统计信息：")
print(f"最小值: {result_df['land_mix_entropy'].min():.6f}")
print(f"最大值: {result_df['land_mix_entropy'].max():.6f}")
print(f"平均值: {result_df['land_mix_entropy'].mean():.6f}")
print(f"中位数: {result_df['land_mix_entropy'].median():.6f}")

# 标准化混合熵统计信息
print("\n标准化混合熵统计信息：")
print(f"最小值: {result_df['normalized_entropy'].min():.6f}")
print(f"最大值: {result_df['normalized_entropy'].max():.6f}")
print(f"平均值: {result_df['normalized_entropy'].mean():.6f}")
print(f"中位数: {result_df['normalized_entropy'].median():.6f}")

# 计算原始混合熵的分布
print("\n原始混合熵分布：")
entropy_bins = pd.cut(result_df['land_mix_entropy'], bins=5)
print(entropy_bins.value_counts().sort_index())

# 计算标准化混合熵的分布
print("\n标准化混合熵分布：")
norm_entropy_bins = pd.cut(result_df['normalized_entropy'], bins=5)
print(norm_entropy_bins.value_counts().sort_index())