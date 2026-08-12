# Read the TBR mesh tally CSV into a DataFrame variable `df`.
using CSV, DataFrames

csv_path = joinpath(@__DIR__, "..", "results", "tbr_mesh.csv")
df = CSV.read(csv_path, DataFrame)
println(df)
