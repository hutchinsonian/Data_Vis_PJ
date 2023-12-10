# Data_Vis_PJ
Project code of DATA620018 
This Backend code mainly refers to https://github.com/tinnerhrhe/Chinavis2022-1

## Install
```
conda create -n datavis python=3.9
conda activate datavis
pip install pandas
```
## Generate the data you need
Put `Link.csv` and `Node.csv` into `./data/`.
```
python backend/score.py  # get score for uniform cost search
python backend/main.py  # get coregraph.json, subgraph.json, ...,
python backend/export.py  # get node.csv, link.cv, ..., for each output item
```
The above code will put the extracted json file into output, and I have already put these files into ouput. So you don't need to run this code

## Visualizes
```
python backend/visualize.py
```

