import pandas as pd
import numpy as np

# 模拟数据：基于已查看的分析报告
vif_data = {
    '特征': ['人口密度 (千人/km²)', '休闲POI数量 (个)', '办公POI数量 (个)', 
            '公共服务POI数量 (个)', '交通设施POI数量 (个)', '居住POI数量 (个)',
            '道路密度 (KM/KM²)', '地铁站点数量 (个)', '公交站点数量 (个)',
            '标准化土地混合熵', '到市中心距离 (km)', '到最近公交距离 (km)'],
    'VIF': [1.0192, 3.2554, 1.6976, 3.9178, 4.1078, 1.8480, 1.0851, 1.1341, 1.6194, 1.7414, 2.9773, 2.1862]
}

# 高相关系数的特征对
high_correlations = [
    ('休闲POI数量 (个)', '公共服务POI数量 (个)', 0.808377),
    ('公共服务POI数量 (个)', '交通设施POI数量 (个)', 0.757694),
    ('休闲POI数量 (个)', '交通设施POI数量 (个)', 0.686740),
    ('公共服务POI数量 (个)', '居住POI数量 (个)', 0.630875),
    ('交通设施POI数量 (个)', '居住POI数量 (个)', 0.620598),
    ('休闲POI数量 (个)', '居住POI数量 (个)', 0.589014)
]

# 计算每个特征的综合评分（结合VIF和相关系数）
def calculate_feature_scores(vif_df, high_corr_pairs):
    # 初始化每个特征的评分
    scores = {feature: {'vif': vif, 'high_corr_count': 0, 'max_corr': 0} 
              for feature, vif in zip(vif_df['特征'], vif_df['VIF'])}
    
    # 统计每个特征的高相关系数情况
    for feat1, feat2, corr in high_corr_pairs:
        if corr > 0.6:
            scores[feat1]['high_corr_count'] += 1
            scores[feat2]['high_corr_count'] += 1
            scores[feat1]['max_corr'] = max(scores[feat1]['max_corr'], corr)
            scores[feat2]['max_corr'] = max(scores[feat2]['max_corr'], corr)
    
    # 计算综合评分（VIF * 高相关计数 * 最大相关系数的加权）
    for feat in scores:
        scores[feat]['score'] = scores[feat]['vif'] * (1 + scores[feat]['high_corr_count'] * 0.5) * \
                              (1 + scores[feat]['max_corr'] * 0.5)
    
    return scores

# 创建DataFrame并计算评分
vif_df = pd.DataFrame(vif_data)
feature_scores = calculate_feature_scores(vif_df, high_correlations)

# 转换为DataFrame便于排序
scores_df = pd.DataFrame.from_dict(feature_scores, orient='index').reset_index()
scores_df.columns = ['特征', 'VIF', '高相关计数', '最大相关系数', '综合评分']

# 按综合评分降序排序
scores_df = scores_df.sort_values('综合评分', ascending=False)

# 生成筛选建议报告
print("="*60)
print("特征共线性筛选建议报告")
print("="*60)
print("\n基于VIF和皮尔逊相关系数分析，建议移除以下三个共线性强的特征：\n")

# 获取综合评分最高的三个特征（应删除的）
features_to_remove = scores_df.head(3)
for i, row in features_to_remove.iterrows():
    print(f"{i+1}. {row['特征']}")
    print(f"   VIF值: {row['VIF']:.4f}")
    print(f"   与其他特征的高相关对数量: {row['高相关计数']}")
    print(f"   最大相关系数: {row['最大相关系数']:.6f}")
    print(f"   综合评分: {row['综合评分']:.4f}")
    print()

print("="*60)
print("特征间高相关性详情（相关系数 > 0.6）：")
print("="*60)
for feat1, feat2, corr in high_correlations:
    if corr > 0.6:
        print(f"{feat1} - {feat2}: {corr:.6f}")

print("\n" + "="*60)
print("删除理由说明：")
print("="*60)
print("1. 虽然所有特征的VIF值都小于5（从严格标准看不存在严重共线性），")
print("   但从相关系数角度分析，存在多对特征之间相关性较高（>0.6）。")
print("\n2. 公共服务POI数量与休闲POI数量的相关系数高达0.808，表明二者信息高度重叠。")
print("\n3. 交通设施POI数量与公共服务POI数量相关系数为0.758，且VIF值最高(4.1078)。")
print("\n4. 居住POI数量与多个其他POI特征存在中等程度的相关性。")
print("\n5. 删除这三个特征可以减少模型复杂度，降低过拟合风险，")
print("   同时保留足够的预测信息。")

# 保存结果到CSV
scores_df.to_csv('d:/Desktop/项目论文/建模/特征工程/特征共线性筛选结果.csv', index=False, encoding='utf-8-sig')
print("\n筛选结果已保存到 '特征共线性筛选结果.csv'")
