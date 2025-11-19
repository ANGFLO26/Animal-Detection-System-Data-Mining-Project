"""
Script để vẽ biểu đồ phân bố classes trong dataset
Sử dụng để tạo hình ảnh minh họa cho báo cáo và slide
"""

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

# Dữ liệu từ result_data_preparation_pro.txt
# Top classes và bottom classes để minh họa
class_data = {
    'Butterfly': 2035,
    'Moths and butterflies': 291,
    'Lizard': 291,
    'Monkey': 206,
    'Spider': 204,
    'Fish': 269,
    'Snake': 147,
    'Frog': 133,
    'Duck': 126,
    'Parrot': 118,
    'Caterpillar': 113,
    'Chicken': 104,
    'Horse': 103,
    'Jellyfish': 102,
    'Deer': 100,
    'Tortoise': 97,
    'Snail': 96,
    'Owl': 91,
    'Camel': 90,
    'Squirrel': 86,
    'Ladybug': 86,
    'Penguin': 87,
    'Eagle': 179,
    'Bear': 124,
    'Brown bear': 140,
    'Bull': 119,
    'Cattle': 46,
    'Centipede': 47,
    'Cheetah': 32,
    'Crab': 75,
    'Crocodile': 35,
    'Elephant': 34,
    'Fox': 42,
    'Giraffe': 63,
    'Goat': 59,
    'Goldfish': 31,
    'Goose': 65,
    'Hamster': 26,
    'Harbor seal': 60,
    'Hedgehog': 25,
    'Hippopotamus': 19,
    'Jaguar': 25,
    'Kangaroo': 28,
    'Koala': 14,
    'Leopard': 32,
    'Lion': 55,
    'Lynx': 22,
    'Magpie': 19,
    'Mule': 19,
    'Ostrich': 41,
    'Otter': 27,
    'Panda': 22,
    'Pig': 56,
    'Polar bear': 56,
    'Rabbit': 65,
    'Raccoon': 30,
    'Raven': 28,
    'Red panda': 17,
    'Rhinoceros': 48,
    'Scorpion': 24,
    'Sea lion': 47,
    'Sea turtle': 65,
    'Seahorse': 8,
    'Shark': 73,
    'Sheep': 34,
    'Shrimp': 17,
    'Sparrow': 122,
    'Squid': 28,  # Ít samples
    'Starfish': 59,
    'Swan': 60,
    'Tick': 15,
    'Tiger': 63,
    'Turkey': 25,
    'Turtle': 29,  # Ít samples
    'Whale': 68,
    'Woodpecker': 41,
    'Worm': 28,
    'Zebra': 39,
    'Canary': 26,
}

def plot_class_distribution():
    """Vẽ biểu đồ phân bố classes"""
    
    # Sắp xếp theo số lượng
    sorted_classes = sorted(class_data.items(), key=lambda x: x[1], reverse=True)
    classes = [c[0] for c in sorted_classes]
    counts = [c[1] for c in sorted_classes]
    
    # Tạo figure với 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Subplot 1: Bar chart tất cả classes
    ax1.barh(range(len(classes)), counts, color='steelblue')
    ax1.set_yticks(range(len(classes)))
    ax1.set_yticklabels(classes, fontsize=8)
    ax1.set_xlabel('Số lượng ảnh', fontsize=12, fontweight='bold')
    ax1.set_title('Phân bố số lượng ảnh theo từng class (80 classes)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    # Highlight các classes có ít samples
    for i, (cls, count) in enumerate(sorted_classes):
        if count < 30:
            ax1.barh(i, count, color='red', alpha=0.7)
    
    # Thêm annotation cho max và min
    max_idx = 0
    min_idx = len(classes) - 1
    ax1.annotate(f'Max: {counts[max_idx]}', 
                xy=(counts[max_idx], max_idx),
                xytext=(counts[max_idx] + 50, max_idx),
                fontsize=10, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='green'))
    ax1.annotate(f'Min: {counts[min_idx]}', 
                xy=(counts[min_idx], min_idx),
                xytext=(counts[min_idx] + 50, min_idx),
                fontsize=10, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red'))
    
    # Subplot 2: Top 20 và Bottom 10
    top_20 = sorted_classes[:20]
    bottom_10 = sorted_classes[-10:]
    
    top_classes = [c[0] for c in top_20]
    top_counts = [c[1] for c in top_20]
    bottom_classes = [c[0] for c in bottom_10]
    bottom_counts = [c[1] for c in bottom_10]
    
    x_pos_top = np.arange(len(top_classes))
    x_pos_bottom = np.arange(len(bottom_classes))
    
    ax2.bar(x_pos_top, top_counts, color='green', alpha=0.7, label='Top 20')
    ax2.bar(x_pos_bottom + len(top_classes) + 2, bottom_counts, 
            color='red', alpha=0.7, label='Bottom 10')
    
    ax2.set_xticks(list(x_pos_top) + list(x_pos_bottom + len(top_classes) + 2))
    ax2.set_xticklabels(top_classes + bottom_classes, rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Số lượng ảnh', fontsize=12, fontweight='bold')
    ax2.set_title('Top 20 classes có nhiều ảnh nhất và Bottom 10 classes có ít ảnh nhất', 
                  fontsize=12, fontweight='bold', pad=20)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('class_distribution.png', dpi=300, bbox_inches='tight')
    print("✅ Đã lưu biểu đồ: class_distribution.png")
    
    # Tạo biểu đồ thứ 2: Phân loại classes
    fig2, ax = plt.subplots(figsize=(10, 6))
    
    # Phân loại
    very_few = [c for c, count in class_data.items() if count < 15]
    few = [c for c, count in class_data.items() if 15 <= count < 30]
    good = [c for c, count in class_data.items() if count >= 30]
    
    categories = ['Rất ít (< 15)', 'Ít (15-30)', 'Tốt (≥ 30)']
    counts_cat = [len(very_few), len(few), len(good)]
    colors = ['red', 'orange', 'green']
    
    bars = ax.bar(categories, counts_cat, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax.set_ylabel('Số lượng classes', fontsize=12, fontweight='bold')
    ax.set_title('Phân loại classes theo số lượng samples', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)
    
    # Thêm số liệu trên mỗi cột
    for bar, count in zip(bars, counts_cat):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{count} classes',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('class_categories.png', dpi=300, bbox_inches='tight')
    print("✅ Đã lưu biểu đồ: class_categories.png")
    
    # In thống kê
    print("\n📊 THỐNG KÊ:")
    print(f"   Tổng classes: {len(class_data)}")
    print(f"   Tổng ảnh: {sum(class_data.values())}")
    print(f"   Max: {max(class_data.values())} ({max(class_data, key=class_data.get)})")
    print(f"   Min: {min(class_data.values())} ({min(class_data, key=class_data.get)})")
    print(f"   Trung bình: {np.mean(list(class_data.values())):.1f}")
    print(f"   Imbalance ratio: {max(class_data.values()) / min(class_data.values()):.1f}:1")
    print(f"\n   Rất ít (< 15): {len(very_few)} classes")
    print(f"   Ít (15-30): {len(few)} classes")
    print(f"   Tốt (≥ 30): {len(good)} classes")

if __name__ == "__main__":
    # Set font để hiển thị tiếng Việt
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['figure.facecolor'] = 'white'
    
    plot_class_distribution()
    print("\n✅ Hoàn thành! Kiểm tra các file PNG đã được tạo.")

