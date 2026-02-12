import geopandas as gpd

# 设置文件路径
subway_path = "D:\Desktop\项目论文\路网交通设施数据\西安市主城区交通站点总\地铁站\11111.shp"

print("开始分析地铁站数据...")

# 读取地铁站数据
try:
    subway_gdf = gpd.read_file(subway_path)
    print(f"成功读取地铁站数据，共 {len(subway_gdf)} 个站点")
    
    print(f"\n地铁站数据字段列表：")
    for col in subway_gdf.columns:
        print(f"- {col}")
    
    print(f"\n地铁站数据的坐标参考系统：{subway_gdf.crs}")
    
    print(f"\n地铁站数据前5行：")
    print(subway_gdf.head())
    
except Exception as e:
    print(f"读取地铁站数据失败：{e}")
