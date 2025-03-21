import pandas as pd
import geopandas as gpd
import os
import arcpy

ztca = os.path.join(r'C:\Users\or0270734\Downloads\tl_2024_us_zcta520', 'tl_2024_us_zcta520.shp')
pop = os.path.join(r'C:\Users\or0270734\PycharmProjects\PythonProject', 'pop_by_ztca.csv')
gdb = os.path.join(os.getcwd(), 'POP_by_ZIP.gdb')

df = pd.read_csv(pop).transpose().reset_index()
df.rename(columns={'index':'ZIP', 0:'POP'}, inplace=True)
df.drop(df.index[0], inplace=True)
df['ZIP'] = [x.replace('ZCTA5 ', ' ') for x in df['ZIP']]
df['POP'] = [int(x.replace(',', '')) if type(x) == str else x for x in df['POP']]
df['ZIP_5'] = [int(x) for x in df['ZIP']]
df['ZIP_3'] = [int(x[0:4]) for x in df['ZIP']]

pop_df = df.groupby(['ZIP_3'])['POP'].sum()
joined_df = pd.merge(df, pop_df, on='ZIP_3')

joined_df.drop(columns=['ZIP'], inplace=True)
joined_df.rename(columns={'POP_x': 'POP_3', 'POP_y':'POP_5'}, inplace=True)

cols_for_3 = ['ZIP_3', 'POP_3']
cols_for_5 = ['ZIP_5', 'POP_5']

df_for_3 = joined_df[cols_for_3]
df_for_5 = joined_df[cols_for_5]

shp_fields = [x.name for x in arcpy.ListFields(ztca)]
if 'ZIP_3' not in shp_fields:
    arcpy.AddField_management(ztca, 'ZIP_3', 'LONG')
    
if not arcpy.Exists(gdb):
    arcpy.CreateFileGDB_management(os.getcwd(), 'POP_by_ZIP.gdb')

expression = """int(str(!ZCTA5CE20!)[0:3])"""
arcpy.CalculateField_management(ztca, 'ZIP_3', expression, 'PYTHON3')
arcpy.Dissolve_management(ztca, os.path.join(gdb, 'POP_by_ZIP3'), 'ZIP_3')
arcpy.CopyFeatures_management(ztca, os.path.join(gdb, 'POP_by_ZIP5'))

...
