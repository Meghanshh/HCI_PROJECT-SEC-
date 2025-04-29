import tensorflow as tf
from tensorflow.keras.applications.efficientnet_v2 import EfficientNetV2B0, preprocess_input
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

# Define constants
IMG_SIZE = (256, 256)
BATCH_SIZE = 32
NUM_CLASSES = 7
EPOCHS = 5  # Reduced epochs for quick training

def create_model():
    # Load the EfficientNetV2B0 model without top layers
    base_model = EfficientNetV2B0(weights='imagenet', include_top=False, input_shape=(*IMG_SIZE, 3))
    
    # Freeze all layers except the last few
    for layer in base_model.layers[:-10]:
        layer.trainable = False
    
    # Add custom layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dropout(0.5)(x)
    x = Dense(512, activation='relu')(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)
    
    # Create the model
    model = Model(inputs=base_model.input, outputs=predictions)
    
    return model

def main():
    # Create data generators
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )
    
    validation_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input
    )
    
    # Load and preprocess the data
    train_generator = train_datagen.flow_from_directory(
        'data/expw/train',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    validation_generator = validation_datagen.flow_from_directory(
        'data/expw/val',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )
    
    # Create and compile the model
    model = create_model()
    model.compile(
        optimizer=Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train the model
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=EPOCHS
    )
    
    # Save the model
    os.makedirs('../model', exist_ok=True)
    model.save('../model/emotion_model.h5')
    print("Model saved successfully!")

if __name__ == '__main__':
    main() 