import pandas as pd
import os

# 定义文件路径
early_peak_file = 'd:/Desktop/项目论文/网格轨迹段汇总/碳排放计算与可视化/早高峰_carbon_emission.csv'
evening_peak_file = 'd:/Desktop/项目论文/网格轨迹段汇总/碳排放计算与可视化/晚高峰_carbon_emission.csv'

def update_carbon_emission(file_path):
    """将指定文件中的carbon_emission_kg列乘以1.3并覆盖原文件"""
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)
        
        # 检查列是否存在
        if 'carbon_emission_kg' not in df.columns:
            print(f"错误：文件 {file_path} 中不存在 'carbon_emission_kg' 列")
            return False
        
        # 将carbon_emission_kg列乘以1.3
        df['carbon_emission_kg'] = df['carbon_emission_kg'] * 1.3
        
        # 保存回原文件，覆盖旧数据
        df.to_csv(file_path, index=False)
        
        print(f"成功更新文件：{file_path}")
        print(f"更新了 {len(df)} 行数据")
        return True
    except Exception as e:
        print(f"处理文件 {file_path} 时出错：{e}")
        return False

# 更新早高峰数据
print("正在更新早高峰碳排放数据...")
update_carbon_emission(early_peak_file)

# 更新晚高峰数据
print("\n正在更新晚高峰碳排放数据...")
update_carbon_emission(evening_peak_file)

print("\n所有文件更新完成！")