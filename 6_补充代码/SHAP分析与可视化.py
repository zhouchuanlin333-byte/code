import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt
import os

# 设置字体：中文用宋体，英文数字用新罗马，大小统一为小四（12pt）
plt.rcParams['font.sans-serif'] = ['SimSun']  # 中文宋体
plt.rcParams['font.serif'] = ['Times New Roman']  # 英文新罗马
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['font.family'] = ['sans-serif', 'serif']  # 混合字体设置
plt.rcParams['font.size'] = 12  # 全局字体大小设为小四（12pt）

# 确保输出目录存在
output_dir = "d:/Desktop/项目论文/SHAP值解释性分析"
# 确保目录存在
os.makedirs(output_dir, exist_ok=True)
print(f"输出目录已创建或存在: {output_dir}")

# 创建早高峰和晚高峰子目录
early_peak_dir = os.path.join(output_dir, "早高峰")
late_peak_dir = os.path.join(output_dir, "晚高峰")
for directory in [early_peak_dir, late_peak_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

# 定义变量名和单位（原始单位）
variable_units = {
    "人口密度": "千人/km²",
    "办公POI数量": "个",
    "休闲POI数量": "个",
    "居住POI数量": "个",
    "交通设施POI数量": "个",
    "公共服务POI数量": "个",
    "道路密度": "km/km²",
    "地铁站点数量": "个",
    "公交站点数量": "个",
    "标准化土地混合熵": "无单位",
    "到市中心距离": "km",
    "到最近公交距离": "km"
}

# 读取数据
def load_data(time_of_day):
    if time_of_day == "早高峰":
        file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv"
    else:
        file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv"
    
    df = pd.read_csv(file_path)
    print(f"{time_of_day}数据加载完成，形状：{df.shape}")
    
    # 使用更安全的方式打印列名，避免编码问题
    try:
        print(f"{time_of_day}数据列名：{list(df.columns)}")
    except UnicodeEncodeError:
        print(f"{time_of_day}数据列名：")
        for col in df.columns:
            print(f"  - {col}")
    
    # 处理晚高峰数据中的额外列
    # 删除所有包含空值的列（由额外逗号导致）
    df = df.dropna(axis=1, how='all')
    
    print(f"{time_of_day}数据清理后形状：{df.shape}")
    
    # 使用更安全的方式打印清理后的列名
    try:
        print(f"{time_of_day}数据清理后列名：{list(df.columns)}")
    except UnicodeEncodeError:
        print(f"{time_of_day}数据清理后列名：")
        for col in df.columns:
            print(f"  - {col}")
    
    # 分离特征和目标变量
    X = df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 训练XGBoost模型并进行SHAP分析
def train_and_analyze(time_of_day, X_train, y_train, X_test, y_test):
    print(f"\n--- {time_of_day}数据分析 ---")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 评估模型
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"{time_of_day} XGBoost模型测试集MSE: {mse:.5f}")
    
    # 保存模型
    model.save_model(os.path.join(output_dir, f"{time_of_day}_xgb_model.json"))
    
    # 创建SHAP解释器
    explainer = shap.Explainer(model)
    shap_values = explainer(X_test)
    
    # 保存SHAP值
    np.save(os.path.join(output_dir, f"{time_of_day}_shap_values.npy"), shap_values.values)
    np.save(os.path.join(output_dir, f"{time_of_day}_X_test.npy"), X_test.values)
    
    return model, explainer, shap_values

# 绘制SHAP值可视化图
def plot_shap_visualizations(time_of_day, explainer, shap_values, X_test):
    print(f"\n--- 绘制{time_of_day} SHAP可视化图 ---")
    
    if time_of_day == "早高峰":
        save_dir = early_peak_dir
    else:
        save_dir = late_peak_dir
    
    # 调试：计算并打印特征重要性排序，与报告进行对比
    print(f"\n{time_of_day} - 调试：计算SHAP值排序")
    shap_importance = np.abs(shap_values.values).mean(axis=0)
    sorted_indices = np.argsort(shap_importance)[::-1]
    sorted_features = X_test.columns[sorted_indices]
    sorted_importance = shap_importance[sorted_indices]
    print(f"按平均绝对SHAP值排序的特征：")
    for i, (feature, importance) in enumerate(zip(sorted_features, sorted_importance)):
        print(f"{i+1}. {feature}: {importance:.6f}")
    
    # 1. SHAP摘要图（特征重要性）
    plt.figure(figsize=(12, 8))
    plt.title(f"{time_of_day} - SHAP特征重要性摘要图", fontsize=15)
    
    # 处理特征名称，去掉单位并更新指定变量名称
    feature_names_without_units = []
    for name in X_test.columns:
        # 更新变量名称
        if "办公POI数量" in name:
            feature_names_without_units.append("就业办公POI数量")
        elif "居住POI数量" in name:
            feature_names_without_units.append("商品住宅POI数量")
        elif "标准化土地混合熵" in name:
            feature_names_without_units.append("标准化土地混合度")
        # 去掉单位，只保留基础特征名
        elif "人口密度" in name:
            feature_names_without_units.append("人口密度")
        elif "道路密度" in name:
            feature_names_without_units.append("道路密度")
        elif "地铁站点数量" in name:
            feature_names_without_units.append("地铁站点数量")
        elif "公交站点数量" in name:
            feature_names_without_units.append("公交站点数量")
        elif "到市中心距离" in name:
            feature_names_without_units.append("到市中心距离")
        elif "到最近公交距离" in name:
            feature_names_without_units.append("到最近公交距离")
        elif "休闲POI数量" in name:
            feature_names_without_units.append("休闲POI数量")
        elif "交通设施POI数量" in name:
            feature_names_without_units.append("交通设施POI数量")
        elif "公共服务POI数量" in name:
            feature_names_without_units.append("公共服务POI数量")
        else:
            # 去掉可能的单位括号
            if " (" in name:
                name = name.split(" (")[0]
            feature_names_without_units.append(name)
    
    # 使用自定义特征名称并调整标签，减小图表宽度（从12变为10）
    shap.summary_plot(shap_values, X_test, feature_names=feature_names_without_units, plot_type="dot", show=False, plot_size=(10, 8))
    
    # 获取当前的轴
    ax = plt.gca()
    
    # 修改横坐标标签和范围（左边只保留到-1.0，右边保留到2.0）
    ax.set_xlabel("SHAP值（对模型输出的影响）")
    ax.set_xlim(-1.0, 2.0)
    
    # 缩小横坐标刻度间隔到原来的一半（从1.0变为0.5）
    ax.set_xticks(np.arange(-1.0, 2.01, 0.5))
    
    # 设置横坐标和纵坐标刻度字体大小为小四
    ax.tick_params(axis='both', labelsize=12)
    
    # 尝试获取颜色条
    cbar = None
    # 遍历所有轴的子对象，寻找颜色条
    for child in ax.get_children():
        if hasattr(child, 'colorbar') and child.colorbar is not None:
            cbar = child.colorbar
            break
    
    # 如果找到颜色条，修改其标签和文本
    if cbar is not None:
        cbar.set_label("特征值")
        cbar_ax = cbar.ax
        
        # 移除所有现有文本
        for text in cbar_ax.texts:
            text.remove()
        
        # 在颜色条旁边添加中文标识，字体大小为小四
        cbar_ax.text(1.2, 0.95, "高", fontsize=12, ha='center', va='center')
        cbar_ax.text(1.2, 0.05, "低", fontsize=12, ha='center', va='center')
        
        # 确保特征值标签也是中文
        cbar.set_label("特征值")
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"{time_of_day}_shap_summary.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"{time_of_day} SHAP摘要图已保存")
    
    # 2. SHAP摘要图（条形图）
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
    plt.title(f'{time_of_day} - SHAP特征重要性条形图')
    plt.savefig(os.path.join(save_dir, f"{time_of_day}_shap_bar.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"{time_of_day} SHAP条形图已保存")
    
    # 3. 每个特征的SHAP依赖图
    for i, feature in enumerate(X_test.columns):
        plt.figure(figsize=(10, 6))
        shap.dependence_plot(feature, shap_values.values, X_test, show=False)
        plt.title(f'{time_of_day} - {feature} SHAP依赖图')
        plt.xlabel(f'{feature} ({variable_units.get(feature, "")})')
        # 清理文件名，移除特殊字符
        clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        plt.savefig(os.path.join(save_dir, f"{time_of_day}_{clean_feature}_shap_dependence.png"), dpi=300, bbox_inches='tight')
        plt.close()
    print(f"{time_of_day} SHAP依赖图已保存")

# 绘制PDP依赖图
def plot_pdp_visualizations(time_of_day, model, X_test):
    print(f"\n--- 绘制{time_of_day} PDP可视化图 ---")
    
    if time_of_day == "早高峰":
        save_dir = early_peak_dir
    else:
        save_dir = late_peak_dir
    
    # 使用shap的partial_dependence函数绘制PDP图
    for feature in X_test.columns:
        plt.figure(figsize=(10, 6))
        shap.plots.partial_dependence(
            feature, model.predict, X_test, ice=False, 
            model_expected_value=True, feature_expected_value=True
        )
        plt.title(f'{time_of_day} - {feature} 部分依赖图')
        plt.xlabel(f'{feature} ({variable_units.get(feature, "")})')
        plt.ylabel('碳排放_carbon_emission_kg (kgCO2/KM/d)')
        # 清理文件名，移除特殊字符
        clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        plt.savefig(os.path.join(save_dir, f"{time_of_day}_{clean_feature}_pdp.png"), dpi=300, bbox_inches='tight')
        plt.close()
    print(f"{time_of_day} PDP图已保存")

# 分析变量交互作用
def analyze_interactions(time_of_day, explainer, shap_values, X_test):
    print(f"\n--- 分析{time_of_day}变量交互作用 ---")
    
    if time_of_day == "早高峰":
        save_dir = early_peak_dir
    else:
        save_dir = late_peak_dir
    
    # 计算特征间的交互强度
    interaction_values = shap.TreeExplainer(explainer.model).shap_interaction_values(X_test)
    
    # 计算平均交互强度（取绝对值）
    mean_interaction = np.abs(interaction_values).mean(axis=0)
    
    # 排除自身交互（对角线）
    np.fill_diagonal(mean_interaction, 0)
    
    # 获取前4组最强交互
    feature_names = X_test.columns
    n_features = len(feature_names)
    
    # 生成所有特征对并计算交互强度
    interactions = []
    for i in range(n_features):
        for j in range(i+1, n_features):
            interactions.append((feature_names[i], feature_names[j], mean_interaction[i, j]))
    
    # 按交互强度排序
    interactions.sort(key=lambda x: x[2], reverse=True)
    
    # 打印前4组最强交互
    print(f"{time_of_day}前4组最强交互变量：")
    for i, (feat1, feat2, strength) in enumerate(interactions[:4]):
        print(f"{i+1}. {feat1} 与 {feat2}，交互强度：{strength:.4f}")
        
        # 绘制交互图
        plt.figure(figsize=(12, 8))
        shap.dependence_plot(
            (feat1, feat2), shap_values.values, X_test, 
            interaction_index=1, show=False
        )
        plt.title(f'{time_of_day} - {feat1} 与 {feat2} 交互作用图')
        # 清理文件名，移除特殊字符
        clean_feat1 = feat1.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        clean_feat2 = feat2.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
        plt.savefig(os.path.join(save_dir, f"{time_of_day}_{clean_feat1}_vs_{clean_feat2}_interaction.png"), dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"{time_of_day}变量交互作用图已保存")

# 生成变量重要度报告
def generate_importance_report(time_of_day, explainer, shap_values, X_test):
    print(f"\n--- 生成{time_of_day}变量重要度报告 ---")
    
    # 计算SHAP特征重要度（平均绝对SHAP值）
    shap_importance = np.abs(shap_values.values).mean(axis=0)
    
    # 计算特征总重要度
    total_importance = shap_importance.sum()
    
    # 计算重要度占比
    importance_percentage = (shap_importance / total_importance) * 100
    
    # 计算正负向反馈（平均SHAP值的符号）
    mean_shap_values = shap_values.values.mean(axis=0)
    feedback = np.where(mean_shap_values > 0, '正向', '负向')
    
    # 创建重要度DataFrame
    importance_df = pd.DataFrame({
        '特征名': X_test.columns,
        'SHAP重要度': shap_importance,
        '重要度占比(%)': importance_percentage,
        '正负向反馈': feedback,
        '单位': [variable_units.get(feature, "") for feature in X_test.columns]
    })
    
    # 按重要度排序
    importance_df = importance_df.sort_values(by='SHAP重要度', ascending=False)
    
    # 保存为CSV文件
    importance_df.to_csv(os.path.join(output_dir, f"{time_of_day}_变量重要度报告.csv"), index=False, encoding='utf-8-sig')
    
    print(f"{time_of_day}变量重要度报告已生成：")
    print(importance_df)
    
    return importance_df

# 主函数
def main():
    # 设置是否跳过PDP依赖图和交互分析
    skip_pdp = True  # 跳过PDP依赖图
    skip_interaction = True  # 跳过交互分析
    
    print(f"\n--- 分析配置 ---\n跳过PDP依赖图: {skip_pdp}\n跳过交互分析: {skip_interaction}\n")
    
    # 处理早高峰数据
    X_early, y_early = load_data("早高峰")
    X_early_train, X_early_test, y_early_train, y_early_test = train_test_split(X_early, y_early, test_size=0.3, random_state=42)
    print(f"早高峰训练集大小：{X_early_train.shape}，测试集大小：{X_early_test.shape}")
    
    # 处理晚高峰数据
    X_late, y_late = load_data("晚高峰")
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    print(f"晚高峰训练集大小：{X_late_train.shape}，测试集大小：{X_late_test.shape}")
    
    # 训练模型并分析早高峰数据
    model_early, explainer_early, shap_values_early = train_and_analyze("早高峰", X_early_train, y_early_train, X_early_test, y_early_test)
    plot_shap_visualizations("早高峰", explainer_early, shap_values_early, X_early_test)
    
    if not skip_pdp:
        plot_pdp_visualizations("早高峰", model_early, X_early_test)
    else:
        print(f"\n--- 跳过早高峰 PDP依赖图生成 ---\n")
        
    if not skip_interaction:
        analyze_interactions("早高峰", explainer_early, shap_values_early, X_early_test)
    else:
        print(f"\n--- 跳过早高峰交互分析 ---\n")
        
    generate_importance_report("早高峰", explainer_early, shap_values_early, X_early_test)
    
    # 训练模型并分析晚高峰数据
    model_late, explainer_late, shap_values_late = train_and_analyze("晚高峰", X_late_train, y_late_train, X_late_test, y_late_test)
    plot_shap_visualizations("晚高峰", explainer_late, shap_values_late, X_late_test)
    
    if not skip_pdp:
        plot_pdp_visualizations("晚高峰", model_late, X_late_test)
    else:
        print(f"\n--- 跳过晚高峰 PDP依赖图生成 ---\n")
        
    if not skip_interaction:
        analyze_interactions("晚高峰", explainer_late, shap_values_late, X_late_test)
    else:
        print(f"\n--- 跳过晚高峰交互分析 ---\n")
        
    generate_importance_report("晚高峰", explainer_late, shap_values_late, X_late_test)
    
    print(f"\n--- 所有分析完成！---")
    print(f"结果保存在：{output_dir}")
    
    # 解释PDP依赖图与SHAP重要度报告不一致的原因
    print("\n--- 关于PDP依赖图与SHAP重要度不一致的说明 ---\n")
    print("1. 定义不同：")
    print("   - SHAP重要度：基于平均绝对SHAP值，反映特征对模型预测的整体影响程度")
    print("   - PDP依赖图：显示单个特征与目标变量之间的边际效应，不直接反映特征重要性")
    print("\n2. 计算方法不同：")
    print("   - SHAP重要度：考虑特征与其他所有特征的交互作用")
    print("   - PDP依赖图：假设特征与其他特征独立，忽略交互作用")
    print("\n3. 目的不同：")
    print("   - SHAP重要度：回答'哪个特征对模型预测最重要'的问题")
    print("   - PDP依赖图：回答'特征值如何影响预测结果'的问题")
    print("\n因此，即使某个特征的SHAP重要度很高，它的PDP依赖图可能看起来比较平坦，")
    print("这是因为该特征的影响可能通过与其他特征的交互作用体现，而不是通过自身的线性关系。")

if __name__ == "__main__":
    main()