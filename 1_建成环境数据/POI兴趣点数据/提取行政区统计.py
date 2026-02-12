import pandas as pd
import os

# 设置文件路径
file_path = '西安市_陕西省_2025poi.csv'

# 读取CSV文件
print("开始读取POI数据文件...")
df = pd.read_csv(file_path)
print(f"文件读取完成，共{len(df)}条数据")

# 提取并统计行政区名称
print("\n正在统计各行政区POI数量...")
district_stats = df['adName'].value_counts()

# 输出统计结果
print("\n各行政区POI数量统计：")
for district, count in district_stats.items():
    print(f"{district}: {count}个POI")

# 输出总行政区数量
print(f"\n共有{len(district_stats)}个行政区")

# 保存统计结果到文件
output_file = '行政区_POI统计结果.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("西安市各行政区POI数量统计\n")
    f.write("="*30 + "\n")
    for district, count in district_stats.items():
        f.write(f"{district}: {count}个POI\n")
    f.write("="*30 + "\n")
    f.write(f"总计：{len(district_stats)}个行政区\n")
    f.write(f"总POI数量：{len(df)}个")

print(f"\n统计结果已保存到：{output_file}")