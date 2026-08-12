# Neutron flux heat map: x-z slice through the whole region (void + slab),
# log color scale.
using CSV, DataFrames, CairoMakie

function plt_heatmap(x, y, values, xlabel, ylabel, title)
    with_theme(theme_latexfonts()) do
        fig = Figure(size = (1000, 600))
        ax = Axis(fig[1, 1], xlabel = xlabel, ylabel = ylabel, title = title, xlabelsize = 25, ylabelsize = 25, titlesize = 30, xticklabelsize = 20, yticklabelsize = 20)
        hm = heatmap!(ax, x, y, values, colorscale = log10)
        Colorbar(fig[1, 2], hm, labelsize = 25, ticklabelsize = 20)
        fig
    end
end

function slice_matrix(slice, xcol, ycol)
    xs = sort(unique(slice[!, xcol]))
    ys = sort(unique(slice[!, ycol]))
    vals = zeros(length(xs), length(ys))
    for row in eachrow(slice)
        i = searchsortedfirst(xs, row[xcol])
        j = searchsortedfirst(ys, row[ycol])
        vals[i, j] = row.flux
    end
    xs, ys, vals
end

df = CSV.read(joinpath(@__DIR__, "..", "results", "flux_mesh.csv"), DataFrame)
label = "$(df.breeder[1]), $(df.enrichment[1]) at% Li-6"

# x-z slice at the y voxel nearest the axis
ys_all = unique(df.y_cm)
y0 = ys_all[argmin(abs.(ys_all))]
xs, zs, flux_xz = slice_matrix(df[df.y_cm .== y0, :], :x_cm, :z_cm)
flux_xz[flux_xz .<= 0] .= NaN  # empty voxels break the log scale

fig = plt_heatmap(xs, zs, flux_xz, "x [cm]", "z [cm]", "Neutron flux, $(label) (y = $(y0) cm)")
png_path = joinpath(@__DIR__, "..", "results", "flux_heatmap.png")
save(png_path, fig)
println("saved $(png_path)")
