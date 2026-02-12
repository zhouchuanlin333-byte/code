import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import shap
import matplotlib.pyplot as plt
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 确保输出目录存在
output_dir = "d:/Desktop/项目论文/SHAP值解释性分析"
late_peak_dir = os.path.join(output_dir, "晚高峰")

# 确保目录存在
os.makedirs(output_dir, exist_ok=True)
os.makedirs(late_peak_dir, exist_ok=True)
print(f"输出目录已创建或存在: {output_dir}")
print(f"晚高峰目录已创建或存在: {late_peak_dir}")

# 定义变量名和单位（原始单位）
variable_units = {
    "人口密度 (千人/km²)": "千人/km²",
    "办公POI数量 (个)": "个",
    "居住POI数量 (个)": "个",
    "道路密度 (KM/KM²)": "KM/KM²",
    "地铁站点数量 (个)": "个",
    "公交站点数量 (个)": "个",
    "标准化土地混合熵": "无单位",
    "到市中心距离 (km)": "km",
    "到最近公交距离 (km)": "km"
}

# 读取晚高峰数据
def load_late_peak_data():
    file_path = "d:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv"
    df = pd.read_csv(file_path)
    print(f"晚高峰数据加载完成，形状：{df.shape}")
    print(f"晚高峰数据列名：{list(df.columns)}")
    
    # 处理晚高峰数据中的额外列
    # 删除所有包含空值的列（由额外逗号导致）
    df = df.dropna(axis=1, how='all')
    
    print(f"晚高峰数据清理后形状：{df.shape}")
    print(f"晚高峰数据清理后列名：{list(df.columns)}")
    
    # 处理列名中的空格（如果有的话）
    df.columns = [col.strip() for col in df.columns]
    
    # 分离特征和目标变量
    X = df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 训练XGBoost模型并进行SHAP分析
def train_and_analyze(X_train, y_train, X_test, y_test):
    print(f"\n--- 晚高峰数据分析 ---")
    
    # 训练XGBoost模型
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 评估模型
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"晚高峰 XGBoost模型测试集MSE: {mse:.5f}")
    
    # 保存模型
    model.save_model(os.path.join(output_dir, f"晚高峰_xgb_model.json"))
    
    # 创建SHAP解释器
    explainer = shap.Explainer(model)
    shap_values = explainer(X_test)
    
    # 保存SHAP值
    np.save(os.path.join(output_dir, f"晚高峰_shap_values.npy"), shap_values.values)
    np.save(os.path.join(output_dir, f"晚高峰_X_test.npy"), X_test.values)
    
    return model, explainer, shap_values

# 绘制SHAP值可视化图
def plot_shap_visualizations(explainer, shap_values, X_test):
    print(f"\n--- 绘制晚高峰 SHAP可视化图 ---")
    time_of_day = "晚高峰"
    save_dir = late_peak_dir
    
    # 1. SHAP摘要图（特征重要性）
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X_test, show=False)
    plt.title(f'{time_of_day} - SHAP特征重要性摘要图')
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
def plot_pdp_visualizations(model, X_test):
    print(f"\n--- 绘制晚高峰 PDP可视化图 ---")
    time_of_day = "晚高峰"
    save_dir = late_peak_dir
    
    # 使用sklearn的PartialDependenceDisplay
    from sklearn.inspection import PartialDependenceDisplay
    
    # 对每个特征绘制PDP图
    for feature in X_test.columns:
        try:
            print(f"正在绘制 {time_of_day} - {feature} PDP图...")
            
            # 创建画布
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 绘制PDP图
            PartialDependenceDisplay.from_estimator(
                model, X_test, [feature], ax=ax, random_state=42
            )
            
            # 设置标题和标签
            ax.set_title(f'{time_of_day} - {feature} 部分依赖图')
            ax.set_xlabel(f'{feature} ({variable_units.get(feature, "")})')
            ax.set_ylabel('碳排放_carbon_emission_kg (kgCO2/KM/d)')
            
            # 清理文件名，移除特殊字符
            clean_feature = feature.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
            
            # 保存图像
            plt.tight_layout()
            plt.savefig(os.path.join(save_dir, f"{time_of_day}_{clean_feature}_pdp.png"), dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"成功绘制 {time_of_day} - {feature} PDP图")
        except Exception as e:
            print(f"绘制 {time_of_day} - {feature} PDP图时出错: {e}")
            import traceback
            traceback.print_exc()
    print(f"{time_of_day} PDP图绘制完成")

# 分析变量交互作用
def analyze_interactions(explainer, shap_values, X_test):
    print(f"\n--- 分析晚高峰变量交互作用 ---")
    time_of_day = "晚高峰"
    save_dir = late_peak_dir
    
    try:
        # 使用SHAP重要度最高的4个特征来绘制交互图
        # 计算SHAP特征重要度（平均绝对SHAP值）
        shap_importance = np.abs(shap_values.values).mean(axis=0)
        
        # 获取前4个最重要的特征
        top_features = X_test.columns[np.argsort(shap_importance)[::-1][:4]]
        
        print(f"{time_of_day}前4个最重要的特征：{list(top_features)}")
        
        # 绘制这些特征之间的交互图
        print(f"{time_of_day}绘制特征交互作用图：")
        for i, feat1 in enumerate(top_features):
            for j, feat2 in enumerate(top_features[i+1:], i+1):
                try:
                    print(f"正在绘制 {feat1} 与 {feat2} 的交互作用图...")
                    plt.figure(figsize=(12, 8))
                    shap.dependence_plot(
                        feat1, shap_values.values, X_test, interaction_index=feat2, show=False
                    )
                    plt.title(f'{time_of_day} - {feat1} 与 {feat2} 交互作用图')
                    
                    # 清理文件名，移除特殊字符
                    clean_feat1 = feat1.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
                    clean_feat2 = feat2.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '')
                    
                    plt.savefig(os.path.join(save_dir, f"{time_of_day}_{clean_feat1}_vs_{clean_feat2}_interaction.png"), dpi=300, bbox_inches='tight')
                    plt.close()
                    print(f"成功绘制 {time_of_day} - {feat1} 与 {feat2} 交互作用图")
                except Exception as e:
                    print(f"绘制 {feat1} 与 {feat2} 交互作用图时出错: {e}")
                    continue
        
        print(f"{time_of_day}变量交互作用图已保存")
    except Exception as e:
        print(f"分析变量交互作用时出错: {e}")
        import traceback
        traceback.print_exc()
        print("跳过变量交互作用分析")

# 生成变量重要度报告
def generate_importance_report(explainer, shap_values, X_test):
    print(f"\n--- 生成晚高峰变量重要度报告 ---")
    time_of_day = "晚高峰"
    
    try:
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
        csv_path = os.path.join(output_dir, f"{time_of_day}_变量重要度报告.csv")
        importance_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        print(f"{time_of_day}变量重要度报告已生成：")
        print(importance_df)
        print(f"报告保存路径：{csv_path}")
        
        return importance_df
    except Exception as e:
        print(f"生成变量重要度报告时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

# 主函数
def main():
    # 处理晚高峰数据
    X_late, y_late = load_late_peak_data()
    X_late_train, X_late_test, y_late_train, y_late_test = train_test_split(X_late, y_late, test_size=0.3, random_state=42)
    print(f"晚高峰训练集大小：{X_late_train.shape}，测试集大小：{X_late_test.shape}")
    
    # 训练模型并分析晚高峰数据
    model_late, explainer_late, shap_values_late = train_and_analyze(X_late_train, y_late_train, X_late_test, y_late_test)
    plot_shap_visualizations(explainer_late, shap_values_late, X_late_test)
    plot_pdp_visualizations(model_late, X_late_test)
    analyze_interactions(explainer_late, shap_values_late, X_late_test)
    generate_importance_report(explainer_late, shap_values_late, X_late_test)
    
    print(f"\n--- 晚高峰分析完成！---")
    print(f"结果保存在：{output_dir}")

if __name__ == "__main__":
    main()