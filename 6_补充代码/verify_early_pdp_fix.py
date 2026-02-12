import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("验证早高峰'到市中心距离'PDP图修复结果...")

# 加载数据
time_of_day = "早高峰"

# 加载标准化数据
std_file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv"
real_file_path = "d:/Desktop/项目论文/建模/早高峰_统一单位.csv"

std_df = pd.read_csv(std_file_path)
real_df = pd.read_csv(real_file_path)

# 确保列名一致
std_df.columns = [col.strip() for col in std_df.columns]
real_df.columns = [col.strip() for col in real_df.columns]

# 分离特征和目标变量
X = std_df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
y = std_df['碳排放_carbon_emission_kg (kgCO2/KM/d)']

# 训练模型（与原脚本相同的参数）
print("\n1. 训练XGBoost模型...")
model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
model.fit(X, y)

# 获取特征
feature = "到市中心距离 (km)"

# 获取碳排放的真实统计信息
carbon_col = '碳排放_carbon_emission_kg (kgCO2/KM/d)'
real_carbon_mean = real_df[carbon_col].mean()
real_carbon_std = real_df[carbon_col].std()

# 获取特征在真实数据中的统计信息
feature_real_mean = real_df[feature].mean()
feature_real_std = real_df[feature].std()
feature_real_min = real_df[feature].min()
feature_real_max = real_df[feature].max()

print(f"\n2. 早高峰特征信息:")
print(f"   特征: {feature}")
print(f"   真实范围: {feature_real_min:.2f} - {feature_real_max:.2f} km")
print(f"   真实均值: {feature_real_mean:.2f} km")
print(f"   真实标准差: {feature_real_std:.2f} km")

# 创建PDP图数据
print("\n3. 生成PDP图数据...")
grid_points = 50  # 使用更少的点以提高可读性

# 创建基于真实值的特征网格
real_feature_grid = np.linspace(0, 30, grid_points)  # 0到30km的范围

# 将真实值转换为标准化值用于模型预测
std_feature_grid = (real_feature_grid - feature_real_mean) / feature_real_std

# 创建包含所有特征的副本
X_pdp = X.copy()

# 固定其他特征为均值
for col in X_pdp.columns:
    if col != feature:
        X_pdp[col] = X_pdp[col].mean()

# 预测每个网格点的碳排放值
pdp_values = []
for val in std_feature_grid:
    X_pdp[feature] = val
    pred = model.predict(X_pdp)
    pdp_values.append(np.mean(pred))

# 将预测值从标准化值转换为真实的碳排放值
real_pdp_values = np.array(pdp_values) * real_carbon_std + real_carbon_mean

# 绘制PDP图
print("\n4. 绘制早高峰PDP图...")
plt.figure(figsize=(12, 6))

# 绘制PDP曲线
plt.plot(real_feature_grid, real_pdp_values, linewidth=2.5, color='blue', label='PDP曲线')

# 标记实际数据范围
plt.axvline(x=feature_real_min, color='red', linestyle='--', alpha=0.7, label=f'实际数据最小值 {feature_real_min:.2f} km')
plt.axvline(x=feature_real_max, color='red', linestyle='--', alpha=0.7, label=f'实际数据最大值 {feature_real_max:.2f} km')

# 标记市中心位置
plt.axvline(x=0, color='green', linestyle='-', alpha=0.7, label='市中心')

# 设置图表属性
plt.title(f'{time_of_day} - {feature} 部分依赖图（修复后）', fontsize=14, fontweight='bold')
plt.xlabel(f'{feature}', fontsize=12)
plt.ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=10)

# 优化x轴刻度
plt.xticks(np.arange(0, 32, 2))

# 保存验证图
plt.tight_layout()
plt.savefig('修复后的_早高峰_到市中心距离_pdp验证图.png', dpi=300)
plt.close()

# 检查PDP曲线变化
print("\n5. PDP曲线变化分析:")
# 计算曲线的变化率
changes = np.diff(real_pdp_values)
max_change_idx = np.argmax(np.abs(changes))
max_change_value = real_feature_grid[max_change_idx] + (real_feature_grid[1] - real_feature_grid[0])/2

print(f"   曲线最大变化点: {max_change_value:.2f} km 处")
print(f"   市中心(0km)处碳排放: {real_pdp_values[0]:.2f} kgCO2/KM/d")
print(f"   10km处碳排放: {real_pdp_values[np.argmin(np.abs(real_feature_grid - 10))]:.2f} kgCO2/KM/d")
print(f"   20km处碳排放: {real_pdp_values[np.argmin(np.abs(real_feature_grid - 20))]:.2f} kgCO2/KM/d")
print(f"   30km处碳排放: {real_pdp_values[-1]:.2f} kgCO2/KM/d")

# 检查生成的PDP图文件是否存在
print("\n6. 检查生成的PDP图文件...")
pdp_file_path = f"d:/Desktop/项目论文/SHAP值解释性分析/PDP_真实数据刻度/{time_of_day}/{time_of_day}_到市中心距离_km_pdp_真实刻度.png"

if os.path.exists(pdp_file_path):
    print(f"✅ 早高峰PDP图文件已成功生成: {os.path.basename(pdp_file_path)}")
    print(f"   文件大小: {os.path.getsize(pdp_file_path) / 1024:.2f} KB")
else:
    print(f"❌ 早高峰PDP图文件不存在: {pdp_file_path}")

# 绘制实际数据散点图作为参考
print("\n7. 实际数据分布参考...")
sample_size = 1000  # 采样部分数据以提高性能
if len(real_df) > sample_size:
    sampled_df = real_df.sample(n=sample_size, random_state=42)
else:
    sampled_df = real_df

plt.figure(figsize=(12, 6))

# 绘制实际数据散点图
plt.scatter(sampled_df[feature], sampled_df[carbon_col], alpha=0.3, color='orange', label='实际数据点')

# 绘制PDP曲线
plt.plot(real_feature_grid, real_pdp_values, linewidth=2.5, color='blue', label='PDP曲线')

# 设置图表属性
plt.title(f'{time_of_day} - {feature} 实际数据与PDP曲线对比', fontsize=14, fontweight='bold')
plt.xlabel(f'{feature}', fontsize=12)
plt.ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=10)

# 优化x轴刻度
plt.xticks(np.arange(0, 32, 2))

# 保存对比图
plt.tight_layout()
plt.savefig('早高峰_到市中心距离_实际数据与PDP对比图.png', dpi=300)
plt.close()

print("\n✅ 早高峰PDP图验证完成！")
print("   生成的验证图:")
print("   - 修复后的_早高峰_到市中心距离_pdp验证图.png")
print("   - 早高峰_到市中心距离_实际数据与PDP对比图.png")
