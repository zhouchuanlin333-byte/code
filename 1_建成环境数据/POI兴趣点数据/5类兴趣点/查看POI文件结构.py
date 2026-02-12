import pandas as pd

# 定义POI文件路径
poi_file = r"D:\Desktop\项目论文\POI兴趣点数据\5类兴趣点\休闲POI_数据.csv"

print(f"查看文件: {poi_file}")
print("=" * 60)

try:
    # 读取前5行数据
    df = pd.read_csv(poi_file, nrows=5)
    
    # 输出列名和数据类型
    print("\n文件列名:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. '{col}'")
    
    print("\n数据类型:")
    print(df.dtypes)
    
    print("\n前3行数据:")
    print(df.head(3).to_string())
    
    # 检查是否有坐标相关的列
    print("\n检查坐标相关列:")
    potential_coord_cols = []
    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in ['x', 'y', 'lon', 'lat', '经度', '纬度']):
            potential_coord_cols.append(col)
    
    if potential_coord_cols:
        print(f"发现潜在坐标列: {potential_coord_cols}")
        # 显示这些列的样例数据
        print("\n坐标列样例数据:")
        print(df[potential_coord_cols].head(5))
    else:
        print("未发现明显的坐标列")
        print("\n完整列名列表:")
        for col in df.columns:
            print(f"- '{col}'")
    
    print("\n" + "=" * 60)
    print("文件结构分析完成")
    
except Exception as e:
    print(f"分析文件时出错: {str(e)}")
