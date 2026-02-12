import pandas as pd

# 加载早高峰原始数据
file_path = 'd:/Desktop/项目论文/建模/早高峰_统一单位.csv'
df = pd.read_csv(file_path)
df = df.dropna(axis=1, how='all')
df.columns = [col.strip() for col in df.columns]

print('早高峰数据列名：')
for i, col in enumerate(df.columns):
    print(f'{i}: {col}')

print(f'\n公共服务POI数量在数据中: {"公共服务POI数量 (个)" in df.columns}')
print(f'交通设施POI数量在数据中: {"交通设施POI数量 (个)" in df.columns}')

# 检查数据形状
print(f'\n数据形状: {df.shape}')
print(f'公共服务POI数量的值范围: {df["公共服务POI数量 (个)"].min()} - {df["公共服务POI数量 (个)"].max()}')
print(f'交通设施POI数量的值范围: {df["交通设施POI数量 (个)"].min()} - {df["交通设施POI数量 (个)"].max()}')