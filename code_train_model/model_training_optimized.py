"""
========================================
FILE 2: model_training_optimized.py
========================================
Training tối ưu cho BALANCED DATASET
Data: 28,184 samples, 80 classes (balanced)
Imbalance: 73:1 (tốt hơn nhiều so với 321:1)
Mục tiêu: mAP 0.78-0.82
"""

from ultralytics import YOLO
import torch
from pathlib import Path
import yaml
import time
from datetime import datetime

class OptimizedTrainer:
    def __init__(self, yaml_config_path, model_size='n'):
        """
        model_size: 
            'n' = nano (KHUYẾN NGHỊ - phù hợp với 80 classes balanced)
            's' = small (nếu muốn accuracy cao hơn)
        """
        self.yaml_config = yaml_config_path
        self.model_size = model_size
        self.model = None
        
        print("="*70)
        print("🔧 KIỂM TRA PHẦN CỨNG")
        print("="*70)
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥️  Device: {self.device.upper()}")
        
        if self.device == 'cuda':
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"🎮 GPU: {gpu_name}")
            print(f"💾 VRAM: {vram:.2f} GB")
            
            print(f"\n💡 CẤU HÌNH CHO BALANCED DATASET:")
            print(f"   📊 22,518 train + 5,666 val")
            print(f"   🎯 80 classes (balanced)")
            print(f"   ⚖️  Imbalance: 73:1 (tốt!)")
            print(f"\n   KHUYẾN NGHỊ:")
            print(f"   - Model: 'n' (nano - đủ cho balanced data)")
            print(f"   - Epochs: 100 (data tốt cần nhiều epochs)")
            print(f"   - Batch: 32-40")
            print(f"   - LR: 0.002 (cao hơn cho convergence nhanh)")
            print(f"   - Augmentation: VỪA PHẢI (data đã balance)")
            
            if vram >= 15:
                print(f"\n   ✅ Batch 40-48 (optimal)")
            elif vram >= 12:
                print(f"\n   ✅ Batch 32-40")
            else:
                print(f"\n   ⚠️  Batch 24-32")
        
        print("="*70)
    
    def load_model(self):
        """Load model"""
        model_name = f'yolov8{self.model_size}.pt'
        
        print(f"\n📦 Đang tải: {model_name}")
        
        try:
            self.model = YOLO(model_name)
            print(f"✓ Loaded!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            raise
        
        try:
            with open(self.yaml_config, 'r') as f:
                config = yaml.safe_load(f)
            
            print(f"\n📊 Dataset Info:")
            print(f"   - Path: {config['path']}")
            print(f"   - Classes: {config['nc']}")
            print(f"   - Names: {', '.join(config['names'][:5])} ...")
            print(f"\n   ✨ BALANCED DATA = BETTER TRAINING!")
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            raise
        
        return self.model
    
    def train(self, epochs=100, imgsz=640, batch=32, patience=40, save_period=5):
        """
        Training tối ưu cho BALANCED dataset
        """
        
        print("\n" + "="*70)
        print("🚀 TRAINING (OPTIMIZED FOR BALANCED DATA)")
        print("="*70)
        
        print(f"\n⚙️  CONFIG:")
        print(f"   Model: YOLOv8{self.model_size}")
        print(f"   Epochs: {epochs}")
        print(f"   Image: {imgsz}")
        print(f"   Batch: {batch}")
        print(f"   Patience: {patience}")
        print(f"   Optimizer: SGD (better than AdamW for balanced data)")
        print(f"   LR: 0.002 (higher for faster convergence)")
        
        if self.device == 'cuda':
            est_time = f"{epochs * 0.07:.1f}-{epochs * 0.09:.1f}h"
        else:
            est_time = "N/A"
        
        print(f"\n⏱️  Time: {est_time}")
        
        print(f"\n🎯 EXPECTED RESULTS:")
        print(f"   Baseline (imbalanced):  mAP50 = 0.69")
        print(f"   Target (balanced):      mAP50 = 0.78-0.82")
        print(f"   Improvement:            +13-19%")
        print(f"\n   Why better:")
        print(f"   ✅ Balanced data (73:1 vs 321:1)")
        print(f"   ✅ Stratified split")
        print(f"   ✅ Model 'n' sufficient (no overfit)")
        print(f"   ✅ SGD optimizer (stable)")
        print(f"   ✅ 100 epochs (enough for convergence)")
        
        print(f"\n❓ Start? (y/n): ", end="")
        confirm = input().strip().lower()
        
        if confirm != 'y':
            print("❌ Cancelled.")
            return None, None
        
        print("\n" + "="*70)
        print("🏃 TRAINING...")
        print("="*70 + "\n")
        
        start_time = time.time()
        
        try:
            results = self.model.train(
                data=self.yaml_config,
                epochs=epochs,
                imgsz=imgsz,
                batch=batch,
                device=self.device,
                
                # Data loading
                workers=8,
                cache=False,
                
                # Early stopping
                patience=patience,
                
                # Save
                save=True,
                save_period=save_period,
                project='runs/detect',
                name='animal_balanced',
                exist_ok=True,
                
                # Model
                pretrained=True,
                optimizer='SGD',      # SGD tốt hơn cho balanced data
                verbose=True,
                seed=42,
                deterministic=False,
                single_cls=False,
                
                # Training
                rect=False,
                cos_lr=True,          # Cosine LR
                close_mosaic=15,      # Tắt mosaic sau epoch 85
                resume=False,
                amp=True,
                fraction=1.0,
                profile=False,
                
                # AUGMENTATION - VỪA PHẢI (data đã balanced)
                hsv_h=0.015,
                hsv_s=0.7,
                hsv_v=0.4,
                degrees=8.0,          # Giảm rotation
                translate=0.1,        # Giảm translation
                scale=0.7,            # Giảm scale
                shear=2.0,            # Giảm shear
                perspective=0.0001,   # Giảm perspective
                flipud=0.0,
                fliplr=0.5,
                mosaic=1.0,
                mixup=0.1,            # Giảm mixup
                copy_paste=0.05,      # Giảm copy-paste
                
                # Validation
                val=True,
                plots=True,
                save_json=False,
                save_hybrid=False,
                conf=None,
                iou=0.7,
                max_det=300,
                half=False,
                dnn=False,
                
                # OPTIMIZER - TUNED FOR SGD
                lr0=0.002,            # LR cao hơn (0.002 vs 0.001)
                lrf=0.0001,           # Final LR
                momentum=0.937,
                weight_decay=0.0005,
                warmup_epochs=3.0,
                warmup_momentum=0.8,
                warmup_bias_lr=0.1,
                
                # LOSS - Balanced weights cho 80 classes
                box=7.5,
                cls=0.5,              # Giảm cls (data balanced)
                dfl=1.5,
                pose=12.0,
                kobj=1.0,
                label_smoothing=0.0,  # Tắt (data tốt)
                
                # Batch
                nbs=64,
                overlap_mask=True,
                mask_ratio=4,
                dropout=0.0,
            )
            
            end_time = time.time()
            hours = int((end_time - start_time) // 3600)
            minutes = int(((end_time - start_time) % 3600) // 60)
            
            print("\n" + "="*70)
            print("🎉 TRAINING DONE!")
            print("="*70)
            print(f"⏱️  Time: {hours}h {minutes}m")
            
            best_path = Path('runs/detect/animal_balanced/weights/best.pt')
            last_path = Path('runs/detect/animal_balanced/weights/last.pt')
            results_path = Path('runs/detect/animal_balanced')
            
            print(f"\n📁 SAVED:")
            print(f"   - Best: {best_path}")
            print(f"   - Last: {last_path}")
            print(f"   - Plots: {results_path}")
            
            return results, best_path
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user")
            last_path = Path('runs/detect/animal_balanced/weights/last.pt')
            return None, last_path if last_path.exists() else None
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            
            if "memory" in str(e).lower():
                print("\n💡 FIX:")
                print("   - Reduce batch: 24 or 16")
                print("   - Reduce imgsz: 512")
            
            raise
    
    def validate(self, model_path=None):
        """Validation"""
        if model_path:
            print(f"\n📦 Load: {model_path}")
            self.model = YOLO(model_path)
        
        print("\n📊 Validating...")
        
        try:
            metrics = self.model.val(data=self.yaml_config)
            
            print("\n" + "="*70)
            print("📈 FINAL RESULTS")
            print("="*70)
            print(f"📊 mAP50:     {metrics.box.map50:.4f}")
            print(f"📊 mAP50-95:  {metrics.box.map:.4f}")
            print(f"🎯 Precision: {metrics.box.mp:.4f}")
            print(f"🎯 Recall:    {metrics.box.mr:.4f}")
            
            # Compare
            baseline = 0.6925  # From previous run
            improvement = ((metrics.box.map50 - baseline) / baseline) * 100
            
            print(f"\n📊 COMPARISON:")
            print(f"   Imbalanced data:  {baseline:.4f}")
            print(f"   Balanced data:    {metrics.box.map50:.4f}")
            
            if improvement > 0:
                print(f"   Improvement:      +{improvement:.1f}% 🎉")
            else:
                print(f"   Change:           {improvement:.1f}%")
            
            print(f"\n💬 EVALUATION:")
            if metrics.box.map50 >= 0.80:
                print("   🌟 EXCELLENT! Target achieved!")
            elif metrics.box.map50 >= 0.75:
                print("   ✅ VERY GOOD! Close to target.")
                print("   💡 To reach 0.80+:")
                print("      - Train +20 epochs")
                print("      - Try model 's'")
            elif metrics.box.map50 >= 0.72:
                print("   ✅ GOOD! Better than baseline.")
                print("   💡 To improve:")
                print("      - Epochs 120-150")
                print("      - Model 's'")
            else:
                print("   ⚠️  Check training logs")
            
            print("="*70)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*70)
    print("TRAINING WITH BALANCED DATASET")
    print("="*70)
    print(f"Dataset: 28,184 samples (balanced)")
    print(f"Train: 22,518 | Val: 5,666")
    print(f"Imbalance: 73:1 (was 321:1)")
    print(f"Target: mAP50 = 0.78-0.82")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # ========================================
    # CONFIG - OPTIMIZED FOR BALANCED DATA
    # ========================================
    
    YAML_CONFIG = "/kaggle/working/yolo_dataset_pro/data.yaml"
    
    MODEL_SIZE = 'n'  # Nano sufficient for balanced data
    
    # OPTIMAL CONFIG
    EPOCHS = 100      # Enough for convergence
    IMAGE_SIZE = 640
    BATCH_SIZE = 32   # 40 if VRAM >= 15GB
    
    PATIENCE = 40     # Higher (data good, need time)
    SAVE_PERIOD = 5
    
    # ========================================
    
    if not Path(YAML_CONFIG).exists():
        print(f"\n❌ Not found: '{YAML_CONFIG}'")
        exit(1)
    
    print(f"\n⚙️  CONFIG:")
    print(f"   Model: YOLOv8{MODEL_SIZE}")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Image: {IMAGE_SIZE}")
    print(f"   Batch: {BATCH_SIZE}")
    print(f"   Time: ~{EPOCHS * 0.08:.1f}h")
    
    print(f"\n🎯 WHY THIS WORKS:")
    print(f"   ✅ Balanced data (73:1 vs 321:1)")
    print(f"   ✅ Model 'n' (no overfit)")
    print(f"   ✅ SGD (stable for balanced)")
    print(f"   ✅ 100 epochs (full convergence)")
    print(f"   ✅ Moderate augmentation")
    print(f"   → Expected: mAP 0.78-0.82")
    
    # Init
    trainer = OptimizedTrainer(
        yaml_config_path=YAML_CONFIG,
        model_size=MODEL_SIZE
    )
    
    # Load
    print("\n" + "="*70)
    print("📥 LOAD MODEL")
    print("="*70)
    trainer.load_model()
    
    # Train
    results, best_model = trainer.train(
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        patience=PATIENCE,
        save_period=SAVE_PERIOD
    )
    
    if best_model:
        # Validate
        print("\n" + "="*70)
        print("🎯 VALIDATION")
        print("="*70)
        trainer.validate(best_model)
        
        print("\n" + "="*70)
        print("✅ COMPLETE!")
        print("="*70)
        print(f"📁 Model: {best_model}")
        print(f"\n📌 NEXT:")
        print(f"   Test inference on real images")
        print("="*70)
        print(f"End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
