import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
from onnx2keras import onnx_to_keras, check_torch_keras_error
import random
import onnx


class LayerTest(nn.Module):
    def __init__(self, out, eps, momentum):
        super(LayerTest, self).__init__()
        self.in2d = nn.InstanceNorm2d(out, eps=eps, momentum=momentum)

    def forward(self, x):
        x = self.in2d(x)
        return x


if __name__ == '__main__':
    max_error = 0
    for i in range(10):
        inp_size = np.random.randint(10, 100)

        model = LayerTest(inp_size, random.random(), random.random())
        model.eval()

        input_np = np.random.uniform(0, 1, (1, inp_size, 224, 224))
        input_var = Variable(torch.FloatTensor(input_np))

        torch.onnx.export(model, input_var, "_tmpnet.onnx", verbose=True, input_names=['test_in'],
                          output_names=['test_out'])

        onnx_model = onnx.load('_tmpnet.onnx')
        k_model = onnx_to_keras(onnx_model, ['test_in'])

        error = check_torch_keras_error(model, k_model, input_np)
        print('Error:', error)

        if max_error < error:
            max_error = error

    print('Max error: {0}'.format(max_error))