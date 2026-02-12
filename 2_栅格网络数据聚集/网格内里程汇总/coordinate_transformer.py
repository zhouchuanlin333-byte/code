#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
坐标系转换工具
用于处理不同坐标系之间的转换
"""

import pyproj
import numpy as np
from shapely.ops import transform
from shapely.geometry import Point, LineString

class CoordinateTransformer:
    """坐标系转换器"""
    
    def __init__(self):
        """初始化转换器"""
        # 定义常用坐标系
        self.wgs84 = pyproj.CRS("EPSG:4326")  # WGS84经纬度坐标系
        
    def get_transformer(self, source_crs, target_crs):
        """
        获取坐标转换器
        
        Args:
            source_crs: 源坐标系
            target_crs: 目标坐标系
            
        Returns:
            pyproj.Transformer: 坐标转换器
        """
        return pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)
    
    def transform_point(self, transformer, point):
        """
        转换单个点的坐标
        
        Args:
            transformer: 坐标转换器
            point: shapely.Point对象
            
        Returns:
            shapely.Point: 转换后的点
        """
        return Point(transformer.transform(point.x, point.y))
    
    def transform_coordinates(self, transformer, lon, lat):
        """
        转换坐标对
        
        Args:
            transformer: 坐标转换器
            lon: 经度
            lat: 纬度
            
        Returns:
            tuple: (转换后的x, 转换后的y)
        """
        return transformer.transform(lon, lat)
    
    def batch_transform_coordinates(self, transformer, lons, lats):
        """
        批量转换坐标对
        
        Args:
            transformer: 坐标转换器
            lons: 经度列表
            lats: 纬度列表
            
        Returns:
            tuple: (转换后的x列表, 转换后的y列表)
        """
        xs, ys = [], []
        for lon, lat in zip(lons, lats):
            x, y = self.transform_coordinates(transformer, lon, lat)
            xs.append(x)
            ys.append(y)
        return xs, ys
    
    def create_transformed_points_gdf(self, df, lon_col, lat_col, crs):
        """
        从DataFrame创建转换后的点GeoDataFrame
        
        Args:
            df: 包含经纬度的DataFrame
            lon_col: 经度列名
            lat_col: 纬度列名
            crs: 目标坐标系
            
        Returns:
            geopandas.GeoDataFrame: 转换后的GeoDataFrame
        """
        import geopandas as gpd
        
        # 创建点几何
        points = [Point(lon, lat) for lon, lat in zip(df[lon_col], df[lat_col])]
        
        # 创建GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=points, crs=self.wgs84)
        
        # 转换坐标系
        gdf = gdf.to_crs(crs)
        
        return gdf
    
    def transform_line(self, transformer, line):
        """
        转换线段坐标
        
        Args:
            transformer: 坐标转换器
            line: shapely.LineString对象
            
        Returns:
            shapely.LineString: 转换后的线段
        """
        # 转换线段的每个端点
        transformed_coords = [
            (transformer.transform(x, y)) 
            for x, y in line.coords
        ]
        return LineString(transformed_coords)
    
    def check_coordinate_range_match(self, coords1, coords2, tolerance=1000):
        """
        检查两组坐标范围是否匹配
        
        Args:
            coords1: 第一组坐标 [(x1, y1), (x2, y2), ...]
            coords2: 第二组坐标 [(x1, y1), (x2, y2), ...]
            tolerance: 容差（米）
            
        Returns:
            bool: 是否匹配
        """
        # 提取坐标范围
        x1_min = min(x for x, y in coords1)
        y1_min = min(y for x, y in coords1)
        x1_max = max(x for x, y in coords1)
        y1_max = max(y for x, y in coords1)
        
        x2_min = min(x for x, y in coords2)
        y2_min = min(y for x, y in coords2)
        x2_max = max(x for x, y in coords2)
        y2_max = max(y for x, y in coords2)
        
        # 检查范围是否重叠或接近
        x_overlap = not (x1_max < x2_min - tolerance or x2_max < x1_min - tolerance)
        y_overlap = not (y1_max < y2_min - tolerance or y2_max < y1_min - tolerance)
        
        return x_overlap and y_overlap
    
    def get_utm_zone(self, lon, lat):
        """
        根据经纬度获取UTM投影带
        
        Args:
            lon: 经度
            lat: 纬度
            
        Returns:
            str: UTM投影带EPSG代码
        """
        # 计算UTM带号
        zone = int((lon + 180) / 6) + 1
        
        # 构建EPSG代码
        if lat >= 0:
            epsg_code = 32600 + zone  # 北半球
        else:
            epsg_code = 32700 + zone  # 南半球
        
        return f"EPSG:{epsg_code}"
    
    def estimate_china_projection(self, center_lon, center_lat):
        """
        估算中国区域的合适投影
        
        Args:
            center_lon: 中心经度
            center_lat: 中心纬度
            
        Returns:
            str: 推荐的EPSG代码
        """
        # 西安地区大约在EPSG:3857（Web墨卡托）或EPSG:4547（西安80高斯克吕格投影）
        # 这里返回常用的Web墨卡托投影
        return "EPSG:3857"

def test_coordinate_transform():
    """测试坐标转换功能"""
    print("=== 测试坐标转换功能 ===")
    
    # 创建转换器
    transformer = CoordinateTransformer()
    
    # 测试WGS84到Web墨卡托的转换
    wgs84 = pyproj.CRS("EPSG:4326")
    web_mercator = pyproj.CRS("EPSG:3857")
    
    # 获取转换器
    proj_transformer = transformer.get_transformer(wgs84, web_mercator)
    
    # 测试点转换（西安中心坐标）
    xi_an_lon, xi_an_lat = 108.94, 34.34
    x, y = transformer.transform_coordinates(proj_transformer, xi_an_lon, xi_an_lat)
    print(f"西安坐标转换: {xi_an_lon}, {xi_an_lat} -> {x:.2f}, {y:.2f}")
    
    # 测试点对象转换
    point = Point(xi_an_lon, xi_an_lat)
    transformed_point = transformer.transform_point(proj_transformer, point)
    print(f"点对象转换结果: {transformed_point}")
    
    # 测试线段转换
    line = LineString([(xi_an_lon, xi_an_lat), (xi_an_lon + 0.1, xi_an_lat + 0.1)])
    transformed_line = transformer.transform_line(proj_transformer, line)
    print(f"线段转换结果: {transformed_line}")
    
    print("坐标转换测试完成")

if __name__ == "__main__":
    test_coordinate_transform()
