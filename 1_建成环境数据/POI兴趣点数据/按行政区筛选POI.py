import pandas as pd
import os

# 设置文件路径
file_path = '西安市_陕西省_2025poi.csv'

# 定义西安市六大主城区
main_districts = ['新城区', '碑林区', '莲湖区', '灞桥区', '未央区', '雁塔区']

# 读取CSV文件
print("开始读取POI数据文件...")
df = pd.read_csv(file_path)
print(f"文件读取完成，共{len(df)}条数据")

# 创建一个汇总统计字典
stats = {}

# 为每个主城区筛选数据并保存
for district in main_districts:
    print(f"\n正在处理{district}的数据...")
    # 筛选当前行政区的数据
    district_data = df[df['adName'] == district].copy()
    
    # 保存到单独的CSV文件
    output_file = f'西安市_{district}_POI.csv'
    district_data.to_csv(output_file, index=False, encoding='utf-8')
    
    # 记录统计信息
    stats[district] = len(district_data)
    print(f"{district}数据已保存，共{len(district_data)}条POI记录")

# 输出汇总统计
print("\n" + "="*50)
print("西安市六大主城区POI数据汇总")
print("="*50)
for district, count in stats.items():
    print(f"{district}: {count}个POI")

# 保存汇总统计到文件
with open('六大主城区POI汇总统计.txt', 'w', encoding='utf-8') as f:
    f.write("西安市六大主城区POI数据汇总\n")
    f.write("="*30 + "\n")
    for district, count in stats.items():
        f.write(f"{district}: {count}个POI\n")
    f.write("="*30 + "\n")
    f.write(f"总计：{sum(stats.values())}个POI")

print(f"\n汇总统计已保存到：六大主城区POI汇总统计.txt")