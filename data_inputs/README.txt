1. "simple_anova_hedonic_blck_fromBGMean" calculates the mean of the housing characteristics at block group level, which is serving
 as the housing characteristics data for each block.
2. "blck_housing_1993_InheritedFromBG" use the BG level sales price data in 1993 as the housing sales price data at block level. Its
population/hhsize/mhi1990 are calculated at the block level under 2010 boundary. Therefore, some blocks receiving 0 population, and 
several hhsize1990 is infinite due to data error. These blocks are removed.
   "blck_housing_1993_InheritedFromBG_v2" is based on the previous version, but filling NA salesprice1993/salespricesf1993/ by the value of the nearest 
neighborhood.

3. baltimore_blck.shp contains all the blocks in the Baltimore city and Baltimore county;
   baltimore_blck2.shp removes NA mhi1990 after join shapefile with blck_housing_1994.csv
   baltimore_blck3.shp removes NA mhi1990 after join shapefile with blck_housing_1993_InheritedFromBG.csv
   