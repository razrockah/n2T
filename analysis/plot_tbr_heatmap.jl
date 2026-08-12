# TBR heat maps for the slab: x-z slice on the source axis (y = 0) and
# x-y slice in the first breeder voxel layer (z = 4.5 cm).
using CSV, DataFrames, CairoMakie

function plt_heatmap(x, y, values, xlabel, ylabel, title)
    with_theme(theme_latexfonts()) do
        fig = Figure(size = (1000, 600))
        ax = Axis(fig[1, 1], xlabel = xlabel, ylabel = ylabel, title = title, xlabelsize = 25, ylabelsize = 25, titlesize = 30, xticklabelsize = 20, yticklabelsize = 20)
        hm = heatmap!(ax, x, y, values)
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
        vals[i, j] = row.tbr
    end
    xs, ys, vals
end

df = CSV.read(joinpath(@__DIR__, "..", "results", "tbr_mesh.csv"), DataFrame)
label = "$(df.breeder[1]), $(df.enrichment[1]) at% Li-6"

# x-z slice through the source axis (a voxel column is centered on y = 0)
xs, zs, tbr_xz = slice_matrix(df[df.y_cm .== 0, :], :x_cm, :z_cm)
fig = plt_heatmap(xs, zs, tbr_xz, "x [cm]", "z [cm]", "TBR, $(label) (y = 0)")
png_path = joinpath(@__DIR__, "..", "results", "tbr_heatmap.png")
save(png_path, fig)
println("saved $(png_path)")

# x-y slice in the first breeder voxel layer (breeder starts at z = 4)
xs, ys, tbr_xy = slice_matrix(df[df.z_cm .== 4.5, :], :x_cm, :y_cm)
fig = plt_heatmap(xs, ys, tbr_xy, "x [cm]", "y [cm]", "TBR, $(label) (z = 4.5 cm)")
png_path = joinpath(@__DIR__, "..", "results", "tbr_heatmap_xy.png")
save(png_path, fig)
println("saved $(png_path)")
