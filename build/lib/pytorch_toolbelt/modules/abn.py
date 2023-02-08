import torch
import torch.nn as nn
import torch.nn.functional as functional
from pytorch_toolbelt.modules.activations import (
    ACT_LEAKY_RELU,
    ACT_NONE,
    ACT_HARD_SIGMOID,
    ACT_HARD_SWISH,
    ACT_SWISH,
    ACT_SELU,
    ACT_ELU,
    ACT_RELU6,
    ACT_RELU,
    hard_swish,
    hard_sigmoid,
    swish,
)

__all__ = ["ABN"]


class ABN(nn.Module):
    """Activated Batch Normalization
    This gathers a `BatchNorm2d` and an activation function in a single module
    """

    def __init__(
        self,
        num_features,
        eps=1e-5,
        momentum=0.1,
        affine=True,
        activation="leaky_relu",
        slope=0.01,
    ):
        """Create an Activated Batch Normalization module
        Parameters
        ----------
        num_features : int
            Number of feature channels in the input and output.
        eps : float
            Small constant to prevent numerical issues.
        momentum : float
            Momentum factor applied to compute running statistics as.
        affine : bool
            If `True` apply learned scale and shift transformation after normalization.
        activation : str
            Name of the activation functions, one of: `leaky_relu`, `elu` or `none`.
        slope : float
            Negative slope for the `leaky_relu` activation.
        """
        super(ABN, self).__init__()
        self.num_features = num_features
        self.affine = affine
        self.eps = eps
        self.momentum = momentum
        self.activation = activation
        self.slope = slope
        if self.affine:
            self.weight = nn.Parameter(torch.ones(num_features))
            self.bias = nn.Parameter(torch.zeros(num_features))
        else:
            self.register_parameter("weight", None)
            self.register_parameter("bias", None)
        self.register_buffer("running_mean", torch.zeros(num_features))
        self.register_buffer("running_var", torch.ones(num_features))
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.zeros_(self.running_mean)
        nn.init.ones_(self.running_var)
        if self.affine:
            nn.init.ones_(self.weight)
            nn.init.zeros_(self.bias)

    def forward(self, x):
        x = functional.batch_norm(
            x,
            self.running_mean,
            self.running_var,
            self.weight,
            self.bias,
            self.training,
            self.momentum,
            self.eps,
        )

        if self.activation == ACT_RELU:
            return functional.relu(x, inplace=True)
        elif self.activation == ACT_RELU6:
            return functional.relu6(x, inplace=True)
        elif self.activation == ACT_LEAKY_RELU:
            return functional.leaky_relu(x, negative_slope=self.slope, inplace=True)
        elif self.activation == ACT_ELU:
            return functional.elu(x, inplace=True)
        elif self.activation == ACT_SELU:
            return functional.selu(x, inplace=True)
        elif self.activation == ACT_SWISH:
            return swish(x)
        elif self.activation == ACT_HARD_SWISH:
            return hard_swish(x, inplace=True)
        elif self.activation == ACT_HARD_SIGMOID:
            return hard_sigmoid(x, inplace=True)
        elif self.activation == ACT_NONE:
            return x
        else:
            raise KeyError(self.activation)

    def __repr__(self):
        rep = (
            "{name}({num_features}, eps={eps}, momentum={momentum},"
            " affine={affine}, activation={activation}"
        )
        if self.activation == "leaky_relu":
            rep += ", slope={slope})"
        else:
            rep += ")"
        return rep.format(name=self.__class__.__name__, **self.__dict__)
