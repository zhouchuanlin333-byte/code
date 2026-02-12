import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

def main():
    # 加载早高峰数据
    early_file_path = "d:/Desktop/项目论文/建模/早高峰_统一单位.csv"
    early_df = pd.read_csv(early_file_path)
    
    # 加载晚高峰数据
    late_file_path = "d:/Desktop/项目论文/建模/晚高峰1_统一单位.csv"
    late_df = pd.read_csv(late_file_path)
    
    print(f"早高峰数据形状: {early_df.shape}")
    print(f"晚高峰数据形状: {late_df.shape}")
    
    # 分析"到市中心距离"与碳排放的直接关系
    for time_period, df in ["早高峰", early_df], ["晚高峰", late_df]:
        print(f"\n\n{'='*60}")
        print(f"{time_period} - 到市中心距离与碳排放关系分析")
        print('='*60)
        
        # 查看到市中心距离的统计信息
        distance_col = "到市中心距离 (km)"
        carbon_col = "碳排放_carbon_emission_kg (kgCO2/KM/d)"
        
        print(f"到市中心距离统计:")
        print(f"  最小值: {df[distance_col].min():.2f} km")
        print(f"  最大值: {df[distance_col].max():.2f} km")
        print(f"  均值: {df[distance_col].mean():.2f} km")
        print(f"  中位数: {df[distance_col].median():.2f} km")
        print(f"  标准差: {df[distance_col].std():.2f} km")
        
        # 查看碳排放的统计信息
        print(f"\n碳排放统计:")
        print(f"  最小值: {df[carbon_col].min():.4f} kgCO2/KM/d")
        print(f"  最大值: {df[carbon_col].max():.4f} kgCO2/KM/d")
        print(f"  均值: {df[carbon_col].mean():.4f} kgCO2/KM/d")
        print(f"  中位数: {df[carbon_col].median():.4f} kgCO2/KM/d")
        print(f"  标准差: {df[carbon_col].std():.4f} kgCO2/KM/d")
        
        # 计算相关系数
        correlation = df[distance_col].corr(df[carbon_col])
        print(f"\n到市中心距离与碳排放的相关系数: {correlation:.4f}")
        
        # 按距离区间分组分析碳排放
        bins = np.linspace(0, df[distance_col].max(), 10)
        labels = [f"{bins[i]:.1f}-{bins[i+1]:.1f}" for i in range(len(bins)-1)]
        df['距离区间'] = pd.cut(df[distance_col], bins=bins, labels=labels)
        
        interval_stats = df.groupby('距离区间')[carbon_col].agg(['mean', 'median', 'std', 'count'])
        print(f"\n不同距离区间的碳排放统计:")
        print(interval_stats.round(4))
        
        # 使用XGBoost模型单独分析距离与碳排放的关系
        X = df[[distance_col]]
        y = df[carbon_col]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # 训练简单的XGBoost模型
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        print(f"\n仅使用距离特征的XGBoost模型R²: {r2:.4f}")
        
        # 生成非线性关系曲线
        distance_range = np.linspace(0, df[distance_col].max(), 200).reshape(-1, 1)
        carbon_pred = model.predict(distance_range)
        
        # 绘制距离与碳排放的关系图
        plt.figure(figsize=(10, 6))
        
        # 散点图（采样部分点以提高性能）
        sampled_df = df.sample(n=min(500, len(df)), random_state=42)
        plt.scatter(sampled_df[distance_col], sampled_df[carbon_col], alpha=0.3, s=20, color='blue', label='原始数据点')
        
        # XGBoost预测的非线性曲线
        plt.plot(distance_range, carbon_pred, color='red', linewidth=2.5, label='非线性关系曲线（XGBoost）')
        
        # 趋势线（简单线性回归）
        from sklearn.linear_model import LinearRegression
        lr_model = LinearRegression()
        lr_model.fit(X, y)
        lr_pred = lr_model.predict(distance_range)
        plt.plot(distance_range, lr_pred, color='green', linewidth=2, linestyle='--', label='线性趋势线')
        
        plt.title(f'{time_period} - 到市中心距离与碳排放关系', fontsize=14, fontweight='bold')
        plt.xlabel('到市中心距离 (km)', fontsize=12)
        plt.ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(f"d:/Desktop/项目论文/距离与碳排放关系_{time_period}.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n{time_period}分析完成，图表已保存")

if __name__ == "__main__":
    main()
