"""
Script để vẽ biểu đồ kết quả training
Tạo loss curves và metrics visualization
"""

import matplotlib.pyplot as plt
import numpy as np

# Dữ liệu từ result_model_training_optimized.txt
# Epoch và metrics
epochs = [1, 10, 20, 30, 40, 50, 60, 70, 80, 100]
map50 = [0.124, 0.561, 0.689, 0.718, 0.741, 0.747, 0.751, 0.753, 0.754, 0.755]
precision = [0.374, 0.585, 0.642, 0.668, 0.684, 0.687, 0.700, 0.713, 0.708, 0.714]
recall = [0.175, 0.555, 0.691, 0.720, 0.738, 0.742, 0.748, 0.741, 0.747, 0.747]

# Loss values (ước tính từ log)
box_loss = [1.248, 1.115, 1.008, 0.946, 0.919, 0.881, 0.849, 0.823, 0.812, 0.594]
cls_loss = [3.722, 2.121, 1.637, 1.472, 1.369, 1.268, 1.186, 1.103, 1.092, 0.588]
dfl_loss = [1.547, 1.419, 1.340, 1.301, 1.288, 1.260, 1.240, 1.220, 1.221, 1.137]

def plot_training_metrics():
    """Vẽ biểu đồ metrics theo epoch"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. mAP50 theo epoch
    ax1 = axes[0, 0]
    ax1.plot(epochs, map50, marker='o', linewidth=2, markersize=8, color='blue')
    ax1.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax1.set_ylabel('mAP50', fontsize=12, fontweight='bold')
    ax1.set_title('mAP50 theo Epoch', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0, 0.8])
    
    # Highlight best
    best_epoch = epochs[np.argmax(map50)]
    best_map = max(map50)
    ax1.annotate(f'Best: {best_map:.4f}\nEpoch {best_epoch}',
                xy=(best_epoch, best_map),
                xytext=(best_epoch + 15, best_map - 0.05),
                fontsize=10, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red'),
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    # 2. Precision và Recall
    ax2 = axes[0, 1]
    ax2.plot(epochs, precision, marker='s', linewidth=2, markersize=8, 
             label='Precision', color='green')
    ax2.plot(epochs, recall, marker='^', linewidth=2, markersize=8, 
             label='Recall', color='orange')
    ax2.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax2.set_title('Precision và Recall theo Epoch', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 0.8])
    
    # 3. Loss curves
    ax3 = axes[1, 0]
    ax3.plot(epochs, box_loss, marker='o', linewidth=2, markersize=6, 
             label='Box Loss', color='blue')
    ax3.plot(epochs, cls_loss, marker='s', linewidth=2, markersize=6, 
             label='Classification Loss', color='red')
    ax3.plot(epochs, dfl_loss, marker='^', linewidth=2, markersize=6, 
             label='DFL Loss', color='green')
    ax3.set_xlabel('Epoch', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Loss', fontsize=12, fontweight='bold')
    ax3.set_title('Loss Curves', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.set_yscale('log')
    
    # 4. So sánh Baseline vs Balanced
    ax4 = axes[1, 1]
    categories = ['Baseline\n(Imbalanced)', 'After Balancing']
    values = [0.6925, 0.7565]
    colors = ['red', 'green']
    bars = ax4.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax4.set_ylabel('mAP50', fontsize=12, fontweight='bold')
    ax4.set_title('So sánh Baseline vs Balanced Data', fontsize=14, fontweight='bold')
    ax4.set_ylim([0.6, 0.8])
    ax4.grid(axis='y', alpha=0.3)
    
    # Thêm số liệu và improvement
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Thêm arrow cho improvement
    improvement = ((0.7565 - 0.6925) / 0.6925) * 100
    ax4.annotate(f'+{improvement:.1f}%',
                xy=(1, 0.7565),
                xytext=(0.5, 0.75),
                fontsize=14, fontweight='bold', color='green',
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    plt.tight_layout()
    plt.savefig('training_results.png', dpi=300, bbox_inches='tight')
    print("✅ Đã lưu biểu đồ: training_results.png")

if __name__ == "__main__":
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.facecolor'] = 'white'
    
    plot_training_metrics()
    print("\n✅ Hoàn thành! Kiểm tra file training_results.png")

