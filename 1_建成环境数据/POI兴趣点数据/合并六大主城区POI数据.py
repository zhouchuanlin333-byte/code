import pandas as pd
import os

# 定义六大主城区
districts = ['新城区', '碑林区', '莲湖区', '灞桥区', '未央区', '雁塔区']

# 创建一个空的DataFrame来存储合并后的数据
merged_data = pd.DataFrame()
print("开始合并六大主城区POI数据...")

# 遍历每个行政区文件
for district in districts:
    file_name = f'西安市_{district}_POI.csv'
    if os.path.exists(file_name):
        print(f"正在处理：{file_name}")
        # 读取当前行政区的POI数据
        district_df = pd.read_csv(file_name)
        # 添加行政区标识列
        district_df['城区标识'] = district
        # 将当前行政区数据添加到合并数据中
        merged_data = pd.concat([merged_data, district_df], ignore_index=True)
        print(f"已添加{district}，当前合并数据总量：{len(merged_data)}")
    else:
        print(f"警告：文件 {file_name} 不存在！")

# 保存合并后的数据到CSV文件
output_file = '西安市六大主城区POI数据汇总.csv'
merged_data.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n数据合并完成！")
print(f"总共合并了 {len(merged_data)} 条POI记录")
print(f"汇总数据已保存到：{output_file}")

# 输出各城区数据量统计
print("\n各城区POI数据量统计：")
district_counts = merged_data['城区标识'].value_counts()
for district, count in district_counts.items():
    print(f"{district}: {count}条记录")