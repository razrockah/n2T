### A Pluto.jl notebook ###
# v1.0.3

using Markdown
using InteractiveUtils

# ╔═╡ 0d784769-d76c-4c6a-92b6-cf7130b35a9c
using CSV, DataFrames, CairoMakie

# ╔═╡ 96f42e1e-e20d-4821-9680-0283ff876257
md"""
# n2T — results

**neutron to tritium**: Li-6 enrichment analysis for fusion breeder blankets, built on [OpenMC](https://openmc.org).

The model is a slab blanket with an 80 x 80 cm face, layered along z (the slab front face is at z = 0, so z is directly the depth into the slab):

| layer | material | thickness |
|-------|----------|-----------|
| coating | W | 0.1 cm |
| first wall | Eurofer + He (77/23 vol%) | 3.9 cm |
| breeder | PbLi / Li / FLiBe, Li-6 enriched | 15 cm |

A uniform box source (Muir DT spectrum, 14.08 MeV, kt = 20 keV) fills the full face of the void, 4 cm thick, centered 10 cm in front of the coating.

`src/run_tbr.py` runs OpenMC and writes the mesh tallies to `results/tbr_mesh.csv` (H3 production over the slab) and `results/flux_mesh.csv` (neutron flux over the whole region), both on 2 x 2 x 1 cm voxels. This notebook loads those CSVs and shows the plots.
"""

# ╔═╡ 8707c617-fb11-4861-8323-5bdc3767faa9
md"## Data"

# ╔═╡ c01496d8-810e-4fff-b67f-e02a0e260476
tbr_df = CSV.read(joinpath(@__DIR__, "results", "tbr_mesh.csv"), DataFrame)

# ╔═╡ 33016492-d524-4fd4-8594-ad3ea87f039c
flux_df = CSV.read(joinpath(@__DIR__, "results", "flux_mesh.csv"), DataFrame)

# ╔═╡ 97d9a1f2-b155-4c3d-97bf-7e9fbe975746
label = "$(tbr_df.breeder[1]), $(tbr_df.enrichment[1]) at% Li-6"

# ╔═╡ 5562969f-e1f4-49af-86ab-8c593458a35e
md"## Plot helpers"

# ╔═╡ 078e3837-6740-4afe-b29c-3010b7aa6b67
function plt_heatmap(x, y, values, xlabel, ylabel, title; colorscale = identity)
    with_theme(theme_latexfonts()) do
        fig = Figure(size = (1000, 600))
        ax = Axis(fig[1, 1], xlabel = xlabel, ylabel = ylabel, title = title, xlabelsize = 25, ylabelsize = 25, titlesize = 30, xticklabelsize = 20, yticklabelsize = 20)
        hm = heatmap!(ax, x, y, values, colorscale = colorscale)
        Colorbar(fig[1, 2], hm, labelsize = 25, ticklabelsize = 20)
        fig
    end
end

# ╔═╡ c5a13c0f-0f9f-447f-b1a0-1920c1328a6b
function slice_matrix(slice, xcol, ycol, vcol)
    xs = sort(unique(slice[!, xcol]))
    ys = sort(unique(slice[!, ycol]))
    vals = zeros(length(xs), length(ys))
    for row in eachrow(slice)
        i = searchsortedfirst(xs, row[xcol])
        j = searchsortedfirst(ys, row[ycol])
        vals[i, j] = row[vcol]
    end
    xs, ys, vals
end

# ╔═╡ 3cd69f6e-6b19-42ee-873e-7a42c3d0ac51
md"## TBR"

# ╔═╡ 81ba8376-f4d8-4242-8aba-5a558594eac3
let
    ys = unique(tbr_df.y_cm)
    y0 = ys[argmin(abs.(ys))]
    xs, zs, tbr_xz = slice_matrix(tbr_df[tbr_df.y_cm .== y0, :], :x_cm, :z_cm, :tbr)
    plt_heatmap(xs, zs, tbr_xz, "x [cm]", "z [cm]", "TBR, $(label) (y = $(y0) cm)")
end

# ╔═╡ caac91ac-f59e-4573-997b-971f3f45af09
let
    xs, ys, tbr_xy = slice_matrix(tbr_df[tbr_df.z_cm .== 4.5, :], :x_cm, :y_cm, :tbr)
    plt_heatmap(xs, ys, tbr_xy, "x [cm]", "y [cm]", "TBR, $(label) (z = 4.5 cm)")
end

# ╔═╡ 09277422-0996-482f-a851-836b1f89c2b2
let
    per_z = combine(groupby(tbr_df, :z_cm), :tbr => sum => :tbr_per_cm)
    with_theme(theme_latexfonts()) do
        fig = Figure(size = (1000, 600))
        ax = Axis(fig[1, 1], xlabel = "z [cm]", ylabel = "TBR per cm of depth", title = "TBR depth profile, $(label)", xlabelsize = 25, ylabelsize = 25, titlesize = 30, xticklabelsize = 20, yticklabelsize = 20)
        lines!(ax, per_z.z_cm, per_z.tbr_per_cm, linewidth = 2)
        fig
    end
end

# ╔═╡ 24ea20be-bda7-46eb-8a87-386a70a2e1de
md"Total TBR (sum over all voxels):"

# ╔═╡ 8e7d2138-f3a1-448a-999e-51a1dee7497e
sum(tbr_df.tbr)

# ╔═╡ 2ed80b22-61c8-4073-b5d2-c45e863c5198
md"## Neutron flux"

# ╔═╡ e3f1a7c2-9b4d-4e6f-8a1c-2d5b7f9e0a3c
let
    ys = unique(flux_df.y_cm)
    y0 = ys[argmin(abs.(ys))]
    xs, zs, flux_xz = slice_matrix(flux_df[flux_df.y_cm .== y0, :], :x_cm, :z_cm, :flux)
    flux_xz[flux_xz .<= 0] .= NaN
    plt_heatmap(xs, zs, flux_xz, "x [cm]", "z [cm]", "Neutron flux, $(label) (y = $(y0) cm)"; colorscale = log10)
end

# ╔═╡ Cell order:
# ╟─96f42e1e-e20d-4821-9680-0283ff876257
# ╠═0d784769-d76c-4c6a-92b6-cf7130b35a9c
# ╟─8707c617-fb11-4861-8323-5bdc3767faa9
# ╠═c01496d8-810e-4fff-b67f-e02a0e260476
# ╠═33016492-d524-4fd4-8594-ad3ea87f039c
# ╠═97d9a1f2-b155-4c3d-97bf-7e9fbe975746
# ╟─5562969f-e1f4-49af-86ab-8c593458a35e
# ╠═078e3837-6740-4afe-b29c-3010b7aa6b67
# ╠═c5a13c0f-0f9f-447f-b1a0-1920c1328a6b
# ╟─3cd69f6e-6b19-42ee-873e-7a42c3d0ac51
# ╠═81ba8376-f4d8-4242-8aba-5a558594eac3
# ╠═caac91ac-f59e-4573-997b-971f3f45af09
# ╠═09277422-0996-482f-a851-836b1f89c2b2
# ╟─24ea20be-bda7-46eb-8a87-386a70a2e1de
# ╠═8e7d2138-f3a1-448a-999e-51a1dee7497e
# ╟─2ed80b22-61c8-4073-b5d2-c45e863c5198
# ╠═e3f1a7c2-9b4d-4e6f-8a1c-2d5b7f9e0a3c
