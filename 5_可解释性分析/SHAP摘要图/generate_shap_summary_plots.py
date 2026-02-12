import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt
import os
from matplotlib.colors import LinearSegmentedColormap

# 设置字体：中文用宋体，英文数字用新罗马，大小统一为小四（12pt）
plt.rcParams['font.sans-serif'] = ['SimSun']  # 中文宋体
plt.rcParams['font.serif'] = ['Times New Roman']  # 英文新罗马
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams['font.family'] = ['sans-serif', 'serif']  # 混合字体设置
plt.rcParams['font.size'] = 12  # 全局字体大小设为小四（12pt）

# 使用SHAP默认的红蓝色映射
default_cmap = 'RdBu_r'  # SHAP库默认的红蓝颜色映射

# 确保输出目录存在
output_dir = "D:/Desktop/项目论文/灰白图"
os.makedirs(output_dir, exist_ok=True)
print(f"输出目录已创建或存在: {output_dir}")

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
    
    # 处理晚高峰数据中的额外列
    # 删除所有包含空值的列（由额外逗号导致）
    df = df.dropna(axis=1, how='all')
    
    print(f"{time_of_day}数据清理后形状：{df.shape}")
    
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
    
    # 创建SHAP解释器
    explainer = shap.Explainer(model)
    shap_values = explainer(X_test)
    
    return model, explainer, shap_values

# 绘制SHAP摘要图
def plot_shap_summary(time_of_day, explainer, shap_values, X_test):
    print(f"\n--- 绘制{time_of_day} SHAP摘要图 ---")
    
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
    
    # 1. SHAP摘要图（特征重要性）
    plt.figure(figsize=(10, 7))  # 缩小高度，从10改为7
    # plt.title(f"{time_of_day} - SHAP特征重要性摘要图", fontsize=15)  # 删除标题
    
    # 使用自定义特征名称并调整标签，使用默认红蓝色映射，禁用默认颜色条
    shap.summary_plot(shap_values, X_test, feature_names=feature_names_without_units, plot_type="dot", show=False, plot_size=(10, 7), cmap=default_cmap, color_bar=False, max_display=len(feature_names_without_units))
    
    # 获取当前的轴
    ax = plt.gca()
    
    # 修改横坐标标签和范围，放大字体（中文宋体，英文新罗马）
    ax.set_xlabel("SHAP值（对模型输出的影响）", fontsize=22, fontfamily=['SimSun', 'Times New Roman'])
    ax.set_xlim(-1.0, 2.0)
    
    # 缩小横坐标刻度间隔
    ax.set_xticks(np.arange(-1.0, 2.01, 0.5))
    
    # 设置横坐标和纵坐标刻度字体大小，与条形图保持一致
    ax.tick_params(axis='both', labelsize=22)
    
    # 显示纵坐标轴和刻度
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_linewidth(1)
    ax.yaxis.set_visible(True)
    # 添加纵坐标刻度线，调整宽度与横坐标一致
    ax.tick_params(axis='y', which='both', left=True, right=False, labelleft=True, labelright=False, width=1, length=4)
    
    # 强制设置1:1宽高比
    ax.set_aspect(1/ax.get_data_ratio())
    
    # 获取主图的位置
    fig = plt.gcf()
    bbox_main = ax.get_position()  # 主图位置
    
    # 手动创建颜色条，完全控制其位置、大小和标签
    # 获取散点图的数据范围用于颜色条
    vmin = X_test.values.min()
    vmax = X_test.values.max()
    
    # 创建颜色条轴，宽度缩小到原来的10分之一（0.01）
    cax = fig.add_axes([bbox_main.x1 + 0.02, bbox_main.y0, 0.01, bbox_main.height])
    
    # 创建颜色条，设置标签
    norm = plt.Normalize(vmin, vmax)
    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=default_cmap), cax=cax)
    
    # 设置颜色条标签为中文宋体，字体大小与坐标轴一致（18号）
    cb.set_label("特征值", fontsize=22, fontfamily='SimSun')
    
    # 移除颜色条刻度
    cb.ax.set_yticklabels([])
    cb.ax.tick_params(length=0)
    
    # 在颜色条旁边添加中文标识（高/低），向右移动并设置与坐标轴一致的字体大小（18号）
    cax.text(3.0, 0.95, "高", fontsize=22, ha='center', va='center', transform=cax.transAxes, fontfamily='SimSun')
    cax.text(3.0, 0.05, "低", fontsize=22, ha='center', va='center', transform=cax.transAxes, fontfamily='SimSun')
    
    # 不使用tight_layout()，避免覆盖颜色条位置调整
    plt.savefig(os.path.join(output_dir, f"{time_of_day}_shap_summary.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"{time_of_day} SHAP摘要图已保存")

# 绘制SHAP条形图
def plot_shap_bar(time_of_day, shap_values, X_test):
    print(f"\n--- 绘制{time_of_day} SHAP条形图 ---")
    
    # 处理特征名称
    feature_names_without_units = []
    for name in X_test.columns:
        if "办公POI数量" in name:
            feature_names_without_units.append("就业办公POI数量")
        elif "居住POI数量" in name:
            feature_names_without_units.append("商品住宅POI数量")
        elif "标准化土地混合熵" in name:
            feature_names_without_units.append("标准化土地混合度")
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
            if " (" in name:
                name = name.split(" (")[0]
            feature_names_without_units.append(name)
    
    plt.figure(figsize=(10, 10))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names_without_units, plot_type="bar", show=False)
    # plt.title(f'{time_of_day} - SHAP特征重要性条形图')  # 删除标题
    
    # 修改条形图颜色为深灰色
    ax = plt.gca()
    for patch in ax.patches:
        patch.set_facecolor('#404040')  # 深灰色
    
    # 设置横纵坐标刻度字体大小和字体类型，确保一致
    # 显式为x轴和y轴分别设置，确保SHAP的默认设置被覆盖
    ax.tick_params(axis='x', labelsize=14, labelfontfamily=['SimSun', 'Times New Roman'])
    ax.tick_params(axis='y', labelsize=14, labelfontfamily=['SimSun', 'Times New Roman'])
    
    # 设置横坐标标签字体大小
    ax.set_xlabel("SHAP值", fontsize=14, fontfamily=['SimSun', 'Times New Roman'])
    
    # 设置横坐标范围和刻度
    ax.set_xlim(0.0, 0.4)
    ax.set_xticks(np.arange(0.0, 0.41, 0.05))
    
    # 强制设置1:1宽高比
    ax.set_aspect(1/ax.get_data_ratio())
    plt.savefig(os.path.join(output_dir, f"{time_of_day}_shap_bar.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"{time_of_day} SHAP条形图已保存")

# 主函数
def main():
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
    plot_shap_summary("早高峰", explainer_early, shap_values_early, X_early_test)
    plot_shap_bar("早高峰", shap_values_early, X_early_test)
    
    # 训练模型并分析晚高峰数据
    model_late, explainer_late, shap_values_late = train_and_analyze("晚高峰", X_late_train, y_late_train, X_late_test, y_late_test)
    plot_shap_summary("晚高峰", explainer_late, shap_values_late, X_late_test)
    plot_shap_bar("晚高峰", shap_values_late, X_late_test)
    
    print(f"\n--- 所有SHAP摘要图生成完成！---")
    print(f"结果保存在：{output_dir}")

if __name__ == "__main__":
    main()