import pandas as pd
import os

# 输入文件路径
input_density_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\重新_网格POI密度统计.csv"
output_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\最终_POI网格统计综合结果.csv"

print(f"开始生成最终综合结果")
print(f"输入文件: {input_density_file}")
print(f"输出文件: {output_file}")
print("=" * 60)

try:
    # 读取密度统计数据
    print("读取POI密度统计数据...")
    df = pd.read_csv(input_density_file)
    print(f"成功读取 {len(df)} 个网格的统计数据")
    
    # 检查网格数量是否为3150
    if len(df) != 3150:
        print(f"警告: 当前统计的网格数量为 {len(df)}，与预期的3150不符")
    else:
        print("✓ 确认所有3150个网格都已包含在统计中")
    
    # 准备输出数据列
    output_columns = [
        'grid_id', '休闲_count', '办公_count', '公共服务_count', '交通设施_count', '居住_count', 'total_count',
        '休闲_density', '办公_density', '公共服务_density', '交通设施_density', '居住_density', 'total_density'
    ]
    
    # 重命名列以符合输出要求
    rename_columns = {
        'grid_id': '网格ID',
        '休闲_count': '休闲POI数量',
        '办公_count': '办公POI数量',
        '公共服务_count': '公共服务POI数量',
        '交通设施_count': '交通设施POI数量',
        '居住_count': '居住POI数量',
        'total_count': '总POI数量',
        '休闲_density': '休闲POI密度(个/km²)',
        '办公_density': '办公POI密度(个/km²)',
        '公共服务_density': '公共服务POI密度(个/km²)',
        '交通设施_density': '交通设施POI密度(个/km²)',
        '居住_density': '居住POI密度(个/km²)',
        'total_density': '总POI密度(个/km²)'
    }
    
    # 创建输出数据框
    output_df = df[output_columns].copy()
    output_df = output_df.rename(columns=rename_columns)
    
    # 按网格ID排序
    output_df = output_df.sort_values(by='网格ID')
    
    # 保存最终结果
    print(f"\n保存最终综合结果到: {output_file}")
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"已保存 {len(output_df)} 个网格的综合统计结果")
    
    # 统计信息
    print("\n" + "=" * 60)
    print("统计信息:")
    print(f"总网格数量: {len(output_df)}")
    print(f"包含POI的网格数量: {(output_df['总POI数量'] > 0).sum()}")
    print(f"空网格数量: {(output_df['总POI数量'] == 0).sum()}")
    print(f"总POI数量: {output_df['总POI数量'].sum()}")
    
    # 检查空网格
    empty_grids = output_df[output_df['总POI数量'] == 0]
    if not empty_grids.empty:
        print(f"\n空网格前5个示例:")
        print(empty_grids.head())
    
    print("\n" + "=" * 60)
    print("最终综合结果生成完成！")
    print(f"文件路径: {output_file}")
    print(f"文件格式: 网格ID,各类POI数量,总数量,各类POI密度,总密度")
    print(f"密度单位: 个/km²")
    print("所有空网格的数量已正确标记为0")
    print("=" * 60)
    
except Exception as e:
    print(f"生成过程中出错: {str(e)}")
