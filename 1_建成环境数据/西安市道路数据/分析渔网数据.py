import geopandas as gpd
import os

# 设置渔网数据路径
fishnet_dir = "D:\Desktop\项目论文\西安市渔网\西安市500米渔网"

# 查找渔网shp文件
def find_fishnet_files(directory):
    fishnet_files = []
    for file in os.listdir(directory):
        if file.endswith(".shp"):
            fishnet_files.append(file)
    return fishnet_files

print(f"正在查找渔网数据文件...")
fishnet_files = find_fishnet_files(fishnet_dir)
print(f"找到的渔网文件: {fishnet_files}")

# 分析每个渔网文件
for fishnet_file in fishnet_files:
    file_path = os.path.join(fishnet_dir, fishnet_file)
    print(f"\n=== 分析文件: {fishnet_file} ===")
    
    try:
        # 读取shp文件
        fishnet = gpd.read_file(file_path)
        
        print(f"数据总行数: {len(fishnet)}")
        print(f"数据列数: {len(fishnet.columns)}")
        
        print(f"\n数据字段列表:")
        print(fishnet.columns.tolist())
        
        print(f"\n坐标系统信息:")
        print(f"坐标系: {fishnet.crs}")
        
        print(f"\n前5行数据预览:")
        print(fishnet.head())
        
        print(f"\n几何类型信息:")
        print(f"几何类型: {fishnet.geometry.type.unique()}")
        
        # 检查是否有网格编号字段
        print(f"\n字段详细信息:")
        for col in fishnet.columns:
            if col != fishnet.geometry.name:
                print(f"{col}: {fishnet[col].dtype}, {fishnet[col].nunique()} 个唯一值")
                # 如果字段值较少，显示几个示例
                if fishnet[col].nunique() <= 10:
                    print(f"  示例值: {fishnet[col].head(5).tolist()}")
        
        # 检查网格大小
        print(f"\n网格大小分析:")
        # 计算网格的宽度和高度
        if len(fishnet) > 0:
            # 选择第一个网格进行分析
            first_grid = fishnet.iloc[0]['geometry']
            bounds = first_grid.bounds
            width = bounds[2] - bounds[0]  # maxx - minx
            height = bounds[3] - bounds[1]  # maxy - miny
            
            print(f"第一个网格边界: {bounds}")
            print(f"网格宽度: {width:.2f} 单位")
            print(f"网格高度: {height:.2f} 单位")
            print(f"网格面积: {width * height:.2f} 平方单位")
        
    except Exception as e:
        print(f"读取文件时出错: {e}")

print(f"\n渔网数据检查完成！")
