import tensorflow as tf
import numpy as np

# Create a simple model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(28, 28, 1)),
    tf.keras.layers.Conv2D(32, 3, activation='relu'),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(10, activation='softmax')
])

# Compile the model
model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Create test data
x_test = np.random.random((10, 28, 28, 1))
y_test = np.eye(10)[np.random.randint(0, 10, 10)]

# Save both model and test data
model.save('tf_model.h5')
np.savez('test_data.npz', x_test=x_test, y_test=y_test)
