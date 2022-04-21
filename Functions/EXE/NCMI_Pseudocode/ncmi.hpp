#include <random>
#include <stdio.h>

// Pseudocode
template<typename label_type>
float FeatureFactory::evaluate_box_mi(const DataSample<label_type>& dataSample, int channel, const Eigen::Vector3d& offset, const Eigen::Vector3d& boxsize, std::vector<float>& outMI)
{
	int img_index = dataSample.image_index;
	Eigen::Vector3d imgpoint = dataSample.point;
	Eigen::Vector3d spacing = m_intensity_images[img_index][channel].spacing();
	Eigen::Vector3d boxsize_pixels = boxsize.cwiseQuotient(spacing);


	Eigen::Vector3d boxpoint_min = imgpoint + offset.cwiseQuotient(spacing) - boxsize_pixels / 2.0;
	Eigen::Vector3d boxpoint_max = boxpoint_min + boxsize_pixels;

	int x_min = static_cast<int>(boxpoint_min[0] + 0.5);
	int y_min = static_cast<int>(boxpoint_min[1] + 0.5);
	int z_min = static_cast<int>(boxpoint_min[2] + 0.5);

	int x_max = static_cast<int>(boxpoint_max[0] + 0.5);
	int y_max = static_cast<int>(boxpoint_max[1] + 0.5);
	int z_max = static_cast<int>(boxpoint_max[2] + 0.5);

	int sizeX = m_intensity_images[img_index][channel].sizeX(); // Size of the image + 1 
	int sizeY = m_intensity_images[img_index][channel].sizeY();
	int sizeZ = m_intensity_images[img_index][channel].sizeZ();

	int count_outside_x = 0;
	int count_outside_y = 0;
	int count_outside_z = 0;

	if (x_min < 0)
	{
		x_min = 0;
		count_outside_x++;
	}
	else if (x_min > sizeX - 1)
	{
		x_min = sizeX - 1;
		count_outside_x++;
	}

	if (x_max < 0)
	{
		x_max = 0;
		count_outside_x++;
	}
	else if (x_max > sizeX - 1)
	{
		x_max = sizeX - 1;
		count_outside_x++;
	}

	if (y_min < 0)
	{
		y_min = 0;
		count_outside_y++;
	}
	else if (y_min > sizeY - 1)
	{
		y_min = sizeY - 1;
		count_outside_y++;
	}

	if (y_max < 0)
	{
		y_max = 0;
		count_outside_y++;
	}
	else if (y_max > sizeY - 1)
	{
		y_max = sizeY - 1;
		count_outside_y++;
	}

	if (z_min < 0)
	{
		z_min = 0;
		count_outside_z++;
	}
	else if (z_min > sizeZ - 1)
	{
		z_min = sizeZ - 1;
		count_outside_z++;
	}

	if (z_max < 0)
	{
		z_max = 0;
		count_outside_z++;
	}
	else if (z_max > sizeZ - 1)
	{
		z_max = sizeZ - 1;
		count_outside_z++;
	}

	if (count_outside_x == 2 || count_outside_y == 2 || count_outside_z == 2) return 0.0f;



	float mi_value = evaluate_MIbox_image(m_intensity_images[0][channel], m_intensity_images[1][channel],x_min, y_min, z_min, x_max, y_max, z_max , outMI);

	return mi_value;
}