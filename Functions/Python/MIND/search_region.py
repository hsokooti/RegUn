import numpy as np
import matplotlib.pyplot as plt

def plot_mind_search_region(r):
    zs, ys, xs = search_region(r)
    if r == 'sparse83':
        kernel = np.zeros([3, 7, 7])
        for i in range(len(zs)):
            kernel[zs[i], ys[i], xs[i]] = 1
        for f in range(3):
            plt.figure(figsize=(8, 8))
            # fig, ax = plt.subplots(figsize=(8, 8))
            plt.imshow(kernel[f, :, :], interpolation='none')
            ax = plt.gca()
            ax.set_xticks(np.arange(0, 10, 1));
            ax.set_yticks(np.arange(0, 10, 1));
            ax.set_xticklabels(np.arange(1, 11, 1));
            ax.set_yticklabels(np.arange(1, 11, 1));
            ax.grid(which='minor', color='g', linestyle='-', linewidth=5)
            plt.draw()
            plt.show()


def search_region(r):
    if r == 0:
        xs = [1, -1, 0, 0, 0, 0]
        ys = [0, 0, 1, -1, 0, 0]
        zs = [0, 0, 0, 0, 1, -1]

    elif r == 'sparse83':
        indices_discard = []
        xs = []
        ys = []
        zs = []
        for z in range(-1,2):
            for y in np.setxor1d(np.arange(-3, 4), 0):
                for x in np.setxor1d(np.arange(-3, 4), 0):
                    if (abs(x) != abs(y)) and (abs(z) == 1):
                        indices_discard.append([z, y, x])
                    elif (abs(x) != abs(y)) and (abs(x) == 3 or abs(y) == 3):
                        indices_discard.append([z, y, x])

        z_mesh, y_mesh, x_mesh = np.meshgrid(np.arange(-1, 2), np.arange(-3, 4), np.arange(-3, 4), indexing='ij')
        for z in range(np.shape(z_mesh)[0]):
            for y in range(np.shape(z_mesh)[1]):
                for x in range(np.shape(z_mesh)[2]):
                    shift = [z_mesh[z, y, x], y_mesh[z, y, x], x_mesh[z, y, x]]
                    if not list_intersection(indices_discard, shift):
                        zs.append(shift[0])
                        ys.append(shift[1])
                        xs.append(shift[2])

    return [zs, ys, xs]


def list_intersection(list, search_element):
    count = 0
    # print('search element {} is '.format(search_element))
    for element in list:
        if element == search_element:
            # print('element {} is removed'.format(element))
            count = count + 1
    return count