import os
import shutil

def main():
    # 定义路径
    new_summary_path = 'd:/Desktop/项目论文/SHAP值解释性分析/早高峰/早高峰_shap_summary.png'
    new_bar_path = 'd:/Desktop/项目论文/SHAP值解释性分析/早高峰/早高峰_shap_bar.png'
    old_fig_dir = 'd:/Desktop/项目论文/shap可视化/'
    
    print('检查文件路径：')
    print(f'新摘要图存在: {os.path.exists(new_summary_path)}')
    print(f'新条形图存在: {os.path.exists(new_bar_path)}')
    print(f'旧图目录存在: {os.path.exists(old_fig_dir)}')
    
    # 复制新生成的可视化图到旧图目录
    if os.path.exists(new_summary_path) and os.path.exists(old_fig_dir):
        # 备份旧图
        print('\n备份旧图：')
        for i in range(1, 5):
            old_fig_path = os.path.join(old_fig_dir, f'Figure_{i}.png')
            if os.path.exists(old_fig_path):
                backup_path = os.path.join(old_fig_dir, f'Figure_{i}_backup.png')
                shutil.copy2(old_fig_path, backup_path)
                print(f'  已备份: Figure_{i}.png -> Figure_{i}_backup.png')
        
        # 复制新图
        print('\n复制新图到旧图目录：')
        new_figure1_path = os.path.join(old_fig_dir, 'Figure_1.png')
        new_figure2_path = os.path.join(old_fig_dir, 'Figure_2.png')
        
        shutil.copy2(new_summary_path, new_figure1_path)
        shutil.copy2(new_bar_path, new_figure2_path)
        
        print(f'  已复制: 早高峰_shap_summary.png -> Figure_1.png')
        print(f'  已复制: 早高峰_shap_bar.png -> Figure_2.png')
        
        # 验证复制结果
        print('\n验证复制结果：')
        print(f'  Figure_1.png存在: {os.path.exists(new_figure1_path)}')
        print(f'  Figure_2.png存在: {os.path.exists(new_figure2_path)}')
        
        if os.path.exists(new_figure1_path):
            print(f'\n成功！现在您在d:/Desktop/项目论文/shap可视化/目录中看到的Figure_1.png将与')
            print(f'SHAP值解释性分析/早高峰_变量重要度报告.csv中的重要度排序保持一致。')
    else:
        print('\n错误：无法找到源文件或目标目录。')

if __name__ == '__main__':
    main()