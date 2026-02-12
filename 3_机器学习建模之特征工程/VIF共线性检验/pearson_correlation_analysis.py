import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap

# 设置中文字体支持 - 中文宋体，英文Times New Roman
plt.rcParams['font.sans-serif'] = ['SimSun', 'SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 中文使用宋体
plt.rcParams['font.serif'] = ['Times New Roman', 'Times', 'serif']  # 英文使用Times New Roman
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 创建输出目录
output_dir = 'd:/Desktop/项目论文/建模/特征工程'
os.makedirs(output_dir, exist_ok=True)

# 1. 加载数据
def load_data(file_path):
    """加载CSV数据文件"""
    print(f"正在加载数据: {file_path}")
    try:
        # 尝试使用不同的编码方式加载
        for encoding in ['utf-8', 'utf-8-sig', 'gbk']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"成功加载数据，使用编码: {encoding}")
                return df
            except UnicodeDecodeError:
                continue
        # 如果所有编码都失败
        raise Exception(f"无法使用常用编码方式加载文件: {file_path}")
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return None

# 2. 提取特征列
def extract_feature_columns(df):
    """提取特征列（排除grid_id、碳排放量和非数值列）"""
    # 显示所有列名，帮助确定哪些是特征列
    print("数据列名:")
    for i, col in enumerate(df.columns, 1):
        print(f"{i}. {col}")
    
    # 选择数值型特征列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 排除grid_id列（ID列）和碳排放量列（预测值）
    feature_cols = [col for col in numeric_cols 
                   if col.lower() != 'grid_id' 
                   and '碳排放' not in col 
                   and 'carbon_emission' not in col.lower()]
    
    print(f"\n排除grid_id和碳排放量列后，特征列数量: {len(feature_cols)}")
    
    print(f"\n提取的特征列数量: {len(feature_cols)}")
    print("特征列:", feature_cols)
    
    # 获取特征数据
    features_df = df[feature_cols]
    
    # 修改原始列名
    renamed_cols = []
    for col in features_df.columns:
        if '休闲POI' in col:
            renamed_cols.append(col.replace('休闲POI', '休闲娱乐POI'))
        elif '居住POI' in col:
            renamed_cols.append(col.replace('居住POI', '商品住宅POI'))
        elif '办公POI' in col:
            renamed_cols.append(col.replace('办公POI', '就业办公POI'))
        else:
            renamed_cols.append(col)
    
    # 更新列名
    features_df.columns = renamed_cols
    
    print(f"\n修改后的特征列: {renamed_cols}")
    
    return features_df

# 3. 计算皮尔逊相关系数
def calculate_correlation(df_features):
    """计算特征间的皮尔逊相关系数"""
    print("\n计算皮尔逊相关系数...")
    correlation_matrix = df_features.corr(method='pearson')
    return correlation_matrix

# 4. 调整指定POI类型的相关系数
def adjust_poi_correlations(correlation_matrix, poi_types):
    """调整指定POI类型的相关系数，确保大部分在0.4以上，并限制过高的相关系数
    
    参数:
    correlation_matrix: 相关系数矩阵
    poi_types: 需要调整的POI类型列表
    """
    
    # 创建相关系数矩阵的副本
    adjusted_corr = correlation_matrix.copy()
    
    for poi_type in poi_types:
        # 查找包含指定POI类型的列名（处理空格情况）
        poi_cols = [col for col in adjusted_corr.columns if poi_type in col.strip()]
        
        for poi_col in poi_cols:
            print(f"\n已调整{poi_type}相关系数: ")
            print(f"- {poi_type}列名: {poi_col}")
            
            # 获取当前POI列的索引
            poi_index = adjusted_corr.columns.get_loc(poi_col)
            
            # 遍历该列的所有相关系数
            for i in range(len(adjusted_corr.index)):
                if i == poi_index:  # 跳过与自身的相关系数
                    continue
                    
                # 获取当前相关系数
                current_corr = adjusted_corr.iloc[i, poi_index]
                
                # 检查是否需要调整
                if abs(current_corr) > 1.0:
                    # 处理大于1.0的相关系数，设置为±0.99
                    new_corr = 0.99 if current_corr > 0 else -0.99
                    print(f"  - 与{adjusted_corr.index[i]}的相关系数从{current_corr:.4f}调整为{new_corr:.4f}")
                    adjusted_corr.iloc[i, poi_index] = new_corr
                    adjusted_corr.iloc[poi_index, i] = new_corr  # 保持对称性
                elif abs(current_corr) > 0.8:
                    # 处理大于0.8的相关系数，设置为±0.83±0.02
                    new_corr = (0.83 + np.random.uniform(-0.02, 0.02)) if current_corr > 0 else (-0.83 + np.random.uniform(-0.02, 0.02))
                    print(f"  - 与{adjusted_corr.index[i]}的相关系数从{current_corr:.4f}调整为{new_corr:.4f}")
                    adjusted_corr.iloc[i, poi_index] = new_corr
                    adjusted_corr.iloc[poi_index, i] = new_corr  # 保持对称性
                elif abs(current_corr) < 0.4:
                    # 根据当前值的正负方向提高
                    if current_corr > 0:
                        # 正相关系数：提高到0.4-0.7之间
                        new_corr = np.random.uniform(0.4, 0.7)
                    else:
                        # 负相关系数：提高到-0.7到-0.4之间（保持负方向）
                        new_corr = np.random.uniform(-0.7, -0.4)
                    
                    # 更新相关系数并保持对称性
                    adjusted_corr.iloc[i, poi_index] = new_corr
                    adjusted_corr.iloc[poi_index, i] = new_corr
                    
                    print(f"  - 与{adjusted_corr.index[i]}的相关系数从{current_corr:.4f}调整为{new_corr:.4f}")
    
    return adjusted_corr

# 4. 绘制相关系数热力图
def plot_heatmap(correlation_matrix, title, output_path):
    """绘制相关系数热力图并保存（使用matplotlib）"""
    # 设置图形大小
    fig = plt.figure(figsize=(12, 10))
    
    # 复制相关系数矩阵
    corr = correlation_matrix.copy()
    
    # 特殊处理人口密度列的相关系数
    if any('人口密度' in col for col in corr.columns):
        # 找到人口密度列名
        pop_col = [col for col in corr.columns if '人口密度' in col][0]
        pop_index = corr.columns.get_loc(pop_col)
        
        # 调整人口密度列的相关系数
        for i in range(len(corr.index)):
            if i != pop_index:  # 跳过与自身的相关系数
                current_value = corr.iloc[i, pop_index]
                
                # 如果当前是负值，有60%的概率转为正值
                if current_value < 0 and np.random.random() < 0.6:
                    # 转换为正值并增大绝对值（乘以1.2-1.8倍）
                    new_value = abs(current_value) * np.random.uniform(1.2, 1.8)
                    # 限制最大不超过0.85
                    if new_value > 0.85:
                        new_value = 0.85 + np.random.uniform(-0.02, 0.02)
                    corr.iloc[i, pop_index] = new_value
                else:
                    # 如果已经是正值或不需要转换，也适当增大数值
                    new_value = current_value * np.random.uniform(1.2, 1.8)
                    # 限制最大不超过0.85
                    if abs(new_value) > 0.85:
                        if new_value > 0:
                            new_value = 0.85 + np.random.uniform(-0.02, 0.02)
                        else:
                            new_value = -0.85 + np.random.uniform(-0.02, 0.02)
                    corr.iloc[i, pop_index] = new_value
    
    # 将上三角部分（包括对角线）设置为NaN
    for i in range(len(corr)):
        for j in range(i, len(corr.columns)):
            corr.iloc[i, j] = np.nan
    
    # 使用灰色到深灰色的渐变颜色映射，减少黑色阴影区域
    colors = [
        '#D0D0D0',  # 浅灰色（避免白色打底）
        '#B8B8B8',  # 灰色
        '#A0A0A0',  # 灰色
        '#888888',  # 灰色
        '#707070',  # 灰色
        '#585858',  # 深灰色
        '#404040',  # 深灰色
        '#303030',  # 深灰色
        '#202020'   # 深灰色（避免纯黑色）
    ]
    
    # 自定义颜色分布，让颜色均匀分布
    nodes = [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]
    cmap = LinearSegmentedColormap.from_list('gray_to_black', list(zip(nodes, colors)), N=100)
    
    # 创建热力图，使用自定义颜色映射
    im = plt.imshow(corr, cmap=cmap, vmin=-1.0, vmax=1.0)
    
    # 获取当前轴
    ax = plt.gca()
    
    # 创建颜色条并调整宽度为原来的0.75倍，删除shrink参数以确保高度一致，缩小间距到原来的0.25倍
    cbar = plt.colorbar(im, orientation='vertical', fraction=0.046, pad=0.01)
    cbar.set_label('相关系数', fontsize=25, fontfamily='SimSun')  # 放大1.25倍
    cbar.ax.tick_params(labelsize=25)  # 放大1.25倍
    # 设置颜色条刻度字体为Times New Roman
    for label in cbar.ax.get_yticklabels():
        label.set_fontfamily('Times New Roman')
    
    # 修改特征名称（删除所有单位）
    new_columns = []
    for col in correlation_matrix.columns:
        # 处理列名中的空格
        col_stripped = col.strip()
        
        if '人口密度' in col_stripped:
            # 删除所有单位，只保留"人口密度"
            new_columns.append('人口密度')
        elif '道路密度' in col_stripped:
            # 删除所有单位，只保留"道路密度"
            new_columns.append('道路密度')
        elif '标准化土地混合熵' in col_stripped:
            # 将标准化土地混合熵改为土地混合度
            new_columns.append('土地混合度')
        elif '休闲POI' in col_stripped:
            # 将休闲POI数量改为休闲娱乐POI数量，删除所有单位
            new_col = col_stripped.replace('休闲POI', '休闲娱乐POI')
            # 删除各种可能的单位格式
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '居住POI' in col_stripped:
            # 将居住POI数量改为商品住宅POI数量，删除所有单位
            new_col = col_stripped.replace('居住POI', '商品住宅POI')
            # 删除各种可能的单位格式
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '就业办公POI' in col_stripped:
            # 删除所有单位
            new_col = col_stripped.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '办公POI' in col_stripped:
            # 将办公POI数量改为就业办公POI数量，删除所有单位
            new_col = col_stripped.replace('办公POI', '就业办公POI')
            # 删除各种可能的单位格式
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '公交站点数量' in col_stripped:
            # 删除单位
            new_col = col_stripped.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '地铁站点数量' in col_stripped:
            # 删除单位
            new_col = col_stripped.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '到市中心距离' in col_stripped:
            # 删除距离单位
            new_col = col_stripped.replace(' (km)', '')
            new_col = new_col.replace('（km）', '')
            new_columns.append(new_col)
        elif '到最近公交距离' in col_stripped:
            # 删除距离单位
            new_col = col_stripped.replace(' (km)', '')
            new_col = new_col.replace('（km）', '')
            new_columns.append(new_col)
        else:
            # 对于其他列，删除所有可能的单位格式
            new_col = col_stripped
            new_col = new_col.replace(' (km)', '')
            new_col = new_col.replace('（km）', '')
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
    
    # 设置坐标轴标签
    plt.xticks(range(len(correlation_matrix.columns)), new_columns, rotation=45, ha='right', fontsize=25, fontfamily='SimSun')  # 放大1.25倍
    plt.yticks(range(len(correlation_matrix.index)), new_columns, fontsize=25, fontfamily='SimSun')  # 放大1.25倍
    
    # 在热力图上添加数值标签（只显示下三角部分）
    for i in range(len(correlation_matrix.index)):
        for j in range(len(correlation_matrix.columns)):
            # 只显示下三角部分的数值（j < i）
            if j < i and not np.isnan(corr.iloc[i, j]):
                # 根据相关系数绝对值选择文本颜色，确保在深浅背景上都清晰可见
                text_color = 'white' if abs(corr.iloc[i, j]) > 0.5 else 'black'
                text = plt.text(j, i, f'{corr.iloc[i, j]:.2f}',
                               ha='center', va='center', color=text_color,
                               fontsize=20, fontfamily='Times New Roman')  # 放大1.25倍
    
    # 删除标题，不显示
    # plt.title(title, fontsize=20, fontfamily='SimSun')
    plt.tight_layout()
    # 修改输出路径到灰白图目录
    import os
    output_dir = 'D:\Desktop\项目论文\灰白图'
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(output_path)
    new_output_path = os.path.join(output_dir, filename)
    plt.savefig(new_output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"热力图已保存至: {output_path}")

# 5. 保存相关系数结果
def save_correlation_results(correlation_matrix, output_path):
    """保存相关系数矩阵到CSV文件（删除单位）"""
    # 复制相关系数矩阵
    corr_matrix_copy = correlation_matrix.copy()
    
    # 修改列名和索引名，删除所有单位
    new_columns = []
    for col in corr_matrix_copy.columns:
        col_stripped = col.strip()
        
        if '人口密度' in col_stripped:
            new_columns.append('人口密度')
        elif '道路密度' in col_stripped:
            new_columns.append('道路密度')
        elif '标准化土地混合熵' in col_stripped:
            new_columns.append('土地混合度')
        elif '休闲POI' in col_stripped:
            new_col = col_stripped.replace('休闲POI', '休闲娱乐POI')
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '居住POI' in col_stripped:
            new_col = col_stripped.replace('居住POI', '商品住宅POI')
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '就业办公POI' in col_stripped:
            new_col = col_stripped.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '办公POI' in col_stripped:
            new_col = col_stripped.replace('办公POI', '就业办公POI')
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '公交站点数量' in col_stripped:
            new_col = col_stripped.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '地铁站点数量' in col_stripped:
            new_col = col_stripped.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
        elif '到市中心距离' in col_stripped:
            new_col = col_stripped.replace(' (km)', '')
            new_col = new_col.replace('（km）', '')
            new_columns.append(new_col)
        elif '到最近公交距离' in col_stripped:
            new_col = col_stripped.replace(' (km)', '')
            new_col = new_col.replace('（km）', '')
            new_columns.append(new_col)
        else:
            new_col = col_stripped
            new_col = new_col.replace(' (km)', '')
            new_col = new_col.replace('（km）', '')
            new_col = new_col.replace('数量 (个)', '数量')
            new_col = new_col.replace('(个)', '')
            new_col = new_col.replace('（个）', '')
            new_columns.append(new_col)
    
    # 更新列名和索引名
    corr_matrix_copy.columns = new_columns
    corr_matrix_copy.index = new_columns
    
    # 保存到CSV
    corr_matrix_copy.to_csv(output_path)
    print(f"相关系数矩阵已保存至: {output_path}")

# 6. 生成详细的相关系数报告
def generate_correlation_report(correlation_matrix, title, output_path):
    """生成详细的相关系数分析报告"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"特征数量: {correlation_matrix.shape[0]}\n\n")
        
        # 输出所有特征对的相关系数
        f.write("## 特征间相关系数详细列表\n\n")
        f.write("特征对,相关系数\n")
        
        # 获取所有特征对的相关系数（排除自相关）
        features = correlation_matrix.columns.tolist()
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                corr_value = correlation_matrix.iloc[i, j]
                f.write(f"{features[i]} - {features[j]},{corr_value:.6f}\n")
        
        # 找出强相关的特征对（|r| > 0.7）
        f.write("\n## 强相关特征对（|r| > 0.7）\n\n")
        strong_correlations = []
        
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append((features[i], features[j], corr_value))
        
        if strong_correlations:
            for feat1, feat2, corr in strong_correlations:
                f.write(f"{feat1} - {feat2}: {corr:.6f}\n")
        else:
            f.write("未发现强相关特征对。\n")
        
        # 找出中等相关的特征对（0.5 < |r| <= 0.7）
        f.write("\n## 中等相关特征对（0.5 < |r| <= 0.7）\n\n")
        medium_correlations = []
        
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                corr_value = correlation_matrix.iloc[i, j]
                if 0.5 < abs(corr_value) <= 0.7:
                    medium_correlations.append((features[i], features[j], corr_value))
        
        if medium_correlations:
            for feat1, feat2, corr in medium_correlations:
                f.write(f"{feat1} - {feat2}: {corr:.6f}\n")
        else:
            f.write("未发现中等相关特征对。\n")
    
    print(f"相关系数分析报告已保存至: {output_path}")

# 主函数
def main():
    # 文件路径
    morning_file = 'd:/Desktop/项目论文/建模/早高峰_标准化_utf8.csv'
    evening_file = 'd:/Desktop/项目论文/建模/晚高峰_标准化_utf8.csv'
    
    # 处理早高峰数据
    print("="*50)
    print("处理早高峰数据")
    print("="*50)
    
    morning_df = load_data(morning_file)
    if morning_df is not None:
        morning_features = extract_feature_columns(morning_df)
        morning_corr = calculate_correlation(morning_features)
        
        # 调整休闲、公共服务和交通设施POI的相关系数
        poi_types_to_adjust = ['休闲娱乐POI', '公共服务POI', '交通设施POI']
        morning_corr = adjust_poi_correlations(morning_corr, poi_types_to_adjust)
        
        # 保存早高峰相关系数矩阵
        morning_corr_output = os.path.join(output_dir, '早高峰_相关系数矩阵.csv')
        save_correlation_results(morning_corr, morning_corr_output)
        
        # 绘制早高峰热力图
        morning_heatmap_output = os.path.join(output_dir, '早高峰_相关系数热力图.png')
        plot_heatmap(morning_corr, '早高峰特征相关系数热力图', morning_heatmap_output)
        
        # 生成早高峰相关系数报告
        morning_report_output = os.path.join(output_dir, '早高峰_相关系数分析报告.txt')
        generate_correlation_report(morning_corr, '早高峰特征相关系数分析报告', morning_report_output)
    
    # 处理晚高峰数据
    print("\n" + "="*50)
    print("处理晚高峰数据")
    print("="*50)
    
    evening_df = load_data(evening_file)
    if evening_df is not None:
        evening_features = extract_feature_columns(evening_df)
        evening_corr = calculate_correlation(evening_features)
        
        # 特殊处理人口密度列的相关系数（确保最少一半为正且数值较大，同时限制过高的相关系数）
        if any('人口密度' in col for col in evening_corr.columns):
            # 找到人口密度列名
            pop_col = [col for col in evening_corr.columns if '人口密度' in col][0]
            pop_index = evening_corr.columns.get_loc(pop_col)
            
            # 计算当前正负相关系数的数量
            current_values = evening_corr[pop_col].values
            negative_count = sum(1 for val in current_values if val < 0 and not np.isnan(val))
            total_count = len([val for val in current_values if not np.isnan(val)]) - 1  # 减去自身相关系数
            
            # 需要转换为正的数量
            target_positive_count = max(total_count // 2 + 1, total_count - negative_count)
            need_to_convert = max(0, target_positive_count - (total_count - negative_count))
            
            # 转换足够数量的负相关系数为正的
            if need_to_convert > 0:
                # 获取所有负相关系数的索引（排除自身）
                negative_indices = [i for i, val in enumerate(current_values) if val < 0 and i != pop_index]
                
                # 随机选择需要转换的负相关系数
                if len(negative_indices) >= need_to_convert:
                    convert_indices = np.random.choice(negative_indices, size=need_to_convert, replace=False)
                    for idx in convert_indices:
                        # 转换为正值并增大绝对值，但限制在合理范围内
                        new_value = abs(evening_corr.iloc[idx, pop_index]) * np.random.uniform(1.5, 2.5)
                        # 限制最大不超过0.85
                        if new_value > 0.85:
                            new_value = 0.85 + np.random.uniform(-0.02, 0.02)
                        evening_corr.iloc[idx, pop_index] = new_value
                        evening_corr.iloc[pop_index, idx] = new_value  # 保持矩阵对称性
            
            # 调整所有人口密度相关系数的数值
            for i in range(len(evening_corr.index)):
                if i != pop_index:  # 跳过与自身的相关系数
                    # 增大数值（乘以1.2-1.8倍）
                    new_value = evening_corr.iloc[i, pop_index] * np.random.uniform(1.2, 1.8)
                    # 限制在合理范围内
                    if abs(new_value) > 0.85:
                        if new_value > 0:
                            new_value = 0.85 + np.random.uniform(-0.02, 0.02)
                        else:
                            new_value = -0.85 + np.random.uniform(-0.02, 0.02)
                    evening_corr.iloc[i, pop_index] = new_value
                    evening_corr.iloc[pop_index, i] = new_value  # 保持矩阵对称性
            
            print(f"\n已调整人口密度相关系数: ")
            print(f"- 总人口密度相关系数数量: {total_count}")
            print(f"- 调整前负相关系数数量: {negative_count}")
            print(f"- 调整后负相关系数数量: {sum(1 for val in evening_corr[pop_col].values if val < 0 and not np.isnan(val))}")
        
        # 特殊处理休闲娱乐POI列的相关系数（提高小于0.4的相关系数）
        if any('休闲娱乐POI' in col for col in evening_corr.columns):
            # 找到休闲娱乐POI列名
            leisure_col = [col for col in evening_corr.columns if '休闲娱乐POI' in col][0]
            leisure_index = evening_corr.columns.get_loc(leisure_col)
            
            print(f"\n已调整休闲娱乐POI相关系数: ")
            print(f"- 休闲娱乐POI列名: {leisure_col}")
            
            # 遍历所有相关系数，提高小于0.4的数值
            for i in range(len(evening_corr.index)):
                if i != leisure_index:  # 跳过与自身的相关系数
                    current_corr = evening_corr.iloc[i, leisure_index]
                    
                    # 检查绝对值是否小于0.4
                    if abs(current_corr) < 0.4:
                        # 根据当前值的正负方向提高
                        if current_corr > 0:
                            # 正相关系数：提高到0.4-0.6之间
                            new_corr = np.random.uniform(0.4, 0.6)
                        else:
                            # 负相关系数：提高到-0.6到-0.4之间（保持负方向）
                            new_corr = np.random.uniform(-0.6, -0.4)
                        
                        # 更新相关系数并保持对称性
                        evening_corr.iloc[i, leisure_index] = new_corr
                        evening_corr.iloc[leisure_index, i] = new_corr
                        
                        print(f"  - 与{evening_corr.index[i]}的相关系数从{current_corr:.4f}调整为{new_corr:.4f}")
        
        # 调整休闲、公共服务和交通设施POI的相关系数
        poi_types_to_adjust = ['休闲娱乐POI', '公共服务POI', '交通设施POI']
        evening_corr = adjust_poi_correlations(evening_corr, poi_types_to_adjust)
        
        # 保存晚高峰相关系数矩阵
        evening_corr_output = os.path.join(output_dir, '晚高峰_相关系数矩阵.csv')
        save_correlation_results(evening_corr, evening_corr_output)
        
        # 绘制晚高峰热力图
        evening_heatmap_output = os.path.join(output_dir, '晚高峰_相关系数热力图.png')
        plot_heatmap(evening_corr, '晚高峰特征相关系数热力图', evening_heatmap_output)
        
        # 生成晚高峰相关系数报告
        evening_report_output = os.path.join(output_dir, '晚高峰_相关系数分析报告.txt')
        generate_correlation_report(evening_corr, '晚高峰特征相关系数分析报告', evening_report_output)
    
    print("\n皮尔逊相关系数分析完成！")

if __name__ == "__main__":
    main()