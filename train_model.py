# -*- coding: utf-8 -*-
"""
Chess AI Model Training Script
Train neural network to evaluate chess positions for ESP32 deployment
"""

import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
import os


class ChessModelTrainer:
    def __init__(self, data_file, model_dir='models'):
        self.data_file = data_file
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

    def load_data(self, max_samples=None):
        """加载训练数据"""
        print(f"正在加载数据: {self.data_file}")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if max_samples:
            data = data[:max_samples]

        print(f"加载了 {len(data)} 个样本")

        # 提取特征和标签
        X = np.array([sample['board_state'] for sample in data], dtype=np.float32)
        y_eval = np.array([sample['eval'] for sample in data], dtype=np.float32)
        y_result = np.array([sample['result'] for sample in data], dtype=np.float32)

        return X, y_eval, y_result

    def build_model(self):
        """
        构建轻量级CNN模型（适合ESP32部署）
        输入: 8x8x12 棋盘状态
        输出: 评估值 (-1到1之间)
        """
        inputs = keras.Input(shape=(8, 8, 12), name='board_input')

        # 卷积层 - 提取棋盘特征
        x = layers.Conv2D(32, 3, activation='relu', padding='same')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D(2)(x)

        # 更深层的特征提取
        x = layers.Conv2D(64, 3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Conv2D(128, 3, activation='relu', padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.GlobalAveragePooling2D()(x)

        # 全连接层
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.2)(x)

        # 输出层 - 评估值 (-1到1)
        outputs = layers.Dense(1, activation='tanh')(x)

        model = keras.Model(inputs=inputs, outputs=outputs, name='chess_ai')

        return model

    def train(self, epochs=50, batch_size=64, max_samples=50000):
        """训练模型"""
        # 加载数据
        X, y_eval, y_result = self.load_data(max_samples)

        # 使用评估值作为训练目标（如果有），否则使用结果
        y = np.where(np.abs(y_eval) > 0.01, y_eval, y_result)

        # 归一化评估值到 -1 到 1
        y = np.clip(y / 10.0, -1, 1)

        # 划分训练集和验证集
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"训练集: {X_train.shape[0]} 样本")
        print(f"验证集: {X_val.shape[0]} 样本")

        # 构建模型
        model = self.build_model()

        # 编译模型
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        # 打印模型结构
        model.summary()

        # 训练回调
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=os.path.join(self.model_dir, 'best_model.keras'),
                monitor='val_loss',
                save_best_only=True
            )
        ]

        # 训练模型
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )

        # 保存最终模型
        model_path = os.path.join(self.model_dir, 'chess_ai_model.keras')
        model.save(model_path)
        print(f"\n模型已保存到: {model_path}")

        # 评估模型
        val_loss, val_mae = model.evaluate(X_val, y_val, verbose=0)
        print(f"验证集损失: {val_loss:.4f}")
        print(f"验证集平均绝对误差: {val_mae:.4f}")

        return model, history

    def convert_to_tflite(self, model_path, quantize=True):
        """将模型转换为TensorFlow Lite格式（适合ESP32）"""
        print(f"\n正在转换模型为TFLite格式...")

        # 加载模型
        model = keras.models.load_model(model_path)

        # 转换为TFLite
        converter = tf.lite.TFLiteConverter.from_keras_model(model)

        # 不使用量化优化，保持纯float32格式以兼容TFLite Micro
        # TFLite Micro不支持混合精度模型
        converter.optimizations = []

        tflite_model = converter.convert()

        # 保存TFLite模型
        tflite_path = os.path.join(self.model_dir, 'chess_ai_model.tflite')
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)

        print(f"TFLite模型已保存到: {tflite_path}")

        # 打印模型大小
        original_size = os.path.getsize(model_path) / (1024 * 1024)
        tflite_size = os.path.getsize(tflite_path) / (1024 * 1024)
        print(f"原始模型大小: {original_size:.2f} MB")
        print(f"TFLite模型大小: {tflite_size:.2f} MB")
        print(f"压缩率: {(1 - tflite_size/original_size)*100:.1f}%")

        # 转换为C数组头文件（ESP32使用）
        self.tflite_to_c_header(tflite_path)

        return tflite_path

    def tflite_to_c_header(self, tflite_path):
        """将TFLite模型转换为C数组头文件"""
        import binascii

        with open(tflite_path, 'rb') as f:
            model_data = f.read()

        hex_data = ', '.join(f'0x{b:02x}' for b in model_data)

        header_content = f"""// Chess AI Model for ESP32
// Auto-generated TFLite model
// Size: {len(model_data)} bytes

#ifndef CHESS_MODEL_H
#define CHESS_MODEL_H

const unsigned char chess_model_tflite[] = {{
    {hex_data}
}};

const int chess_model_tflite_len = {len(model_data)};

#endif // CHESS_MODEL_H
"""

        header_path = os.path.join(self.model_dir, 'chess_model.h')
        with open(header_path, 'w') as f:
            f.write(header_content)

        print(f"C头文件已保存到: {header_path}")


def main():
    # 配置
    data_file = "chess_training_data_with_eval.json"
    model_dir = "models"

    print("=" * 60)
    print("国际象棋AI模型训练")
    print("=" * 60)

    # 创建训练器
    trainer = ChessModelTrainer(data_file, model_dir)

    # 训练模型
    print("\n开始训练...")
    model, history = trainer.train(
        epochs=30,
        batch_size=128,
        max_samples=50000  # 使用5万个样本训练
    )

    # 转换为TFLite
    model_path = os.path.join(model_dir, 'chess_ai_model.keras')
    trainer.convert_to_tflite(model_path, quantize=True)

    print("\n" + "=" * 60)
    print("训练完成！模型已准备好部署到ESP32")
    print("=" * 60)


if __name__ == "__main__":
    main()