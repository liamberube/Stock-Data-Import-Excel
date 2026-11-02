import numpy as np
import pandas as pd


df = pd.read_excel("Stock_History_Formulas.xlsx")
df.to_csv('Data/Stock_Values_data.csv')