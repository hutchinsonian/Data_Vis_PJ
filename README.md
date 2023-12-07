# Data_Vis_PJ
Project code of DATA620018 
This Backend code mainly refers to https://github.com/tinnerhrhe/Chinavis2022-1

## Install
```
conda create -n datavis python=3.9
conda activate datavis
pip install pandas
```
## Prepare
Put `Link.csv` and `Node.csv` into `./data/`.
```
python backend/main.py
python backend/export.py
```
The above code will put the extracted json file into output, but I have already put these files into ouput. So you don't need to run this code

## Run
```
python backend/visualize.py
```

