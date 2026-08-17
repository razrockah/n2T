import openmc

with openmc.StatePoint('li_statepoint.h5') as sp:
    li_mesh_tbr_df = sp.get_tally(name='tbr mesh').get_pandas_dataframe()
li_mesh_tbr_df.to_csv("li_tbr_mesh.csv", index = False)

with openmc.StatePoint('flibe_statepoint.h5') as sp:
    flibe_mesh_tbr_df = sp.get_tally(name='tbr mesh').get_pandas_dataframe()
flibe_mesh_tbr_df.to_csv("flibe_tbr_mesh.csv", index = False)

with openmc.StatePoint('pbli_statepoint.h5') as sp:
    pbli_mesh_tbr_df = sp.get_tally(name='tbr mesh').get_pandas_dataframe()
pbli_mesh_tbr_df.to_csv("pbli_tbr_mesh.csv", index = False)


