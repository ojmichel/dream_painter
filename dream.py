import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

import IPython.display as display
import PIL.Image


# img = PIL.Image.open('test.jpeg')
base_model = tf.keras.applications.InceptionV3(include_top=False, weights='imagenet')

class DeepDream(tf.Module):
    def __init__(self, model):
        self.model = model

    @tf.function(input_signature=(
            tf.TensorSpec(shape=[None, None, 3], dtype=tf.float32),
            tf.TensorSpec(shape=[], dtype=tf.int32),
            tf.TensorSpec(shape=[], dtype=tf.float32),)
    )
    def __call__(self, img, steps, step_size):
        print("Tracing")
        loss = tf.constant(0.0)

        for n in tf.range(steps):
            print(n)
            with tf.GradientTape() as tape:
                tape.watch(img)
                loss = calc_loss(img, self.model)
            gradients = tape.gradient(loss, img)

            # Normalize the gradients.
            gradients /= tf.math.reduce_std(gradients) + 1e-8

            # In gradient ascent, the "loss" is maximized so that the input image increasingly "excites" the layers.
            # You can update the image by directly adding the gradients (because they're the same shape!)
            img = img + gradients * step_size
            img = tf.clip_by_value(img, -1, 1)

        return loss, img

def show(img):
    display.display(PIL.Image.fromarray(np.array(img)))
def downsize(img,max_dim=None):
    if max_dim:
        img.thumbnail((max_dim, max_dim))
    return np.array(img)
def deprocess(img):
    img = 255*(img + 1.0)/2.0
    return tf.cast(img, tf.uint8)

def dd_model(names):
    layers = [base_model.get_layer(name).output for name in names]
    return tf.keras.Model(inputs=base_model.input, outputs=layers)

def calc_loss(img,model):
    img_batch = tf.expand_dims(img,axis=0)
    layer_activations = model(img_batch)
    if len(layer_activations) == 1:
        layer_activations = [layer_activations]
    losses = []
    for act in layer_activations:
        loss = tf.math.reduce_mean(act)
        losses.append(loss)

    return tf.reduce_sum(losses)

def run_deep_dream_simple(deepdream,img, steps=100, step_size=0.01):
  # Convert from uint8 to the range expected by the model.
    img = tf.keras.applications.inception_v3.preprocess_input(img)
    img = tf.convert_to_tensor(img)
    step_size = tf.convert_to_tensor(step_size)
    steps_remaining = steps
    step = 0
    while steps_remaining:
        if steps_remaining>100:
            run_steps = tf.constant(100)
        else:
            run_steps = tf.constant(steps_remaining)
        steps_remaining -= run_steps
        step += run_steps

        loss, img = deepdream(img, run_steps, tf.constant(step_size))

        display.clear_output(wait=True)
        show(deprocess(img))
        print ("Step {}, loss {}".format(step, loss))


    result = deprocess(img)
    display.clear_output(wait=True)
    show(result)

    return result
def run(img,names,steps,step_size):
    deepdream = DeepDream(dd_model(names))
    input_img = downsize(img)
    dream_img = run_deep_dream_simple(deepdream,input_img,steps=steps,step_size=step_size)
    return dream_img

# a = run(['mixed10'],100,0.01)
# show(a)