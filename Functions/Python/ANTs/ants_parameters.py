def affine_EMPIRE10(use_mask=False):
    text = """
command="antsRegistration \
--verbose 1 \
--dimensionality $dim \
--output [${op}] \
--use-histogram-matching 1 \
--initial-moving-transform [${FixedImage}, ${MovingImage}, 0] \
--transform Rigid[0.1] \
--metric MI[${FixedImage}, ${MovingImage}, 1 ,32, Regular, 0.25] \
--convergence 1000x500x250x100 \
--smoothing-sigmas 3x2x1x0 \
--shrink-factors 8x4x2x1 \
--transform Affine[0.1] \
--metric MI[${FixedImage},${MovingImage}, 1, 32, Regular, 0.25] \
--convergence 1000x500x250x100 \
--smoothing-sigmas 3x2x1x0 \
--shrink-factors 8x4x2x1 \
--collapse-output-transforms 1 \
"""
    if use_mask:
        text = text + '--masks [${FixedMask}, ${MovingMask}] '
    text = text + '"'
    return text


def BSpline_SyN_EMPIRE10(setting):
    use_mask = setting['useMask']
    iterations = setting['initial_nonrigid_iterations']

    text = """
command="antsRegistration \
--verbose 1 \
--dimensionality $dim \
--output [${op}] \
--use-histogram-matching 1 \
--initial-moving-transform ${InitialTransform} \
--transform BSplineSyN[0.1, 40, 0, 3] \
--smoothing-sigmas 3x2x1x0 \
--shrink-factors 6x4x2x1 \
"""

    text = text + '--metric CC[${FixedImage}, ${MovingImage}, 1, 4'
    if setting['RandomSampling']:
        text = text + ', Random, '+str(setting['initial_nonrigid_samplingPercentage'])
    text = text + '] '
    text = text + '--convergence ['+str(iterations[0])
    for itr in iterations[1:]:
        text = text + 'x' + str(itr)
    if 'convergenceThreshold' in setting.keys():
        convergence_threshold = setting['convergenceThreshold']
    else:
        convergence_threshold = '1e-6'
    text = text + ', ' + convergence_threshold
    text = text + '] '
    if use_mask:
        text = text + '--masks [${FixedMask}, ${MovingMask}] '
    text = text + '"'
    return text


def bspline_syn_empire10_final(setting):
    use_mask = setting['useMask']
    text = """
command="antsRegistration \
--verbose 1 \
--dimensionality $dim \
--output [${op}] \
--use-histogram-matching 1 \
--initial-moving-transform ${InitialTransform} \
--transform BSplineSyN[0.1, 40, 0, 3] \
--smoothing-sigmas 0 \
--shrink-factors 1 \
"""

    text = text + '--metric CC[${FixedImage}, ${MovingImage}, 1, 4'
    if setting['RandomSampling']:
        text = text + ', Random, '+str(setting['final_nonrigid_samplingPercentage'])
    text = text + '] '
    text = text + '--convergence '+str(setting['final_nonrigid_iterations']) + ' '
    if use_mask:
        text = text + '--masks [${FixedMask}, ${MovingMask}] '
    text = text + '"'
    return text


def transform(number_of_transforms=1):
    text = """
command="antsApplyTransforms \
--verbose 1 \
--dimensionality $dim \
--output [${op}, 1] \
--input ${InputImage} \
--reference-image ${ReferenceImage} \
--interpolation BSpline[3] \
--default-value ${DefaultPixelValue} \
"""
    for transform in range(number_of_transforms):
        text = text + '--transform ${Transform'+str(transform)+'} '
    text = text + '"'
    return text



def transform_image(number_of_transforms=1):
    text = """
command="antsApplyTransforms \
--verbose 1 \
--dimensionality $dim \
--output ${op} \
--input ${InputImage} \
--reference-image ${ReferenceImage} \
--interpolation BSpline[3] \
--default-value ${DefaultPixelValue} \
"""
    for transform in range(number_of_transforms):
        text = text + '--transform ${Transform'+str(transform)+'} '
    text = text + '"'
    return text


def header_registration():
    text = """#!/bin/bash
# h.sokooti@gmail.com
        
ANTS=${ANTSPATH}/antsRegistration
echo "antsRegistration path is  $ANTSPATH"
    
"""
    return text


def header_transform():
    text = """#!/bin/bash
# h.sokooti@gmail.com

ANTS=${ANTSPATH}/antsApplyTransforms
echo "antsApplyTransforms path is  $ANTSPATH"

"""
    return text


def footer():
    text = """

echo " $command "
$command

ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=$ORIGINALNUMBEROFTHREADS
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS

"""
    return text


def write_number_of_threads(number_of_threads):
    text= 'NUMBEROFTHREADS=' + str(number_of_threads) + '\n'
    text = text + """
ORIGINALNUMBEROFTHREADS=${ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS}
ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=$NUMBEROFTHREADS
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS
        
"""
    return text


def write_fixed_image(fixed_image):
    text= 'FixedImage=' + fixed_image + '\n'
    return text


def write_fixed_mask(fixed_mask):
    text= 'FixedMask=' + fixed_mask + '\n'
    return text

def write_moving_image(moving_image):
    text= 'MovingImage=' + moving_image + '\n'
    return text


def write_moving_mask(moving_mask):
    text= 'MovingMask=' + moving_mask + '\n'
    return text


def write_default_pixel_value(default_pixel_value):
    text= 'DefaultPixelValue=' + str(default_pixel_value) + '\n'
    return text


def write_input_image(input_image):
    text= 'InputImage=' + input_image + '\n'
    return text


def write_reference_image(reference_image):
    text= 'ReferenceImage=' + reference_image + '\n'
    return text


def write_transform_parameters(transform, transform_number=0):
    text= 'Transform'+str(transform_number) + '=' + transform + '\n'
    return text


def write_initial_transform(transform):
    text= 'InitialTransform=' + transform + '\n'
    return text


def write_dimension(dim):
    text= 'dim=' + str(dim) + '\n'
    return text


def write_output(output):
    text= 'op=' + str(output) + '\n'
    return text


