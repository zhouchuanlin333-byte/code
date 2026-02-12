import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.colors as mcolors

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 定义变量单位
VARIABLE_UNITS = {
    '人口密度': '千人/km²'
}

def generate_custom_distribution_data():
    """
    按照用户指定的分布规律生成人口密度SHAP数据
    """
    # 定义各区间的参数
    intervals = [
        {'range': (0, 5), 'count': 315, 'shap_range': (-0.8, -0.3)},
        {'range': (5, 10), 'count': 945, 'shap_range': (-0.2, 0.3)},
        {'range': (10, 15), 'count': 788, 'shap_range': (0.4, 0.9)},
        {'range': (15, 20), 'count': 630, 'shap_range': (1.0, 1.6)},
        {'range': (20, 25), 'count': 378, 'shap_range': (1.5, 2.1)},
        {'range': (25, 30), 'count': 94, 'shap_range': (1.4, 1.9)}
    ]
    
    all_data = []
    
    for interval in intervals:
        min_val, max_val = interval['range']
        count = interval['count']
        shap_min, shap_max = interval['shap_range']
        
        # 在该区间内生成均匀分布的人口密度值
        population_density = np.random.uniform(min_val, max_val, count)
        
        # 在指定SHAP范围内生成均匀分布的SHAP值
        shap_values = np.random.uniform(shap_min, shap_max, count)
        
        # 添加一些随机噪声使数据更真实
        population_density += np.random.normal(0, 0.1, count)
        shap_values += np.random.normal(0, 0.05, count)
        
        # 确保数据在合理范围内
        population_density = np.clip(population_density, min_val, max_val)
        shap_values = np.clip(shap_values, shap_min, shap_max)
        
        for pop, shap in zip(population_density, shap_values):
            all_data.append({
                '人口密度': pop,
                'SHAP值': shap
            })
    
    return pd.DataFrame(all_data)

def plot_custom_population_density_shap_scatter(df, save_path=None):
    """
    绘制按用户指定分布生成的人口密度SHAP散点图
    """
    plt.figure(figsize=(12, 8))
    
    # 创建颜色映射
    scatter = plt.scatter(
        df['人口密度'], 
        df['SHAP值'], 
        c=df['人口密度'], 
        cmap='viridis', 
        alpha=0.7, 
        s=30,
        edgecolors='black', 
        linewidth=0.5
    )
    
    # 设置标题和标签
    plt.title('人口密度 SHAP值分布散点图\n(按指定分布规律生成)', fontsize=16, pad=20)
    plt.xlabel(f'人口密度 ({VARIABLE_UNITS["人口密度"]})', fontsize=14)
    plt.ylabel('SHAP值', fontsize=14)
    
    # 设置x轴范围
    plt.xlim(-1, 31)
    
    # 添加零线
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=2)
    
    # 添加网格线
    plt.grid(True, alpha=0.3)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter)
    cbar.set_label(f'人口密度 ({VARIABLE_UNITS["人口密度"]})', fontsize=12)
    
    # 设置刻度
    plt.xticks(np.arange(0, 31, 5))
    
    # 在x=5, 10, 15, 20, 25, 30处添加垂直虚线
    for x in [5, 10, 15, 20, 25, 30]:
        plt.axvline(x=x, color='gray', linestyle='--', alpha=0.3)
    
    # 添加区间标签
    interval_labels = ['0~5', '5~10', '10~15', '15~20', '20~25', '25~30']
    interval_positions = [2.5, 7.5, 12.5, 17.5, 22.5, 27.5]
    
    for i, (label, pos) in enumerate(zip(interval_labels, interval_positions)):
        plt.text(pos, plt.ylim()[1] * 0.95, label, 
                ha='center', va='top', fontsize=10, 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"散点图已保存至: {save_path}")
    
    plt.show()

def print_distribution_summary(df):
    """
    打印数据分布摘要
    """
    print("=" * 60)
    print("人口密度SHAP数据分布摘要")
    print("=" * 60)
    
    # 定义区间
    intervals = [
        (0, 5, '0~5'),
        (5, 10, '5~10'),
        (10, 15, '10~15'),
        (15, 20, '15~20'),
        (20, 25, '20~25'),
        (25, 30, '25~30')
    ]
    
    total_samples = len(df)
    
    print(f"总样本数: {total_samples}")
    print(f"人口密度范围: [{df['人口密度'].min():.3f}, {df['人口密度'].max():.3f}] {VARIABLE_UNITS['人口密度']}")
    print(f"SHAP值范围: [{df['SHAP值'].min():.4f}, {df['SHAP值'].max():.4f}]")
    print(f"SHAP值均值: {df['SHAP值'].mean():.4f}")
    print()
    
    print("各区间分布:")
    print("-" * 60)
    print(f"{'区间':<10} {'样本数':<10} {'占比':<10} {'SHAP范围':<20}")
    print("-" * 60)
    
    for min_val, max_val, label in intervals:
        mask = (df['人口密度'] >= min_val) & (df['人口密度'] < max_val)
        count = mask.sum()
        percentage = (count / total_samples) * 100
        
        if count > 0:
            shap_min = df.loc[mask, 'SHAP值'].min()
            shap_max = df.loc[mask, 'SHAP值'].max()
            shap_range = f"[{shap_min:.2f}, {shap_max:.2f}]"
        else:
            shap_range = "N/A"
        
        print(f"{label:<10} {count:<10} {percentage:<10.1f}% {shap_range:<20}")
    
    print("-" * 60)

def main():
    """
    主函数：生成按用户指定分布的人口密度SHAP散点图
    """
    print("开始生成按指定分布的人口密度SHAP散点图...")
    
    # 生成符合用户要求分布的数据
    df = generate_custom_distribution_data()
    
    # 打印分布摘要
    print_distribution_summary(df)
    
    # 绘制散点图
    output_path = r"D:\Desktop\项目论文\shap可视化\SHAP分布散点图\早高峰_人口密度_SHAP分布散点图_自定义分布.png"
    plot_custom_population_density_shap_scatter(df, save_path=output_path)
    
    print("散点图生成完成！")
    print(f"图片已保存至: {output_path}")

if __name__ == "__main__":
    main()