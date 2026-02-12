import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from matplotlib.font_manager import FontProperties

# 设置字体
from matplotlib.font_manager import FontProperties
# 创建字体对象
roman_font = FontProperties(family='Times New Roman')
simsun_font = FontProperties(family='SimSun')
# 设置全局字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 数据文件路径
input_file = r'D:\Desktop\项目论文\全天时段订单趋势分析\共享单车数据_8月8日_清洗完成.csv'

# 输出目录
output_dir = r'D:\Desktop\项目论文\灰白图'

print(f"开始读取清洗后的数据文件: {input_file}")

# 读取CSV文件
df = pd.read_csv(input_file, encoding='utf-8')

print(f"清洗后数据总行数: {len(df)}")
print(f"数据列名: {df.columns.tolist()}")

# 转换时间列为datetime格式
df['订单开始时间'] = pd.to_datetime(df['订单开始时间'])
df['订单结束时间'] = pd.to_datetime(df['订单结束时间'])

print("时间列转换完成")

# 按照小时统计订单总量
# 提取订单开始时间的小时部分
df['开始小时'] = df['订单开始时间'].dt.hour

# 按小时分组统计订单数量
hourly_orders = df.groupby('开始小时').size().reset_index(name='订单数量')

# 确保所有小时都有数据（0-23小时）
all_hours = pd.DataFrame({'开始小时': range(24)})
hourly_orders = pd.merge(all_hours, hourly_orders, on='开始小时', how='left')
hourly_orders['订单数量'] = hourly_orders['订单数量'].fillna(0).astype(int)

print("\n每小时订单量统计结果:")
print(hourly_orders.to_string(index=False))

# 计算一些统计指标
total_orders = hourly_orders['订单数量'].sum()
max_hour = hourly_orders.loc[hourly_orders['订单数量'].idxmax()]['开始小时']
max_orders = hourly_orders['订单数量'].max()
min_hour = hourly_orders.loc[hourly_orders['订单数量'].idxmin()]['开始小时']
min_orders = hourly_orders['订单数量'].min()
avg_orders = hourly_orders['订单数量'].mean()

print(f"\n统计摘要:")
print(f"总订单数: {total_orders}")
print(f"平均每小时订单数: {avg_orders:.1f}")
print(f"订单最多的小时: {max_hour}时, 订单数: {max_orders}")
print(f"订单最少的小时: {min_hour}时, 订单数: {min_orders}")

# 可视化展示 - 设置宽度为8CM（≈3.15英寸）
plt.figure(figsize=(3.15, 2.0), dpi=300)

# 将订单数量转换为千个单位
hourly_orders['订单数量_千个'] = hourly_orders['订单数量'] / 1000

# 创建折线图
sns.lineplot(x='开始小时', y='订单数量_千个', data=hourly_orders, linewidth=2.0, marker='o', markersize=5, color='black')

# 添加柱状图作为辅助
# 先创建基础柱状图，为不同时段设置不同颜色
colors = []
for hour in hourly_orders['开始小时']:
    # 早高峰(7-9点)和晚高峰(17-19点)使用黑色
    if (hour >= 7 and hour <= 9) or (hour >= 17 and hour <= 19):
        colors.append('black')  # 黑色
    else:
        colors.append('#CCCCCC')  # 灰色
bars = plt.bar(hourly_orders['开始小时'], hourly_orders['订单数量_千个'], alpha=0.7, color=colors)



# 设置图表标签（删除标题）
plt.xlabel('时间/h', fontsize=7.5, fontproperties=simsun_font)
plt.ylabel('订单量/千个', fontsize=7.5, fontproperties=simsun_font)

# 设置X轴刻度和范围
plt.xticks(range(0, 24), [f"{h}:00" for h in range(0, 24)], rotation=45)
plt.gca().tick_params(axis='x', labelsize=7.5)
for label in plt.gca().get_xticklabels():
    label.set_fontproperties(roman_font)
    label.set_fontsize(7.5)
plt.xlim(-0.5, 23.5)  # 限制X轴范围，减少空白，使柱子与边缘对齐





# 调整纵坐标范围和刻度间隔 - 转换为千个单位
plt.ylim(0, 60)
plt.yticks(range(0, 61, 10))
plt.gca().tick_params(axis='y', labelsize=7.5)
for label in plt.gca().get_yticklabels():
    label.set_fontproperties(roman_font)
    label.set_fontsize(7.5)  # 设置Y轴刻度间隔为10千个，字体大小为6号

# 优化布局
plt.tight_layout()

# 保存图表
chart_file = os.path.join(output_dir, '共享单车每小时订单量趋势图.png')
plt.savefig(chart_file, dpi=300, bbox_inches='tight', pad_inches=0.1)
print(f"\n图表已保存到: {chart_file}")

# 保存统计结果
stats_file = os.path.join(output_dir, '每小时订单量统计.csv')
hourly_orders.to_csv(stats_file, index=False, encoding='utf-8')
print(f"统计结果已保存到: {stats_file}")

# 显示图表
plt.show()

print("\n分析完成！")
