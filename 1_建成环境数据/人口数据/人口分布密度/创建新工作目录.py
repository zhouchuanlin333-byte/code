import os
import shutil

# 基础路径设置
base_dir = r"D:\Desktop\项目论文\人口数据\人口分布密度"
new_dir = os.path.join(base_dir, "global_landsat_processing")

print("开始创建新的工作目录结构...")
print(f"基础目录: {base_dir}")
print(f"新工作目录: {new_dir}")

try:
    # 如果新目录已存在，先删除
    if os.path.exists(new_dir):
        print(f"注意: 目录 {new_dir} 已存在，将重新创建")
        shutil.rmtree(new_dir)
    
    # 创建新的目录结构
    # 1. 创建主工作目录
    os.makedirs(new_dir, exist_ok=True)
    print(f"已创建主工作目录: {new_dir}")
    
    # 2. 创建子目录
    subdirs = [
        "tmp",       # 临时文件
        "results",   # 结果文件
        "figures",   # 可视化图表
        "scripts"    # 脚本文件
    ]
    
    for subdir in subdirs:
        dir_path = os.path.join(new_dir, subdir)
        os.makedirs(dir_path, exist_ok=True)
        print(f"已创建子目录: {dir_path}")
    
    # 创建链接到原有results和figures目录的软链接（如果支持）
    # 这样可以保持输出路径在原来的位置
    try:
        # 创建到原有results目录的软链接
        original_results = os.path.join(base_dir, "results")
        link_results = os.path.join(new_dir, "linked_results")
        
        if os.path.exists(original_results):
            if not os.path.exists(link_results):
                # 在Windows上创建软链接
                os.system(f"mklink /d \"{link_results}\" \"{original_results}\"")
                print(f"已创建到原有results目录的链接: {link_results}")
        
        # 创建到原有figures目录的软链接
        original_figures = os.path.join(base_dir, "figures")
        link_figures = os.path.join(new_dir, "linked_figures")
        
        if os.path.exists(original_figures):
            if not os.path.exists(link_figures):
                # 在Windows上创建软链接
                os.system(f"mklink /d \"{link_figures}\" \"{original_figures}\"")
                print(f"已创建到原有figures目录的链接: {link_figures}")
    except Exception as e:
        print(f"创建软链接时出错（非关键错误）: {e}")
    
    # 打印目录结构
    print("\n创建的目录结构:")
    for root, dirs, files in os.walk(new_dir):
        level = root.replace(new_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
    
    print("\n工作目录结构创建完成！")
    print(f"新工作目录: {new_dir}")
    print(f"结果和图表将输出到: {os.path.join(base_dir, 'results')} 和 {os.path.join(base_dir, 'figures')}")
    
    # 创建一个配置文件，记录路径信息
    config_path = os.path.join(new_dir, "config.py")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("# 配置文件 - 全球人口密度数据处理\n")
        f.write("# 创建时间: " + "\n")
        f.write("\n# 路径配置\n")
        f.write(f"BASE_DIR = r\"{base_dir}\"\n")
        f.write(f"WORK_DIR = r\"{new_dir}\"\n")
        f.write(f"TMP_DIR = r\"{os.path.join(new_dir, 'tmp')}\"\n")
        f.write(f"RESULTS_DIR = r\"{os.path.join(base_dir, 'results')}\"\n")
        f.write(f"FIGURES_DIR = r\"{os.path.join(base_dir, 'figures')}\"\n")
        f.write("\n# 输入数据路径\n")
        f.write(f"GLOBAL_LANDSCAN_PATH = r\"D:\\Desktop\\项目论文\\人口数据\\人口栅格分布数据\\landscan-global-2024.tif\"\n")
        f.write(f"XIAN_BOUNDARY_PATH = r\"D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\西安市六大主城区.shp\"\n")
        f.write(f"FISHNET_PATH = r\"D:\\Desktop\\项目论文\\西安市渔网\\西安市500米渔网\\带编号完整渔网网格.shp\"\n")
        f.write("\n# 坐标系配置\n")
        f.write("TARGET_CRS = 'EPSG:4547'\n")
    
    print(f"\n已创建配置文件: {config_path}")
    
except Exception as e:
    print(f"创建目录结构时出错: {e}")
    import traceback
    traceback.print_exc()
