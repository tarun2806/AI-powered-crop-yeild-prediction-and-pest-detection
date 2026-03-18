import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import os

# Set up data paths
# Expected structure: static/images/{pest_name}/*.jpg
train_dir = 'static/images'  
validation_dir = 'static/val_images'

class PestTransferEngine:
    def __init__(self, num_classes=5, input_shape=(224, 224, 3)):
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.model = self._build_model()

    def _build_model(self):
        """Constructs MobileNetV2 Transfer Learning Architecture."""
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=self.input_shape)
        
        # Freeze the base model to preserve ImageNet features
        base_model.trainable = False
        
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        model = Model(inputs=base_model.input, outputs=predictions)
        model.compile(optimizer='adam', 
                      loss='categorical_crossentropy', 
                      metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])
        return model

    def train(self, epochs=15, batch_size=32):
        """Standard production training pipeline with augmentation."""
        train_datagen = ImageDataGenerator(
            rescale=1.0/255,
            rotation_range=30,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        val_datagen = ImageDataGenerator(rescale=1.0/255)

        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical'
        )

        val_generator = val_datagen.flow_from_directory(
            validation_dir,
            target_size=self.input_shape[:2],
            batch_size=batch_size,
            class_mode='categorical'
        )

        # Callbacks for production reliability
        callbacks = [
            ModelCheckpoint('models/best_pest_model.h5', save_best_only=True, monitor='val_accuracy'),
            EarlyStopping(patience=5, restore_best_weights=True)
        ]

        print("🚀 Starting Transfer Learning Training...")
        history = self.model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=epochs,
            callbacks=callbacks
        )
        
        print(f"✅ Training Complete. Best model saved to models/best_pest_model.h5")
        return history

if __name__ == "__main__":
    if not os.path.exists('models'):
        os.makedirs('models')
        
    engine = PestTransferEngine()
    # Note: Requires actual images in static/images folder to run
    try:
        engine.train()
    except Exception as e:
        print(f"⚠️ Training skipped: {str(e)}")
        print("💡 Ensure your dataset is in 'static/images' with subfolders for each pest.")
