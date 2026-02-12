import pandas as pd
import os

# 定义六大主城区
districts = ['新城区', '碑林区', '莲湖区', '灞桥区', '未央区', '雁塔区']

# 验证每个文件
total_poi = 0
for district in districts:
    file_name = f'西安市_{district}_POI.csv'
    if os.path.exists(file_name):
        print(f"\n验证文件：{file_name}")
        # 读取文件
        df = pd.read_csv(file_name)
        print(f"文件包含 {len(df)} 条记录")
        total_poi += len(df)
        
        # 检查行政区字段是否正确
        unique_districts = df['adName'].unique()
        print(f"文件中包含的行政区：{unique_districts}")
        
        # 显示前2条记录样例
        print("\n前2条记录样例：")
        print(df.head(2))
        
        # 检查是否包含所有必要的列
        print("\n文件列信息：")
        for col in df.columns:
            print(f"- {col}")
        print("="*60)
    else:
        print(f"错误：文件 {file_name} 不存在！")

print(f"\n总计：六大主城区共包含 {total_poi} 个POI记录")
print("\n文件验证完成！")