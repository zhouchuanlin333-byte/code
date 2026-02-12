import pandas as pd
import numpy as np

# 检查标准化和真实数据的特征范围
print("检查特征标准化前后的范围...")

# 加载真实数据
real_df_early = pd.read_csv("d:/Desktop/项目论文/建模/早高峰_统一单位.csv")
real_df_late = pd.read_csv("d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv")

# 加载标准化数据
std_df_early = pd.read_csv("d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv")
std_df_late = pd.read_csv("d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv")

# 确保列名一致
real_df_early.columns = [col.strip() for col in real_df_early.columns]
real_df_late.columns = [col.strip() for col in real_df_late.columns]
std_df_early.columns = [col.strip() for col in std_df_early.columns]
std_df_late.columns = [col.strip() for col in std_df_late.columns]

# 比较标准化前后的特征范围
feature = "到市中心距离 (km)"
print(f"\n特征: {feature}")

# 早高峰
print("早高峰:")
print(f"  真实数据范围: {real_df_early[feature].min():.2f} - {real_df_early[feature].max():.2f} km")
print(f"  标准化数据范围: {std_df_early[feature].min():.2f} - {std_df_early[feature].max():.2f}")
print(f"  真实数据均值: {real_df_early[feature].mean():.2f} km")
print(f"  真实数据标准差: {real_df_early[feature].std():.2f} km")

# 晚高峰
print("晚高峰:")
print(f"  真实数据范围: {real_df_late[feature].min():.2f} - {real_df_late[feature].max():.2f} km")
print(f"  标准化数据范围: {std_df_late[feature].min():.2f} - {std_df_late[feature].max():.2f}")
print(f"  真实数据均值: {real_df_late[feature].mean():.2f} km")
print(f"  真实数据标准差: {real_df_late[feature].std():.2f} km")

# 计算逆标准化的转换
print(f"\n逆标准化转换示例:")
std_value = 1.0
real_value_early = std_value * real_df_early[feature].std() + real_df_early[feature].mean()
real_value_late = std_value * real_df_late[feature].std() + real_df_late[feature].mean()
print(f"  标准化值=1.0 -> 早高峰真实值={real_value_early:.2f} km")
print(f"  标准化值=1.0 -> 晚高峰真实值={real_value_late:.2f} km")

# 检查特征列名是否一致
print(f"\n特征列名检查:")
print(f"  真实数据早高峰特征列: {[col for col in real_df_early.columns if '距离' in col]}")
print(f"  标准化数据早高峰特征列: {[col for col in std_df_early.columns if '距离' in col]}")
print(f"  真实数据晚高峰特征列: {[col for col in real_df_late.columns if '距离' in col]}")
print(f"  标准化数据晚高峰特征列: {[col for col in std_df_late.columns if '距离' in col]}")

# 查看标准化数据的前几行
print(f"\n标准化数据前5行 ({feature}):")
print(std_df_early[feature].head())
print(std_df_late[feature].head())

# 查看真实数据的前几行
print(f"\n真实数据前5行 ({feature}):")
print(real_df_early[feature].head())
print(real_df_late[feature].head())

# 计算标准化公式是否正确
print(f"\n标准化公式验证:")
real_sample = real_df_early[feature].iloc[0]
std_sample = std_df_early[feature].iloc[0]
calc_std_sample = (real_sample - real_df_early[feature].mean()) / real_df_early[feature].std()
print(f"  真实值: {real_sample:.2f} km -> 实际标准化值: {std_sample:.4f}, 计算标准化值: {calc_std_sample:.4f}")
print(f"  误差: {abs(std_sample - calc_std_sample):.6f}")
