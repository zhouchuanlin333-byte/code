import pandas as pd
import os

# 原始数据文件路径
input_file = r'D:\Desktop\项目文件\低碳项目\西安市网约车、出租车、共享单车一周运营里程数据\Chuzucheqingxi\共享单车数据_精确\共享单车数据_清洗后_8月8日_精确.csv'

print(f"开始读取原始数据文件: {input_file}")

# 读取前10行数据查看时间格式
df = pd.read_csv(input_file, encoding='utf-8', nrows=10)

print("前10行数据:")
print(df)

# 查看时间列的具体内容
print("\n订单开始时间列内容:")
print(df['订单开始时间'])

print("\n订单结束时间列内容:")
print(df['订单结束时间'])
