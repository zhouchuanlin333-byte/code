import pandas as pd

# 读取数据
df = pd.read_csv('d:/Desktop/项目论文/建模/早高峰_统一单位.csv')
df.columns = [col.strip() for col in df.columns]

print('所有列名：')
for i, col in enumerate(df.columns):
    print(f'{i}: {repr(col)}')

print('\n包含休闲的列：')
for col in df.columns:
    if '休闲' in col:
        print(repr(col))

print('\n包含POI的列：')
for col in df.columns:
    if 'POI' in col:
        print(repr(col))