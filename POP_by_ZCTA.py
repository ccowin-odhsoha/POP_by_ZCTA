import os
import arcpy
import pandas as pd

cwd = os.getcwd()
zcta_folder = os.path.join(cwd, 'tl_2024_us_zcta520')
state_folder = os.path.join(cwd, 'tl_2024_us_state')
zcta_shp = os.path.join(zcta_folder, 'tl_2024_us_zcta520.shp')
state_shp = os.path.join(state_folder, 'tl_2024_us_state.shp')

pop_csv = os.path.join(cwd, 'pop_by_zcta.csv')
pop_csv_trans = os.path.join(cwd, 'pop_by_zcta_trans.csv')
gdb = os.path.join(cwd, 'POP_by_ZIP.gdb')
pop_path = os.path.join(gdb, 'Pop')
zcta_fc_path = os.path.join(gdb, 'ZCTA_FC')
zcta_fl_path = os.path.join(gdb, 'ZCTA_FL')
state_path = os.path.join(gdb, 'State')
zcta_in_oregon_path = os.path.join(gdb, 'ZCTA_in_Oregon')

zcta3_path = os.path.join(gdb, 'Pop_by_ZCTA3')
zcta5_path = os.path.join(gdb, 'Pop_by_ZCTA5')

csv_out = os.path.join(cwd, 'POP_by_ZCTA_FINAL.csv')

df = pd.read_csv(pop_csv).transpose().reset_index()
df.rename(columns={'index':'ZIP', 0:'POP'}, inplace=True)
df.drop(df.index[0], inplace=True)
df['ZIP'] = [x.replace('ZCTA5 ', '') for x in df['ZIP']]
df['POP'] = [int(pop.replace(',', '')) if type(pop) == str else pop for pop in df['POP']]
df.to_csv(pop_csv_trans, index=False)

if not arcpy.Exists(gdb):
    arcpy.CreateFileGDB_management(cwd, 'POP_by_ZIP.gdb')
else:
    arcpy.Delete_management(os.path.join(cwd, 'POP_by_ZIP.gdb'))
    arcpy.CreateFileGDB_management(cwd, 'POP_by_ZIP.gdb')

arcpy.env.workspace = gdb
zcta_fc = arcpy.conversion.ExportFeatures(zcta_shp, zcta_fc_path)
zcta_fl = arcpy.management.MakeFeatureLayer(zcta_fc, zcta_fl_path)
pop_tbl = arcpy.conversion.ExportTable(pop_csv_trans, pop_path)
arcpy.management.AddField(pop_tbl, 'ZIP_text', 'TEXT')
arcpy.management.CalculateField(pop_tbl, 'ZIP_text', '!ZIP!', 'PYTHON3')

zcta_in_oregon_with_pop = arcpy.management.JoinField(zcta_fl, "ZCTA5CE20", pop_path, 'ZIP_text', fields=['POP'])
delete_selection = arcpy.management.SelectLayerByAttribute(zcta_in_oregon_with_pop, 'NEW_SELECTION', 'POP IS NULL')
arcpy.management.DeleteFeatures(delete_selection)
arcpy.management.AddField(zcta_in_oregon_with_pop, 'ZIP3', 'TEXT')
arcpy.management.AddField(zcta_in_oregon_with_pop, 'ZIP5', 'TEXT')
arcpy.management.CalculateField(zcta_in_oregon_with_pop, 'ZIP5', '!ZCTA5CE20!', 'PYTHON3')
arcpy.management.CalculateField(zcta_in_oregon_with_pop, 'ZIP3', 'str(!ZCTA5CE20!)[0:3]', 'PYTHON3')

arcpy.management.Dissolve(zcta_in_oregon_with_pop, zcta3_path, 'ZIP3', [['POP', 'SUM']])

arcpy.management.JoinField(zcta_in_oregon_with_pop, 'ZIP3', zcta3_path, 'ZIP3', fields=['SUM_POP'])
final = arcpy.conversion.ExportFeatures(zcta_in_oregon_with_pop, zcta5_path, field_mapping=r'ZIP5 "ZIP5" true true false 255 Text 0 0,First,#,C:\Users\or0270734\PycharmProjects\POP_by_ZCTA\POP_by_ZIP.gdb\ZCTA_FC,ZIP5,0,254;POP5 "POP5" true true false 4 Long 0 0,First,#,C:\Users\or0270734\PycharmProjects\POP_by_ZCTA\POP_by_ZIP.gdb\ZCTA_FC,POP,-1,-1;ZIP3 "ZIP3" true true false 255 Text 0 0,First,#,C:\Users\or0270734\PycharmProjects\POP_by_ZCTA\POP_by_ZIP.gdb\ZCTA_FC,ZIP3,0,254;POP3 "POP3" true true false 8 Double 0 0,First,#,C:\Users\or0270734\PycharmProjects\POP_by_ZCTA\POP_by_ZIP.gdb\ZCTA_FC,SUM_POP,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,C:\Users\or0270734\PycharmProjects\POP_by_ZCTA\POP_by_ZIP.gdb\ZCTA_FC,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,C:\Users\or0270734\PycharmProjects\POP_by_ZCTA\POP_by_ZIP.gdb\ZCTA_FC,Shape_Area,-1,-1')
selection = arcpy.management.SelectLayerByAttribute(final, 'NEW_SELECTION', 'POP3 <= 20000')
arcpy.management.CalculateField(selection, 'ZIP3', '"000"', 'PYTHON3')
arcpy.conversion.ExportTable(final, csv_out, sort_field='ZIP5 ASCENDING')
