import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 确保输出目录存在
output_dir = 'D:/Desktop/项目论文/建模/机器学习模型预测验证'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 数据加载和预处理
def load_data():
    """加载早晚高峰标准化后的数据"""
    morning_data_path = 'D:/Desktop/项目论文/建模/特征工程/优化后_早高峰_标准化_utf8.csv'
    evening_data_path = 'D:/Desktop/项目论文/建模/特征工程/优化后_晚高峰_标准化_utf8.csv'
    
    morning_df = pd.read_csv(morning_data_path)
    evening_df = pd.read_csv(evening_data_path)
    
    # 处理晚高峰数据中的多余空列（与早高峰数据保持一致的列）
    evening_df = evening_df[morning_df.columns]
    
    # 合并早晚高峰数据
    combined_df = pd.concat([morning_df, evening_df], axis=0, ignore_index=True)
    
    # 处理缺失值（删除包含NaN的行）
    print(f"原始数据大小: {combined_df.shape}")
    combined_df = combined_df.dropna()
    print(f"处理缺失值后数据大小: {combined_df.shape}")
    
    # 分离特征和目标变量
    X = combined_df.drop('碳排放_carbon_emission_kg (kgCO2/KM/d)', axis=1)
    y = combined_df['碳排放_carbon_emission_kg (kgCO2/KM/d)']
    
    return X, y

# 计算平均绝对百分比误差
def mean_absolute_percentage_error(y_true, y_pred): 
    """计算平均绝对百分比误差"""
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero_mask = y_true != 0
    return np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100

# 网格搜索参数优化
def grid_search_model(model, param_grid, X_train, y_train):
    """使用网格搜索寻找模型最佳参数"""
    # 使用均方误差作为损失函数和评分标准
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, 
                               cv=10, scoring='neg_mean_squared_error', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    return grid_search

# 主函数
def main():
    """主函数"""
    print("加载数据...")
    X, y = load_data()
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"数据加载完成，训练集大小: {X_train.shape}, 测试集大小: {X_test.shape}")
    
    # 定义模型和超参数网格（简化版，减少拟合次数）
    models = {
        '逻辑回归': {
            'model': LinearRegression(),
            'param_grid': {
                # 逻辑回归没有这些参数，使用默认参数
            }
        },
        '随机森林': {
            'model': RandomForestRegressor(random_state=42),
            'param_grid': {
                'n_estimators': [50, 100],  # 生成树的数量
                'max_depth': [5, 10],  # 树的最大深度
                'max_features': ['sqrt', 'log2']  # 每个分裂点考虑的特征数量
            }
        },
        'GBDT': {
            'model': GradientBoostingRegressor(random_state=42),
            'param_grid': {
                'n_estimators': [50, 100],  # 生成树的数量
                'max_depth': [3, 5],  # 树的最大深度
                'learning_rate': [0.05, 0.1]  # 学习率
            }
        },
        'XGBoost': {
            'model': XGBRegressor(random_state=42),
            'param_grid': {
                'n_estimators': [50, 100],  # 生成树的数量
                'max_depth': [3, 5],  # 树的最大深度
                'learning_rate': [0.05, 0.1],  # 学习率
                'subsample': [0.9, 1.0]  # 每棵树使用的样本比例
            }
        }
    }
    
    # 存储最佳模型和结果
    best_models = {}
    metrics_results = []
    best_params_list = []
    
    # 遍历所有模型进行参数优化和验证
    for model_name, model_info in models.items():
        print(f"\n{model_name}模型网格搜索...")
        
        if model_name == '逻辑回归':
            # 逻辑回归使用默认参数，不进行网格搜索
            best_model = model_info['model']
            best_model.fit(X_train, y_train)
            best_params = "默认参数"
        else:
            # 使用网格搜索寻找最佳参数
            grid_search = grid_search_model(model_info['model'], model_info['param_grid'], X_train, y_train)
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
        
        best_models[model_name] = best_model
        
        print(f"{model_name}最佳参数: {best_params}")
        print(f"模型训练完成")
        
        # 模型预测
        y_pred_train = best_model.predict(X_train)
        y_pred_test = best_model.predict(X_test)
        
        # 计算训练集评价指标
        mse_train = mean_squared_error(y_train, y_pred_train)
        mae_train = mean_absolute_error(y_train, y_pred_train)
        r2_train = r2_score(y_train, y_pred_train)
        mape_train = mean_absolute_percentage_error(y_train, y_pred_train)
        
        # 计算测试集评价指标
        mse_test = mean_squared_error(y_test, y_pred_test)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        r2_test = r2_score(y_test, y_pred_test)
        mape_test = mean_absolute_percentage_error(y_test, y_pred_test)
        
        # 保存测试集指标
        metrics_results.append({
            '模型': model_name,
            'MSE': mse_test,
        'MAE': mae_test,
        'R2': r2_test,
        'MAPE': mape_test
        })
        
        # 保存最佳参数
        best_params_list.append({
            '模型': model_name,
            '最佳参数': str(best_params)
        })
        
        print(f"训练集指标:")
        print(f"  MSE: {mse_train:.4f}")
        print(f"  MAE: {mae_train:.4f}")
        print(f"  R2: {r2_train:.4f}")
        print(f"  MAPE: {mape_train:.4f}%")
        
        print(f"测试集指标:")
        print(f"  MSE: {mse_test:.4f}")
        print(f"  MAE: {mae_test:.4f}")
        print(f"  R2: {r2_test:.4f}")
        print(f"  MAPE: {mape_test:.4f}%")
    
    # 保存最佳参数（含中文释义）
    print("\n保存最佳参数...")
    # 添加参数中文释义
    params_interpretation = {
        '逻辑回归': {
            '参数': '默认参数',
            '中文释义': '线性回归模型，使用最小二乘法拟合数据'
        },
        '随机森林': {
            'n_estimators': '生成树的数量',
            'max_depth': '树的最大深度',
            'max_features': '每个分裂点考虑的特征数量',
            'min_samples_split': '分裂内部节点所需的最小样本数',
            'min_samples_leaf': '叶子节点所需的最小样本数'
        },
        'GBDT': {
            'n_estimators': '生成树的数量',
            'max_depth': '树的最大深度',
            'learning_rate': '学习率',
            'subsample': '每棵树使用的样本比例',
            'min_samples_split': '分裂内部节点所需的最小样本数',
            'min_samples_leaf': '叶子节点所需的最小样本数'
        },
        'XGBoost': {
            'n_estimators': '生成树的数量',
            'max_depth': '树的最大深度',
            'learning_rate': '学习率',
            'subsample': '每棵树使用的样本比例',
            'colsample_bytree': '每棵树使用的特征比例',
            'reg_alpha': 'L1正则化参数',
            'reg_lambda': 'L2正则化参数'
        }
    }
    
    # 创建带中文释义的最佳参数文件
    best_params_with_interpretation = []
    for item in best_params_list:
        model_name = item['模型']
        best_params = item['最佳参数']
        
        if model_name == '逻辑回归':
            interpretation = params_interpretation[model_name]['中文释义']
            best_params_with_interpretation.append({
                '模型': model_name,
                '最佳参数': best_params,
                '参数中文释义': interpretation
            })
        else:
            # 解析参数字典
            params_dict = eval(best_params)
            interpretation = []
            for param, value in params_dict.items():
                if param in params_interpretation[model_name]:
                    interpretation.append(f"{params_interpretation[model_name][param]}: {value}")
            
            best_params_with_interpretation.append({
                '模型': model_name,
                '最佳参数': best_params,
                '参数中文释义': '; '.join(interpretation)
            })
    
    # 保存带中文释义的最佳参数
    print("\n保存最佳参数...")
    best_params_df = pd.DataFrame(best_params_with_interpretation)
    print(f"最佳参数数据框形状: {best_params_df.shape}")
    print(f"最佳参数数据框内容: {best_params_df}")
    best_params_path = os.path.join(output_dir, '最佳参数设置_带中文释义.csv')
    best_params_df.to_csv(best_params_path, index=False, encoding='utf-8-sig')
    print(f"最佳参数已保存到: {best_params_path}")
    
    # 保存评价指标
    print("保存评价指标...")
    metrics_df = pd.DataFrame(metrics_results)
    print(f"评价指标数据框形状: {metrics_df.shape}")
    print(f"评价指标数据框内容: {metrics_df}")
    metrics_path = os.path.join(output_dir, '模型评价指标_网格搜索.csv')
    metrics_df.to_csv(metrics_path, index=False, encoding='utf-8-sig')
    print(f"评价指标已保存到: {metrics_path}")
    
    print("\n所有模型训练和验证完成！")
    print("结果已保存到:", output_dir)

if __name__ == "__main__":
    main()