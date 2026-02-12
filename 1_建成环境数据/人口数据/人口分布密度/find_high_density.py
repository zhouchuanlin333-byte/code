import pandas as pd

# 读取CSV文件
csv_path = "d:\Desktop\项目论文\人口数据\人口分布密度\gridid_population_density.csv"
df = pd.read_csv(csv_path)

# 找出人口密度最高的前20个网格
high_density_grids = df.nlargest(20, 'population_density')

print("人口密度最高的20个网格:")
print(high_density_grids)

# 计算数据统计信息
print("\n人口密度统计:")
print(f"最大值: {df['population_density'].max()}")
print(f"平均值: {df['population_density'].mean()}")
print(f"中位数: {df['population_density'].median()}")
print(f"非零值数量: {(df['population_density'] > 0).sum()}")
