import pandas as pd
import os

# 原始数据文件路径
input_file = r'D:\Desktop\项目文件\低碳项目\西安市网约车、出租车、共享单车一周运营里程数据\Chuzucheqingxi\共享单车数据_精确\共享单车数据_清洗后_8月8日_精确.csv'

# 输出数据文件路径
output_dir = r'D:\Desktop\项目论文\全天时段订单趋势分析'
output_file = os.path.join(output_dir, '共享单车数据_8月8日_清洗完成.csv')

print(f"开始读取原始数据文件: {input_file}")

# 读取CSV文件
df = pd.read_csv(input_file, encoding='utf-8')

print(f"原始数据总行数: {len(df)}")
print(f"数据列名: {df.columns.tolist()}")

# 检查是否存在必要的时间列
if '订单开始时间' not in df.columns or '订单结束时间' not in df.columns:
    raise ValueError("数据中缺少必要的时间列：'订单开始时间'或'订单结束时间'")

# 转换时间列为datetime格式
df['订单开始时间'] = pd.to_datetime(df['订单开始时间'])
df['订单结束时间'] = pd.to_datetime(df['订单结束时间'])

print("时间列转换完成")

# 1. 删除起止时间都不是8月8日的订单
# 保留至少有一个时间点在8月8日的订单
# 创建目标日期对象 (2025-08-08)
target_date = pd.to_datetime('2025-08-08').date()

# 检查开始时间或结束时间是否在8月8日
df = df[(df['订单开始时间'].dt.date == target_date) | (df['订单结束时间'].dt.date == target_date)]

print(f"保留至少有一个时间点在8月8日的订单后，剩余行数: {len(df)}")

# 2. 计算订单时间（分钟）
df['订单时长(分钟)'] = (df['订单结束时间'] - df['订单开始时间']).dt.total_seconds() / 60

print(f"订单时长计算完成，平均订单时长: {df['订单时长(分钟)'].mean():.2f} 分钟")

# 3. 删除订单时间小于5分钟的订单
df = df[df['订单时长(分钟)'] >= 5]

print(f"删除订单时间小于5分钟的订单后，剩余行数: {len(df)}")

# 4. 删除订单时间大于50分钟的订单
df = df[df['订单时长(分钟)'] <= 50]

print(f"删除订单时间大于50分钟的订单后，剩余行数: {len(df)}")

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 保存处理后的DataFrame
df.to_csv(output_file, index=False, encoding='utf-8')
print(f"处理完成，数据已保存到: {output_file}")
print(f"清洗后数据总行数: {len(df)}")
