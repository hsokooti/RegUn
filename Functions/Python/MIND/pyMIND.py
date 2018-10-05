import numpy as np
from Functions.Python.MIND.search_region import *
from scipy.ndimage.filters import convolve

def MIND(image, r=0, sigma=0.5, dimension=3):
    if dimension is not 3:
        raise ValueError('MIND is only implemented for dimenstion = 3, but the dimension is set to {}'.format(dimension))
    shift_values = search_region(r)
    shift_values_r0 = search_region(0)
    Dp = np.zeros(np.r_[np.shape(image), len(shift_values_r0[0])], dtype=np.float32)
    #  Calculating Gaussian weighted patch SSD using convolution
    for i in range(len(shift_values_r0[0])):
        Dp[:, :, :, i] = filter_image3(np.square(image - shift_image3(image,
                         [shift_values_r0[0][i], shift_values_r0[1][i], shift_values_r0[2][i]])), sigma, r)
    #  Variance measure for Gaussian function (see Section 3.2)
    V = np.mean(Dp, dimension)
    # the following can improve robustness (by limiting V to be in smaller range)
    val1 = [np.sqrt(np.mean(V)), np.square(np.mean(V))]
    V = np.minimum(np.maximum(V, min(val1)), max(val1))

    I1 = np.zeros(np.r_[np.shape(image), len(shift_values_r0[0])], dtype=np.float32)
    for i in range(len(shift_values_r0[0])):
        I1[:, :, :, i] = np.exp(-Dp[:, :, :, i]/V)

    # normalise descriptors to a maximum of 1 (only within six-neighbourhood)
    max1 = np.max(I1, axis=dimension)

    mind = np.zeros(np.r_[np.shape(image), len(shift_values_r0[0])], dtype=np.float32)
    if r == 0:
        # if six-neighbourhood is used, all patch distances are already calculated
        for i in range(len(shift_values_r0[0])):
            mind[:, :, :, i] = I1[:, :, :, i]/max1
    else:
        for i in range(len(shift_values[0])):
            mind[:, :, :, i] = np.exp(-filter_image3(np.square(image - shift_image3(image,
                                [shift_values[0][i], shift_values[1][i], shift_values[2][i]])), sigma, r) / V) / max1
    return mind


def shift_image3(image, shift_values):
    shift_image = np.zeros(np.shape(image), dtype=np.float32)
    low_im = np.empty(3, dtype=np.int)
    high_im = np.empty(3, dtype=np.int)
    low_shift = np.empty(3, dtype=np.int)
    high_shift = np.empty(3, dtype=np.int)
    for dim in range(3):
        low_im[dim] = max(0, shift_values[dim])
        low_shift[dim] = max(0, -shift_values[dim])
        high_im[dim] = min(np.shape(image)[dim], np.shape(image)[dim] + shift_values[dim])
        high_shift[dim] = min(np.shape(image)[dim], np.shape(image)[dim] - shift_values[dim])
    shift_image[low_shift[0]:high_shift[0], low_shift[1]:high_shift[1], low_shift[2]:high_shift[2]] = \
    image[low_im[0]:high_im[0], low_im[1]:high_im[1], low_im[2]:high_im[2]]
    return shift_image

def filter_image3(image, sigma=0.5, r=0, mode='constant'):
    h = gauss1D(shape=np.ceil(sigma*3/2)*2+1)
    if r == 'sparse83':
        hoi = 1
    else:
        filter_out = convolve(image, np.reshape(h, [-1, 1, 1]), mode=mode)
        filter_out = convolve(filter_out, np.reshape(h, [1, -1, 1]), mode=mode)
        filter_out = convolve(filter_out, np.reshape(h, [1, 1, -1]), mode=mode)
    return filter_out.astype(np.float32)

def gauss2D(shape=(3,3),sigma=0.5):
    m,n = [(ss-1.)/2. for ss in shape]
    y,x = np.ogrid[-m:m+1,-n:n+1]
    h = np.exp( -(x*x + y*y) / (2.*sigma*sigma) )
    h[ h < np.finfo(h.dtype).eps*h.max() ] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h


def gauss1D(shape=3, sigma=0.5):
    m = (shape-1.)/2.
    x = np.ogrid[-m:m+1]
    h = np.exp( -(x*x) / (2.*sigma*sigma))
    h[h < np.finfo(h.dtype).eps*h.max()] = 0
    sumh = h.sum()
    if sumh != 0:
        h /= sumh
    return h


if __name__ == '__main__':
    Im = np.ones((20, 20, 20))
    plot_mind_search_region(r='sparse83')
    MIND(Im, r='sparse83')
