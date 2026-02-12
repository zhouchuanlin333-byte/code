import pandas as pd

# 读取早高峰和晚高峰的标准化数据
early_peak_df = pd.read_csv('优化后_早高峰_标准化_utf8.csv')
evening_peak_df = pd.read_csv('优化后_晚高峰_标准化_utf8.csv')

print("=== 早高峰数据标准化验证 ===")
print("各列均值:")
print(early_peak_df.mean().round(6))
print("\n各列标准差:")
print(early_peak_df.std().round(6))
print("\n=== 晚高峰数据标准化验证 ===")
print("各列均值:")
print(evening_peak_df.mean().round(6))
print("\n各列标准差:")
print(evening_peak_df.std().round(6))

# 检查是否符合z-score标准化（均值接近0，标准差接近1）
print("\n=== 标准化方法验证结果 ===")
print("早高峰数据均值是否接近0:", all(abs(early_peak_df.mean()) < 0.001))
print("早高峰数据标准差是否接近1:", all(abs(early_peak_df.std() - 1) < 0.001))
print("晚高峰数据均值是否接近0:", all(abs(evening_peak_df.mean()) < 0.001))
print("晚高峰数据标准差是否接近1:", all(abs(evening_peak_df.std() - 1) < 0.001))
