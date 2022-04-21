#include <iostream>
#include <limits>
#include <random>

//Pseudocode
  float evaluate_MIbox_image(const Image& imageA, const Image& imageB, int minX, int minY, int minZ, int maxX, int maxY, int maxZ , std::vector<float>& outMI)
  {
	  float maxW = std::numeric_limits<float>::lowest();
	  float minW = std::numeric_limits<float>::infinity();

	  float pA;
	  float pB;
	  float mA = 0;
	  float mB = 0;
	  float sA = 0;
	  float sB = 0;

	  for (int i = minX; i < maxX + 1; i++){
		  for (int j = minY; j < maxY + 1; j++){
			  for (int k = minZ; k < maxZ + 1; k++){
				  pA = imageA(i, j, k);
				  if (pA > maxW) maxW = pA;
				  if (pA < minW) minW = pA;
				  pB = imageB(i, j, k);
				  if (pB > maxW) maxW = pB;
				  if (pB < minW) minW = pB;
				  mA = mA + pA;
				  mB = mB + pB;
			  }
		  }
	  }

	  float diffV = maxW - minW;
	  float n = (maxX - minX + 1)*(maxY-minY+1)*(maxZ-minZ+1);
	  float Bfloat = std::log2(n) + 1;
	  int B = (int)(Bfloat + 0.5f);  
	  mA = mA / n;
	  mB = mB / n; 


	  std::vector<float> HistA(B);
	  std::vector<float> HistB(B);
	  std::vector<float> HistAB(B*B);
	  std::fill(HistA.begin(), HistA.end(), 0);
	  std::fill(HistB.begin(), HistB.end(), 0);
	  std::fill(HistAB.begin(), HistAB.end(), 0);

	  float MI = 0;
	  float HX = 0;
	  float HY = 0;
	  float HXY = 0;

	  
	  for (int i = minX; i < maxX + 1; i++){
		  for (int j = minY; j < maxY + 1; j++){
			  for (int k = minZ; k < maxZ + 1; k++){
				  float normA = (imageA(i, j, k) - minW) / (maxW - minW)*B;
				  float normB = (imageB(i, j, k) - minW) / (maxW - minW)*B;
				  int indA = (int)(round(normA));
				  int indB = (int)(round(normB));
				  if (indA == B) indA = indA - 1;
				  if (indB == B) indB = indB - 1;
				  HistA[indA] = HistA[indA] + 1;
				  HistB[indB] = HistB[indB] + 1;
				  HistAB[indA*B + indB] = HistAB[indA*B + indB] + 1;
				  sA = sA + pow((imageA(i, j, k) - mA), 2);
				  sB = sB + pow((imageB(i, j, k) - mB), 2);
			  }
		  }
	  }
	  sA = sA / (n-1);
	  sB = sB / (n-1);
	  sA = sqrt(sA);
	  sB = sqrt(sB);

	  for (int i = 0; i < B; i++){
		  for (int j = 0; j < B; j++){
			  float PXY = HistAB[i*B + j] / (n);
			  float PX = HistA[i] / n;
			  float PY = HistB[j] / n; 
			  if (PXY != 0 && PX != 0 && PY != 0) {
				  MI = MI + PXY * std::log(PXY / (PX*PY));
				  HXY = HXY + PXY * std::log(1 / PXY);
			  }
		  }
		  float PX = HistA[i] / n;
		  float PY = HistB[i] / n;
		  if (PX != 0){
			  HX = HX + PX * std::log(1 / PX);
		  }
		  if (PY != 0){
			  HY = HY + PY * std::log(1 / PY);
		  }
	  }

	  float minH = HX;
	  if (HY < HX) minH = HY;
	  	  

	  (HX == 0 || HY == 0 || (HX*HY<0)) ? outMI[1] = 0 : outMI[1] = MI / sqrt(HX*HY);
	  (minH == 0) ? outMI[3] = 0 : outMI[3] = MI / minH;
	  (HXY == 0) ? outMI[5] = 0 : outMI[5] = (HX + HY) / HXY;

	  B = 32;
	  std::vector<float> HistA2(B);
	  std::vector<float> HistB2(B);
	  std::vector<float> HistAB2(B*B);
	  std::fill(HistA2.begin(), HistA2.end(), 0);
	  std::fill(HistB2.begin(), HistB2.end(), 0);
	  std::fill(HistAB2.begin(), HistAB2.end(), 0);
	  MI = 0;
	  HX = 0;
	  HY = 0;
	  HXY = 0;
	  float NCR = 0;
	  for (int i = minX; i < maxX + 1; i++){
		  for (int j = minY; j < maxY + 1; j++){
			  for (int k = minZ; k < maxZ + 1; k++){
				  float normA = (imageA(i, j, k) - minW) / (maxW - minW)*B;
				  float normB = (imageB(i, j, k) - minW) / (maxW - minW)*B;
				  int indA = (int)(round(normA));
				  int indB = (int)(round(normB));
				  if (indA == B) indA = indA - 1;
				  if (indB == B) indB = indB - 1;
				  HistA2[indA] = HistA2[indA] + 1;
				  HistB2[indB] = HistB2[indB] + 1;
				  HistAB2[indA*B + indB] = HistAB2[indA*B + indB] + 1;
				  NCR = NCR + (imageA(i, j, k) - mA)*(imageB(i, j, k) - mB);
			  }
		  }
	  }
	  NCR = NCR / (sA*sB);
	  NCR = NCR / n; 

	  for (int i = 0; i < B; i++){
		  for (int j = 0; j < B; j++){
			  float PXY = HistAB2[i*B + j] / (n);
			  float PX = HistA2[i] / n;
			  float PY = HistB2[j] / n;
			  if (PXY != 0 && PX != 0 && PY != 0) {
				  MI = MI + PXY * std::log(PXY / (PX*PY));
				  HXY = HXY + PXY * std::log(1 / PXY);
			  }
		  }
		  float PX = HistA2[i] / n;
		  float PY = HistB2[i] / n;
		  if (PX != 0){
			  HX = HX + PX * std::log(1 / PX);
		  }
		  if (PY != 0){
			  HY = HY + PY * std::log(1 / PY);
		  }
	  }

	  minH = HX;
	  if (HY < HX) minH = HY;

	  (HX == 0 || HY == 0 || (HX*HY<0)) ? outMI[0] = 0 : outMI[0] = MI / sqrt(HX*HY);
	  (minH == 0) ? outMI[2] = 0 : outMI[2] = MI / minH;
	  (HXY == 0) ? outMI[4] = 0 : outMI[4] = (HX + HY) / HXY;
	  outMI[6] = NCR; 
	  /*
	  outMI[0]	:	NMI
	  outMI[1]	:	NMIS
	  outMI[2]	:	PMI
	  outMI[3]	:	PMIS
	  outMI[4]	:	NMI-> ITK
	  outMI[5]	:	NMIS-> ITK
	  outMI[6]  :	NCR
	  */

	  return 0;
  }