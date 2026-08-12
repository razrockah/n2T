# Heat map of the TBR mesh tally: x-z slice through the source plane.
using CSV, DataFrames, CairoMakie

function plt_heatmap(x, z, values, xlabel, ylabel, title)
    with_theme(theme_latexfonts()) do
        fig = Figure(size = (1000, 600))
        ax = Axis(fig[1, 1], xlabel = xlabel, ylabel = ylabel, title = title, xlabelsize = 25, ylabelsize = 25, titlesize = 30, xticklabelsize = 20, yticklabelsize = 20)
        hm = heatmap!(ax, x, z, values)
        Colorbar(fig[1, 2], hm, labelsize = 25, ticklabelsize = 20)
        fig
    end
end

csv_path = joinpath(@__DIR__, "..", "results", "tbr_mesh.csv")
df = CSV.read(csv_path, DataFrame)

# x-z slice at the y bin closest to the source plane (y = 0)
ys = unique(df.y_cm)
y0 = ys[argmin(abs.(ys))]
slice = df[df.y_cm .== y0, :]

xs = sort(unique(slice.x_cm))
zs = sort(unique(slice.z_cm))
tbr = zeros(length(xs), length(zs))
for row in eachrow(slice)
    i = searchsortedfirst(xs, row.x_cm)
    j = searchsortedfirst(zs, row.z_cm)
    tbr[i, j] = row.tbr
end

title = "TBR, $(slice.breeder[1]), $(slice.enrichment[1]) at% Li-6 (y = $(y0) cm)"
fig = plt_heatmap(xs, zs, tbr, "x [cm]", "z [cm]", title)

png_path = joinpath(@__DIR__, "..", "results", "tbr_heatmap.png")
save(png_path, fig)
println("saved $(png_path)")
