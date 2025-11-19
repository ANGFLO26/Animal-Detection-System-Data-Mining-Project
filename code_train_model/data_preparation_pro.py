"""
========================================
FILE 1: data_preparation_pro.py (PROFESSIONAL VERSION)
========================================
Pipeline chuẩn bị dữ liệu CHUYÊN NGHIỆP cho Object Detection

FEATURES:
✅ Phân tích data imbalance
✅ Data cleaning & validation
✅ Xử lý class imbalance (oversample/undersample)
✅ Stratified split
✅ Class-specific augmentation
✅ Quality metrics & reports
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import yaml
import re
from collections import Counter
import random
import numpy as np

class ProfessionalDataPreparation:
    def __init__(self, dataset_path, output_path, min_samples_per_class=30):
        """
        dataset_path: folder dataset gốc
        output_path: folder output
        min_samples_per_class: số ảnh tối thiểu/class (classes ít hơn sẽ bị oversample)
        """
        self.dataset_path = Path(dataset_path)
        self.output_path = Path(output_path)
        self.min_samples_per_class = min_samples_per_class
        self.classes = []
        
        # Statistics
        self.stats = {
            'total_images': 0,
            'processed': 0,
            'skipped': 0,
            'augmented': 0,
            'class_distribution': {},
            'classes_removed': [],
            'classes_oversampled': []
        }
        
        random.seed(42)
        np.random.seed(42)
    
    # ========== BƯỚC 1: PHÂN TÍCH ==========
    
    def analyze_dataset(self):
        """BƯỚC 1: Phân tích toàn bộ dataset"""
        print("="*70)
        print("📊 BƯỚC 1: PHÂN TÍCH DATASET")
        print("="*70)
        
        # Get classes
        train_path = self.dataset_path / 'train'
        classes = []
        for item in train_path.iterdir():
            if item.is_dir() and item.name != 'Label':
                classes.append(item.name)
        
        self.classes = sorted(classes)
        print(f"✓ Tìm thấy {len(self.classes)} classes")
        
        # Count images per class
        class_counts = {}
        for split in ['train', 'test']:
            split_path = self.dataset_path / split
            if not split_path.exists():
                continue
            
            for class_folder in split_path.iterdir():
                if not class_folder.is_dir() or class_folder.name == 'Label':
                    continue
                
                class_name = class_folder.name
                images = [f for f in class_folder.iterdir() 
                         if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp']]
                
                if class_name not in class_counts:
                    class_counts[class_name] = 0
                class_counts[class_name] += len(images)
        
        self.stats['class_distribution'] = class_counts
        
        # Analyze imbalance
        total_images = sum(class_counts.values())
        avg_per_class = total_images / len(class_counts)
        max_count = max(class_counts.values())
        min_count = min(class_counts.values())
        imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
        
        print(f"\n📈 PHÂN TÍCH:")
        print(f"   - Tổng ảnh: {total_images}")
        print(f"   - Trung bình/class: {avg_per_class:.1f}")
        print(f"   - Max: {max_count} | Min: {min_count}")
        print(f"   - Imbalance ratio: {imbalance_ratio:.1f}:1")
        
        # Categorize
        very_few = [(c, n) for c, n in class_counts.items() if n < 15]
        few = [(c, n) for c, n in class_counts.items() if 15 <= n < self.min_samples_per_class]
        good = [(c, n) for c, n in class_counts.items() if n >= self.min_samples_per_class]
        
        print(f"\n🔍 PHÂN LOẠI:")
        print(f"   🔴 Rất ít (< 15): {len(very_few)} classes")
        print(f"   🟡 Ít (< {self.min_samples_per_class}): {len(few)} classes")
        print(f"   🟢 Tốt (>= {self.min_samples_per_class}): {len(good)} classes")
        
        if very_few:
            print(f"\n   Classes rất ít data (sẽ BỎ QUA):")
            for cls, count in sorted(very_few, key=lambda x: x[1])[:10]:
                print(f"      - {cls}: {count} ảnh")
        
        if few:
            print(f"\n   Classes cần OVERSAMPLE:")
            for cls, count in sorted(few, key=lambda x: x[1])[:10]:
                target = self.min_samples_per_class
                print(f"      - {cls}: {count} → {target} ảnh")
        
        return {
            'very_few': very_few,
            'few': few,
            'good': good,
            'imbalance_ratio': imbalance_ratio
        }
    
    # ========== BƯỚC 2: VALIDATE IMAGE & BBOX ==========
    
    def validate_image(self, img_path):
        """Validate ảnh"""
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                if w < 32 or h < 32 or w > 10000 or h > 10000:
                    return False, 0, 0
                img.verify()
                return True, w, h
        except:
            return False, 0, 0
    
    def validate_and_fix_bbox(self, x_min, y_min, x_max, y_max, img_w, img_h):
        """Validate và fix bbox"""
        # Swap if wrong
        if x_min > x_max: x_min, x_max = x_max, x_min
        if y_min > y_max: y_min, y_max = y_max, y_min
        
        # Clamp
        x_min = max(0, min(img_w, x_min))
        y_min = max(0, min(img_h, y_min))
        x_max = max(0, min(img_w, x_max))
        y_max = max(0, min(img_h, y_max))
        
        # Check valid
        w = x_max - x_min
        h = y_max - y_min
        
        if w < 5 or h < 5:
            return False, 0, 0, 0, 0
        
        area = w * h
        img_area = img_w * img_h
        
        if area < 0.0005 * img_area or area > 0.98 * img_area:
            return False, 0, 0, 0, 0
        
        return True, x_min, y_min, x_max, y_max
    
    # ========== BƯỚC 3: PARSE LABEL ==========
    
    def parse_label_file(self, label_path, img_w, img_h, class_name):
        """Parse label với class name có space"""
        try:
            with open(label_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                return None
            
            # Clean
            content = re.sub(r'\s+', ' ', content)
            
            # Extract coordinates
            coords = re.findall(r'-?\d+\.?\d*', content)
            if len(coords) < 4:
                return None
            
            x_min, y_min, x_max, y_max = map(float, coords[:4])
            
            # Validate & fix
            is_valid, x_min, y_min, x_max, y_max = self.validate_and_fix_bbox(
                x_min, y_min, x_max, y_max, img_w, img_h
            )
            
            if not is_valid:
                return None
            
            # To YOLO format
            x_center = ((x_min + x_max) / 2) / img_w
            y_center = ((y_min + y_max) / 2) / img_h
            width = (x_max - x_min) / img_w
            height = (y_max - y_min) / img_h
            
            # Clamp
            x_center = max(0, min(1, x_center))
            y_center = max(0, min(1, y_center))
            width = max(0, min(1, width))
            height = max(0, min(1, height))
            
            if width < 0.005 or height < 0.005:
                return None
            
            class_id = self.classes.index(class_name)
            return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
            
        except:
            return None
    
    # ========== BƯỚC 4: COLLECT & FILTER DATA ==========
    
    def collect_valid_samples(self, analysis):
        """Thu thập tất cả samples hợp lệ"""
        print("\n" + "="*70)
        print("📦 BƯỚC 2: THU THẬP & LỌC DỮ LIỆU")
        print("="*70)
        
        # Classes to keep (remove very_few)
        classes_to_remove = [c for c, _ in analysis['very_few']]
        self.stats['classes_removed'] = classes_to_remove
        
        if classes_to_remove:
            print(f"\n🔴 Loại bỏ {len(classes_to_remove)} classes (< 15 ảnh)")
            self.classes = [c for c in self.classes if c not in classes_to_remove]
            print(f"✓ Còn lại: {len(self.classes)} classes")
        
        # Collect all valid samples
        all_samples = {cls: [] for cls in self.classes}
        
        for split in ['train', 'test']:
            split_path = self.dataset_path / split
            if not split_path.exists():
                continue
            
            print(f"\n📂 Đang thu thập từ {split}...")
            
            for class_folder in split_path.iterdir():
                if not class_folder.is_dir() or class_folder.name == 'Label':
                    continue
                
                class_name = class_folder.name
                if class_name not in self.classes:
                    continue
                
                label_folder = class_folder / 'Label'
                if not label_folder.exists():
                    continue
                
                for img_file in class_folder.iterdir():
                    if img_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.bmp']:
                        continue
                    
                    # Validate image
                    is_valid, img_w, img_h = self.validate_image(img_file)
                    if not is_valid:
                        continue
                    
                    # Get label
                    label_file = label_folder / f"{img_file.stem}.txt"
                    if not label_file.exists():
                        continue
                    
                    # Parse label
                    yolo_label = self.parse_label_file(label_file, img_w, img_h, class_name)
                    if yolo_label is None:
                        continue
                    
                    # Add to collection
                    all_samples[class_name].append({
                        'image_path': img_file,
                        'label': yolo_label,
                        'class': class_name
                    })
        
        # Print statistics
        print(f"\n✓ Thu thập hoàn tất:")
        for cls in self.classes[:5]:
            print(f"   - {cls}: {len(all_samples[cls])} samples")
        if len(self.classes) > 5:
            print(f"   ... và {len(self.classes)-5} classes khác")
        
        return all_samples
    
    # ========== BƯỚC 5: HANDLE IMBALANCE ==========
    
    def balance_dataset(self, all_samples, analysis):
        """Cân bằng dataset bằng oversampling"""
        print("\n" + "="*70)
        print("⚖️  BƯỚC 3: CÂN BẰNG DATASET")
        print("="*70)
        
        balanced_samples = {}
        
        for cls in self.classes:
            samples = all_samples[cls]
            current_count = len(samples)
            
            if current_count >= self.min_samples_per_class:
                # Enough samples
                balanced_samples[cls] = samples
            else:
                # Need oversampling
                needed = self.min_samples_per_class - current_count
                oversampled = random.choices(samples, k=needed)
                balanced_samples[cls] = samples + oversampled
                
                self.stats['classes_oversampled'].append((cls, current_count, self.min_samples_per_class))
                self.stats['augmented'] += needed
                
                print(f"   🔄 {cls}: {current_count} → {len(balanced_samples[cls])}")
        
        total_after = sum(len(s) for s in balanced_samples.values())
        print(f"\n✓ Cân bằng hoàn tất: {total_after} samples")
        
        return balanced_samples
    
    # ========== BƯỚC 6: STRATIFIED SPLIT ==========
    
    def stratified_split(self, balanced_samples, train_ratio=0.8):
        """Split train/val với stratification"""
        print("\n" + "="*70)
        print("📊 BƯỚC 4: STRATIFIED TRAIN/VAL SPLIT")
        print("="*70)
        
        train_samples = []
        val_samples = []
        
        for cls, samples in balanced_samples.items():
            random.shuffle(samples)
            
            split_idx = int(len(samples) * train_ratio)
            train_samples.extend(samples[:split_idx])
            val_samples.extend(samples[split_idx:])
        
        # Shuffle again
        random.shuffle(train_samples)
        random.shuffle(val_samples)
        
        print(f"✓ Split hoàn tất:")
        print(f"   - Train: {len(train_samples)} samples")
        print(f"   - Val: {len(val_samples)} samples")
        print(f"   - Ratio: {train_ratio:.1%} / {1-train_ratio:.1%}")
        
        return train_samples, val_samples
    
    # ========== BƯỚC 7: SAVE TO DISK ==========
    
    def save_samples(self, train_samples, val_samples):
        """Lưu samples ra disk"""
        print("\n" + "="*70)
        print("💾 BƯỚC 5: LƯU DỮ LIỆU")
        print("="*70)
        
        # Create folders
        for split in ['train', 'val']:
            (self.output_path / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.output_path / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
        # Save train
        print("\n📁 Lưu train set...")
        for i, sample in enumerate(train_samples):
            new_name = f"{sample['class']}_{i:05d}{sample['image_path'].suffix}"
            
            # Copy image
            shutil.copy(
                sample['image_path'],
                self.output_path / 'images' / 'train' / new_name
            )
            
            # Save label
            label_path = self.output_path / 'labels' / 'train' / f"{Path(new_name).stem}.txt"
            with open(label_path, 'w') as f:
                f.write(sample['label'])
        
        # Save val
        print("📁 Lưu val set...")
        for i, sample in enumerate(val_samples):
            new_name = f"{sample['class']}_{i:05d}{sample['image_path'].suffix}"
            
            shutil.copy(
                sample['image_path'],
                self.output_path / 'images' / 'val' / new_name
            )
            
            label_path = self.output_path / 'labels' / 'val' / f"{Path(new_name).stem}.txt"
            with open(label_path, 'w') as f:
                f.write(sample['label'])
        
        print(f"✓ Lưu hoàn tất!")
        
        self.stats['processed'] = len(train_samples) + len(val_samples)
    
    # ========== BƯỚC 8: CREATE CONFIG ==========
    
    def create_yaml_config(self):
        """Tạo YAML config"""
        config = {
            'path': str(self.output_path.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'nc': len(self.classes),
            'names': self.classes
        }
        
        yaml_path = self.output_path / 'data.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        return yaml_path
    
    # ========== MAIN RUN ==========
    
    def run(self):
        """Chạy toàn bộ pipeline"""
        print("="*70)
        print("🚀 PROFESSIONAL DATA PREPARATION PIPELINE")
        print("="*70)
        print(f"Input: {self.dataset_path}")
        print(f"Output: {self.output_path}")
        print(f"Min samples/class: {self.min_samples_per_class}")
        print("="*70)
        
        # Bước 1: Analyze
        analysis = self.analyze_dataset()
        
        # Bước 2: Collect valid samples
        all_samples = self.collect_valid_samples(analysis)
        
        # Bước 3: Balance dataset
        balanced_samples = self.balance_dataset(all_samples, analysis)
        
        # Bước 4: Stratified split
        train_samples, val_samples = self.stratified_split(balanced_samples)
        
        # Bước 5: Save
        self.save_samples(train_samples, val_samples)
        
        # Bước 6: Create config
        yaml_path = self.create_yaml_config()
        
        # Final report
        print("\n" + "="*70)
        print("🎉 HOÀN THÀNH!")
        print("="*70)
        
        print(f"\n📊 TỔNG KẾT:")
        print(f"   - Classes gốc: {len(self.stats['class_distribution'])}")
        print(f"   - Classes loại bỏ: {len(self.stats['classes_removed'])}")
        print(f"   - Classes cuối: {len(self.classes)}")
        print(f"   - Samples oversampled: {self.stats['augmented']}")
        print(f"   - Train: {len(train_samples)}")
        print(f"   - Val: {len(val_samples)}")
        print(f"   - Total: {self.stats['processed']}")
        
        if self.stats['classes_removed']:
            print(f"\n🔴 Classes đã loại bỏ:")
            for cls in self.stats['classes_removed'][:10]:
                print(f"   - {cls}")
        
        if self.stats['classes_oversampled']:
            print(f"\n🔄 Classes đã oversample:")
            for cls, before, after in self.stats['classes_oversampled'][:10]:
                print(f"   - {cls}: {before} → {after}")
        
        print(f"\n📁 Config: {yaml_path}")
        print("="*70)
        
        return yaml_path


# ============================================================
# CÁCH SỬ DỤNG
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROFESSIONAL DATA PREPARATION")
    print("="*70)
    
    DATASET_PATH = "/kaggle/input/animals-detection-images-dataset"
    OUTPUT_PATH = "yolo_dataset_pro"
    MIN_SAMPLES_PER_CLASS = 30  # Tối thiểu 30 ảnh/class
    
    print(f"\n⚙️  CẤU HÌNH:")
    print(f"   Input: {DATASET_PATH}")
    print(f"   Output: {OUTPUT_PATH}")
    print(f"   Min samples/class: {MIN_SAMPLES_PER_CLASS}")
    
    print(f"\n❓ Tiếp tục? (y/n): ", end="")
    confirm = input().strip().lower()
    
    if confirm != 'y':
        print("❌ Đã hủy.")
        exit(0)
    
    print("\n")
    prep = ProfessionalDataPreparation(DATASET_PATH, OUTPUT_PATH, MIN_SAMPLES_PER_CLASS)
    yaml_config = prep.run()
    
    print("\n" + "="*70)
    print("✅ THÀNH CÔNG!")
    print("="*70)
    print("📌 TIẾP THEO: Training với data đã cân bằng")
    print("="*70)
