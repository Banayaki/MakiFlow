from __future__ import absolute_import
import tensorflow as tf

from makiflow.layers.activation_converter import ActivationConverter
from makiflow.base import MakiLayer, MakiTensor
from makiflow.layers.sf_layer import SimpleForwardLayer


class InputLayer(MakiTensor):
    def __init__(self, input_shape, name):
        self.params = []
        self._name = str(name)
        self._input_shape = input_shape
        self.input = tf.placeholder(tf.float32, shape=input_shape, name=self._name)
        super().__init__(
            data_tensor=self.input,
            parent_layer=self,
            parent_tensor_names=None,
            previous_tensors={},
        )

    def get_shape(self):
        return self._input_shape

    def get_name(self):
        return self._name

    def get_params(self):
        return []

    def get_params_dict(self):
        return {}

    def to_dict(self):
        return {
            "name": self._name,
            "parent_tensor_names": [],
            'type': 'InputLayer',
            'params': {
                'name': self._name,
                'input_shape': self._input_shape
            }
        }


class ReshapeLayer(SimpleForwardLayer):
    def __init__(self, new_shape: list, name):
        super().__init__(name, [], {})
        self.new_shape = new_shape

    def _forward(self, X):
        return tf.reshape(tensor=X, shape=self.new_shape, name=self.get_name())

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'ReshapeLayer',
            'params': {
                'name': self.get_name(),
                'new_shape': self.new_shape
            }
        }

        
class MulByAlphaLayer(SimpleForwardLayer):
    def __init__(self, alpha, name):
        self.alpha = tf.constant(alpha)
        super().__init__(name,[],{})
    
    def _forward(self, X):
        return X * self.alpha
    
    def _training_forward(self, X):
        return self._forward(X)
    
    def to_dict(self):
        return {
            'type' : 'MulByAlphaLayer',
            'params' : {
                'name': self.get_name(),
                'alpha': self.alpha,
            }
        }


class SumLayer(MakiLayer):
    def __init__(self, name):
        super().__init__(name, [], {})

    def __call__(self, x: list):
        data = [one_tensor.get_data_tensor() for one_tensor in x]
        data = self._forward(data)

        parent_tensor_names = [one_tensor.get_name() for one_tensor in x]
        previous_tensors = {}
        for one_tensor in x:
            previous_tensors.update(one_tensor.get_previous_tensors())
            previous_tensors.update(one_tensor.get_self_pair())

        maki_tensor = MakiTensor(
            data_tensor=data,
            parent_layer=self,
            parent_tensor_names=parent_tensor_names,
            previous_tensors=previous_tensors,
        )
        return maki_tensor

    def _forward(self, X):
        return sum(X)

    def _training_forward(self, X):
        return self._forward(X)

    def to_dict(self):
        return {
            'type': 'SumLayer',
            'params': {
                'name': self._name,
            }
        }


class ConcatLayer(MakiLayer):
    def __init__(self, name, axis=3):
        super().__init__(name, [], {})
        self.axis = axis

    def __call__(self, x: list):
        data = [one_tensor.get_data_tensor() for one_tensor in x]
        data = self._forward(data)

        parent_tensor_names = [one_tensor.get_name() for one_tensor in x]
        previous_tensors = {}
        for one_tensor in x:
            previous_tensors.update(one_tensor.get_previous_tensors())
            previous_tensors.update(one_tensor.get_self_pair())

        maki_tensor = MakiTensor(
            data_tensor=data,
            parent_layer=self,
            parent_tensor_names=parent_tensor_names,
            previous_tensors=previous_tensors,
        )
        return maki_tensor

    def _forward(self, X):
        return tf.concat(values=X, axis=self.axis)

    def _training_forward(self, X):
        return self._forward(X)

    def to_dict(self):
        return {
            'type': 'ConcatLayer',
            'params': {
                'name': self._name,
                'axis': self.axis,
            }
        }


class ZeroPaddingLayer(SimpleForwardLayer):
    def __init__(self, padding, name):
        """
        This layer can add rows and columns of zeros
        at the top, bottom, left and right side of an image tensor.

        Parameters
        ----------
        padding : list
            List the number of additional rows and columns in the appropriate directions. 
            For example like [ [top,bottom], [left,right] ]
            
        """
        assert(len(padding) == 2)
        self.padding = [ [0,0], padding[0], padding[1], [0,0]]
        super().__init__(name,[],{})
    
    def _forward(self, X):
        return tf.pad(
            tensor=X,
            paddings=self.padding,
            mode="CONSTANT",
        )

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'ZeroPaddingLayer',
            'params': {
                'name': self._name,
                'padding': self.padding,
            }
        }


class GlobalMaxPoolLayer(SimpleForwardLayer):
    def __init__(self, name):
        super().__init__(name, [], {})
    
    def _forward(self, X):
        assert(len(X.shape) == 4)
        return tf.reduce_max(X, axis=[1,2])

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'GlobalMaxPoolLayer',
            'params': {
                'name': self._name,
            }
        }


class GlobalAvgPoolLayer(SimpleForwardLayer):
    def __init__(self, name):
        super().__init__(name, [], {})
    
    def _forward(self, X):
        assert(len(X.shape) == 4)
        return tf.reduce_mean(X, axis=[1, 2])
    
    def _training_forward(self, x):
        return self._forward(x)
    
    def to_dict(self):
        return {
            'type' : 'GlobalAvgPoolLayer',
            'params' : {
                'name' : self._name,
            }
        }


class MaxPoolLayer(SimpleForwardLayer):
    def __init__(self, name, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME'):
        super().__init__(name, [], {})
        self.ksize = ksize
        self.strides = strides
        self.padding = padding

    def _forward(self, X):
        return tf.nn.max_pool(
            X,
            ksize=self.ksize,
            strides=self.strides,
            padding=self.padding
        )

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'MaxPoolLayer',
            'params': {
                'name': self._name,
                'ksize': self.ksize,
                'strides': self.strides,
                'padding': self.padding
            }
        }


class AvgPoolLayer(SimpleForwardLayer):
    def __init__(self, name, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME'):
        super().__init__(name, [], {})
        self.ksize = ksize
        self.strides = strides
        self.padding = padding

    def _forward(self, X):
        return tf.nn.avg_pool(
            X,
            ksize=self.ksize,
            strides=self.strides,
            padding=self.padding
        )

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'AvgPoolLayer',
            'params': {
                'name': self._name,
                'ksize': self.ksize,
                'strides': self.strides,
                'padding': self.padding
            }
        }


class UpSamplingLayer(SimpleForwardLayer):
    def __init__(self, name, size=(2, 2)):
        super().__init__(name, [], {})
        self.size = size

    def _forward(self, X):
        t_shape = X.get_shape()
        im_size = (t_shape[1]*self.size[0], t_shape[2]*self.size[1])
        return tf.image.resize_nearest_neighbor(
            X,
            im_size
        )

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'UpSamplingLayer',
            'params': {
                'name': self._name,
                'size': self.size
            }
        }


class ActivationLayer(SimpleForwardLayer):
    def __init__(self, name, activation=tf.nn.relu):
        super().__init__(name, [], {})
        if activation is None:
            raise Exception("Activation can't None")
        self.f = activation

    def _forward(self, X):
        return self.f(X)

    def _training_forward(self, X):
        return self.f(X)

    def to_dict(self):
        return {
            'type': 'ActivationLayer',
            'params': {
                'name': self._name,
                'activation': ActivationConverter.activation_to_str(self.f)
            }
        }


class FlattenLayer(SimpleForwardLayer):
    def __init__(self, name):
        super().__init__(name, [], {})

    def _forward(self, X):
        return tf.contrib.layers.flatten(X)

    def _training_forward(self, x):
        return self._forward(x)

    def to_dict(self):
        return {
            'type': 'FlattenLayer',
            'params': {
                'name': self._name
            }
        }


class DropoutLayer(SimpleForwardLayer):
    def __init__(self, name, p_keep=0.9):
        super().__init__(name, [], {})
        self._p_keep = p_keep

    def _forward(self, X):
        return X

    def _training_forward(self, X):
        return tf.nn.dropout(X, self._p_keep)

    def to_dict(self):
        return {
            'type': 'DropoutLayer',
            'params': {
                'name': self._name,
                'p_keep': self._p_keep
            }
        }

class Bilinear_resize(SimpleForwardLayer):
    def __init__(self, new_shape: list, name, align_corners=False, half_pixel_centers=False):
        assert (len(new_shape) == 2)
        self.new_shape = new_shape
        self.name = name
        self.align_corners = align_corners
        self.half_pixel_centers = half_pixel_centers

        super().__init__(name,[],{})

    def _forward(self,X):
        return tf.image.resize_bilinear(X,
                new_shape,
                align_corners=self.align_corners,
                name=self.name,
                half_pixel_centers=self.half_pixel_centers,
        )
    
    def _training_forward(self,X):
        return self._forward(X)
    
    def to_dict(self):
        return {
            'type': 'BilinearResizeLayer',
            'params':{
                'name': self.name,
                'new_shape': self.new_shape,
            }
        }

