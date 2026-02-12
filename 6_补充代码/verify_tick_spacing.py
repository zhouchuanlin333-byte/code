import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 模拟到市中心距离的特征范围（假设最大距离为30km）
x_min = 0
x_max = 30

# 原刻度计算逻辑
def original_tick_logic(x_min, x_max):
    tick_spacing = (x_max - x_min) / 5
    if tick_spacing < 0.1:
        tick_spacing = 0.05
    elif tick_spacing < 1:
        tick_spacing = 0.1
    elif tick_spacing < 5:
        tick_spacing = 0.5
    elif tick_spacing < 10:
        tick_spacing = 1
    elif tick_spacing < 50:
        tick_spacing = 5
    elif tick_spacing < 100:
        tick_spacing = 10
    else:
        tick_spacing = 50
    return tick_spacing

# 新刻度计算逻辑
def new_tick_logic(x_min, x_max, unit):
    tick_spacing = (x_max - x_min) / 5
    
    # 根据特征类型和单位调整刻度间隔
    if "km" in unit or "KM" in unit:
        if tick_spacing < 0.5:
            tick_spacing = 0.5
        elif tick_spacing < 2:
            tick_spacing = 1
        elif tick_spacing < 5:
            tick_spacing = 2
        elif tick_spacing < 10:
            tick_spacing = 5
        elif tick_spacing < 50:
            tick_spacing = 10
        else:
            tick_spacing = 20
    else:
        # 其他特征保持原有逻辑，但增加适应性
        if tick_spacing < 0.1:
            tick_spacing = 0.1  # 最小刻度至少为0.1
        elif tick_spacing < 1:
            tick_spacing = 0.2
        elif tick_spacing < 5:
            tick_spacing = 0.5
        elif tick_spacing < 10:
            tick_spacing = 1
        elif tick_spacing < 50:
            tick_spacing = 5
        elif tick_spacing < 100:
            tick_spacing = 10
        else:
            tick_spacing = 50
    return tick_spacing

# 计算刻度
original_ticks = np.arange(np.round(x_min / original_tick_logic(x_min, x_max)) * original_tick_logic(x_min, x_max), 
                          np.round(x_max / original_tick_logic(x_min, x_max)) * original_tick_logic(x_min, x_max) + original_tick_logic(x_min, x_max), 
                          original_tick_logic(x_min, x_max))

new_ticks = np.arange(np.round(x_min / new_tick_logic(x_min, x_max, "km")) * new_tick_logic(x_min, x_max, "km"), 
                     np.round(x_max / new_tick_logic(x_min, x_max, "km")) * new_tick_logic(x_min, x_max, "km") + new_tick_logic(x_min, x_max, "km"), 
                     new_tick_logic(x_min, x_max, "km"))

# 绘制对比图表
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# 原刻度
ax1.set_title('原刻度逻辑（不合适的小刻度）', fontsize=14, fontweight='bold')
ax1.set_xlim(x_min, x_max)
ax1.set_xticks(original_ticks)
ax1.set_xlabel('到市中心距离 (km)', fontsize=12)
ax1.set_ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
ax1.grid(True, alpha=0.3)

# 在x轴下方标记每个刻度
for i, tick in enumerate(original_ticks):
    ax1.text(tick, -0.5, f'{tick:.1f}', ha='center', fontsize=10, rotation=45)

# 新刻度
ax2.set_title('新刻度逻辑（合适的大刻度）', fontsize=14, fontweight='bold')
ax2.set_xlim(x_min, x_max)
ax2.set_xticks(new_ticks)
ax2.set_xlabel('到市中心距离 (km)', fontsize=12)
ax2.set_ylabel('碳排放 (kgCO2/KM/d)', fontsize=12)
ax2.grid(True, alpha=0.3)

# 在x轴下方标记每个刻度
for i, tick in enumerate(new_ticks):
    ax2.text(tick, -0.5, f'{tick:.1f}', ha='center', fontsize=10, rotation=45)

plt.tight_layout()
plt.savefig('刻度对比图.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"原刻度间隔: {original_tick_logic(x_min, x_max):.2f} km")
print(f"原刻度数量: {len(original_ticks)}")
print(f"原刻度值: {original_ticks}")
print(f"\n新刻度间隔: {new_tick_logic(x_min, x_max, 'km'):.2f} km")
print(f"新刻度数量: {len(new_ticks)}")
print(f"新刻度值: {new_ticks}")
print(f"\n刻度对比完成，图表已保存为'刻度对比图.png'")