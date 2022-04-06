# icom_abm

Geopandas package installation problem:

module load python/anaconda3.6
source /share/apps/python/anaconda3.6/etc/profile.d/conda.sh

pip install --user geopandas==0.9.0     failed because setuptool package is not up-to-date

Solution:
pip install --upgrade setuptools (also make sure pip is up-to-date; if not, update pip)

