import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# 尝试导入shap库，如果失败则跳过SHAP分析
try:
    import shap
    shap_available = True
except ImportError:
    shap_available = False
    print("shap库未安装，将跳过SHAP分析")

# 设置中文字体为宋体，英文字体为Times New Roman
plt.rcParams['font.sans-serif'] = ['SimSun', 'Times New Roman']
plt.rcParams['font.family'] = ['SimSun', 'Times New Roman']
plt.rcParams['axes.unicode_minus'] = False

# 确保输出目录存在
output_dir = 'd:/Desktop/项目论文/建模/机器学习模型预测验证'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 数据加载函数，分别返回早高峰和晚高峰数据
def load_data_by_period():
    """加载早高峰和晚高峰标准化后的数据"""
    morning_data_path = 'd:/Desktop/项目论文/建模/早高峰_标准化_utf8.csv'
    evening_data_path = 'd:/Desktop/项目论文/建模/晚高峰_标准化_utf8.csv'
    
    # 加载数据
    morning_df = pd.read_csv(morning_data_path)
    evening_df = pd.read_csv(evening_data_path)
    
    # 处理缺失值
    print(f"早高峰原始数据大小: {morning_df.shape}")
    morning_df = morning_df.dropna()
    print(f"早高峰处理缺失值后数据大小: {morning_df.shape}")
    
    print(f"晚高峰原始数据大小: {evening_df.shape}")
    evening_df = evening_df.dropna()
    print(f"晚高峰处理缺失值后数据大小: {evening_df.shape}")
    
    # 分离特征和目标变量
    X_morning = morning_df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y_morning = morning_df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    X_evening = evening_df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y_evening = evening_df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return (X_morning, y_morning), (X_evening, y_evening)

# 计算MAPE
def calculate_mape(y_true, y_pred):
    """计算平均绝对百分比误差"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

# 绘制单个拟合曲线
def plot_fit_curve(y_true, y_pred, model_name, data_type, period_name, r2_value):
    """绘制模型拟合曲线并标记R2值"""
    fig = plt.figure(figsize=(8, 8))  # 调整为1:1比例
    plt.scatter(y_true, y_pred, alpha=0.5, s=20)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('真实值', fontsize=18)
    plt.ylabel('预测值', fontsize=18)
    plt.title(f'{period_name}-{model_name}-{data_type}拟合曲线', fontsize=20)
    # plt.grid(True)  # 删除网格线
    
    # 设置坐标轴刻度字体大小
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    
    # 在左上角标注模型名称和R2值
    model_text = f'{model_name}'
    r2_text = f'R²={r2_value:.4f}'
    
    # 添加模型名称（居中显示，调整位置确保在左上角完全显示）
    plt.text(0.15, 0.95, model_text, transform=plt.gca().transAxes, fontsize=18, 
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 添加R2值（在模型名称下方，居中显示）
    plt.text(0.15, 0.88, r2_text, transform=plt.gca().transAxes, fontsize=18, 
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    return fig

# 绘制某个时段（早高峰或晚高峰）所有模型的训练集和测试集拟合图
def plot_all_separate_fit_curves(models, X_train, y_train, X_test, y_test, period_name):
    """绘制某个时段所有模型的训练集和测试集拟合图"""
    results = {}
    
    for model_name, model in models.items():
        # 训练模型
        model.fit(X_train, y_train)
        
        # 预测
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # 计算评估指标
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        mae_train = mean_absolute_error(y_train, y_pred_train)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        mape_train = calculate_mape(y_train, y_pred_train)
        mape_test = calculate_mape(y_test, y_pred_test)
        
        # 绘制训练集拟合曲线
        train_plot = plot_fit_curve(y_train, y_pred_train, model_name, '训练集', period_name, r2_train)
        train_plot.savefig(os.path.join(output_dir, f'{period_name}-{model_name}-训练集拟合曲线.png'), dpi=150, bbox_inches='tight')
        plt.close(train_plot)
        
        # 绘制测试集拟合曲线
        test_plot = plot_fit_curve(y_test, y_pred_test, model_name, '测试集', period_name, r2_test)
        test_plot.savefig(os.path.join(output_dir, f'{period_name}-{model_name}-测试集拟合曲线.png'), dpi=150, bbox_inches='tight')
        plt.close(test_plot)
        
        # 保存结果
        results[model_name] = {
            'r2_train': r2_train,
            'r2_test': r2_test,
            'mse_train': mse_train,
            'mse_test': mse_test,
            'mae_train': mae_train,
            'mae_test': mae_test,
            'mape_train': mape_train,
            'mape_test': mape_test
        }
        
        # 打印结果
        print(f"{period_name}-{model_name}:")
        print(f"  训练集 - MSE: {mse_train:.4f}, MAE: {mae_train:.4f}, R²: {r2_train:.4f}, MAPE: {mape_train:.2f}%")
        print(f"  测试集 - MSE: {mse_test:.4f}, MAE: {mae_test:.4f}, R²: {r2_test:.4f}, MAPE: {mape_test:.2f}%")
    
    return results

# 主函数
def perform_shap_analysis(model, X, y, feature_names, output_dir, period_name):
    """
    对XGBoost模型进行SHAP值分析
    
    参数：
    model: 训练好的XGBoost模型
    X: 特征数据
    y: 目标变量
    feature_names: 特征名称列表
    output_dir: 输出目录
    period_name: 时段名称（早高峰/晚高峰）
    """
    if not shap_available:
        return
        
    try:
        # 创建SHAP解释器
        explainer = shap.TreeExplainer(model)
        
        # 计算SHAP值
        shap_values = explainer.shap_values(X)
        
        # 创建SHAP值目录
        shap_dir = os.path.join(output_dir, f"SHAP值解释性分析_{period_name}")
        os.makedirs(shap_dir, exist_ok=True)
        
        # 1. 绘制SHAP汇总图
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X, feature_names=feature_names, show=False)
        plt.title(f"{period_name} SHAP值汇总图")
        plt.tight_layout()
        plt.savefig(os.path.join(shap_dir, f"{period_name}_SHAP汇总图.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. 绘制SHAP条形图（变量重要度）
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X, feature_names=feature_names, plot_type="bar", show=False)
        plt.title(f"{period_name} 变量重要度条形图")
        plt.tight_layout()
        plt.savefig(os.path.join(shap_dir, f"{period_name}_变量重要度条形图.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. 计算每个变量的平均SHAP值（重要度）和正负性影响
        mean_abs_shap = np.abs(shap_values).mean(axis=0)
        mean_shap = shap_values.mean(axis=0)
        
        # 创建变量重要度表
        importance_df = pd.DataFrame({
            '变量名称': feature_names,
            '平均SHAP值（影响方向）': mean_shap,
            '平均绝对SHAP值（重要度）': mean_abs_shap
        })
        
        # 按重要度排序
        importance_df = importance_df.sort_values(by='平均绝对SHAP值（重要度）', ascending=False)
        
        # 保存变量重要度表
        importance_df.to_csv(os.path.join(shap_dir, f"{period_name}_变量重要度及影响方向.csv"), index=False, encoding='utf-8-sig')
        
        print(f"{period_name} SHAP分析完成，结果已保存到 {shap_dir}")
        
    except Exception as e:
        print(f"{period_name} SHAP分析过程中出错: {e}")

def main():
    """主函数"""
    print("加载数据...")
    (X_morning, y_morning), (X_evening, y_evening) = load_data_by_period()
    
    # 定义模型
    models = {
        'RF': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
        'GBDT': GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.1,random_state=42),
        'XGBoost': XGBRegressor(n_estimators=500, max_depth=5, learning_rate=0.05, random_state=42)
    }
    
    # 处理早高峰数据
    print("\n" + "="*50)
    print("处理早高峰数据...")
    X_train_morning, X_test_morning, y_train_morning, y_test_morning = train_test_split(
        X_morning, y_morning, test_size=0.2, random_state=42
    )
    print(f"早高峰训练集大小: {X_train_morning.shape}, 测试集大小: {X_test_morning.shape}")
    
    # 绘制早高峰所有模型的训练集和测试集拟合图
    morning_results = plot_all_separate_fit_curves(
        models, X_train_morning, y_train_morning, X_test_morning, y_test_morning, "早高峰"
    )
    
    # 处理晚高峰数据
    print("\n" + "="*50)
    print("处理晚高峰数据...")
    X_train_evening, X_test_evening, y_train_evening, y_test_evening = train_test_split(
        X_evening, y_evening, test_size=0.2, random_state=42
    )
    print(f"晚高峰训练集大小: {X_train_evening.shape}, 测试集大小: {X_test_evening.shape}")
    
    # 绘制晚高峰所有模型的训练集和测试集拟合图
    evening_results = plot_all_separate_fit_curves(
        models, X_train_evening, y_train_evening, X_test_evening, y_test_evening, "晚高峰"
    )
    
    # 生成总表
    print("\n" + "="*50)
    print("生成测试集验证指标总表...")
    
    # 准备数据
    index = []
    metrics = []
    
    for period in ["早高峰", "晚高峰"]:
        results = morning_results if period == "早高峰" else evening_results
        for model_name in models.keys():
            index.append(f"{period}-{model_name}")
            metrics.append({
                '时段': period,
                '模型': model_name,
                'MSE': results[model_name]['mse_test'],
                'MAE': results[model_name]['mae_test'],
                'R²': results[model_name]['r2_test'],
                'MAPE(%)': results[model_name]['mape_test']
            })
    
    # 创建DataFrame
    metrics_df = pd.DataFrame(metrics, index=index)
    metrics_df = metrics_df[['时段', '模型', 'MSE', 'MAE', 'R²', 'MAPE(%)']]
    
    # 保存为CSV文件
    output_file = os.path.join(output_dir, '测试集验证指标总表.csv')
    # 如果文件存在，先删除
    if os.path.exists(output_file):
        os.remove(output_file)
    metrics_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # 打印总表
    print("测试集验证指标总表:")
    print(metrics_df)
    print(f"\n总表已保存到: {output_file}")
    
    # 执行SHAP分析
    print("\n" + "="*50)
    print("执行SHAP值分析...")
    
    # 早高峰XGBoost模型SHAP分析
    xgb_morning = models['XGBoost']
    xgb_morning.fit(X_train_morning, y_train_morning)
    perform_shap_analysis(
        xgb_morning, X_test_morning, y_test_morning, 
        X_morning.columns.tolist(), output_dir, "早高峰"
    )
    
    # 晚高峰XGBoost模型SHAP分析
    xgb_evening = models['XGBoost']
    xgb_evening.fit(X_train_evening, y_train_evening)
    perform_shap_analysis(
        xgb_evening, X_test_evening, y_test_evening, 
        X_evening.columns.tolist(), output_dir, "晚高峰"
    )
    
    print("\n" + "="*50)
    print("所有模型训练和验证完成！")
    print(f"结果已保存到: {output_dir}")
    print("\n生成的文件列表:")
    for period in ["早高峰", "晚高峰"]:
        for model in models.keys():
            print(f"  - {period}-{model}-训练集拟合曲线.png")
            print(f"  - {period}-{model}-测试集拟合曲线.png")
        print(f"  - SHAP值解释性分析_{period}/")
    print("  - 测试集验证指标总表.csv")

if __name__ == "__main__":
    main()