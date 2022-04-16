import math
import openmc
import openmc_dagmc_wrapper as odw
import openmc_data_downloader as odd

w = openmc.Material(name="w")
w.add_element("W", 1)
w.set_density("g/cc", 19.3)


cu = openmc.Material(name="cu")
cu.add_element("Cr", 0.012)
cu.add_element("Zr", 0.0007)
cu.set_density("g/cc", 8.96)

copper = openmc.Material(name="copper")
copper.add_element("copper", 1)
copper.set_density("g/cc", 8.96)

dag_univ = openmc.DAGMCUniverse("dagmc.h5m")

containing_cell = openmc.Cell(cell_id=9999, fill=dag_univ)

geometry = openmc.Geometry(root=[containing_cell])

# creates an edge of universe boundary surface
vac_surf = openmc.Sphere(r=10000, surface_id=9999, boundary_type="vacuum")

# adds reflective surface for the sector model at 0 degrees
reflective_1 = openmc.Plane(
    a=math.sin(0),
    b=-math.cos(0),
    c=0.0,
    d=0.0,
    surface_id=9991,
    boundary_type="reflective",
)

# adds reflective surface for the sector model at 90 degrees
reflective_2 = openmc.Plane(
    a=math.sin(math.radians(90)),
    b=-math.cos(math.radians(90)),
    c=0.0,
    d=0.0,
    surface_id=9990,
    boundary_type="reflective",
)

# specifies the region as below the universe boundary and inside the reflective surfaces
region = -vac_surf

# creates a cell from the region and fills the cell with the dagmc geometry
containing_cell = openmc.Cell(cell_id=9999, region=region, fill=dag_univ)

geometry = openmc.Geometry(root=[containing_cell])

my_source = openmc.Source()

# sets the location of the source to x=0 y=0 z=0
my_source.space = openmc.stats.Point((0, 0, 5))

# sets the direction to isotropic
my_source.angle = openmc.stats.Isotropic()

# sets the energy distribution to 100% 14MeV neutrons
my_source.energy = openmc.stats.Discrete([14e6], [1])


# this links the material tags in the dagmc h5m file with materials.
# these materials are input as strings so they will be looked up in the
# neutronics material maker package
materials = odw.Materials(
    h5m_filename="dagmc.h5m",
    correspondence_dict={
        "blue_part": cu,
        "grey_part":w,
        "red_part": copper,
    },
)
settings = openmc.Settings()
settings.batches = 50
settings.particles = 1000000
settings.inactive = 0
settings.run_mode = "fixed source"
settings.source = my_source
# adds a tally to record the heat deposited in entire geometry
cell_tally = openmc.Tally(name="heating")
cell_tally.scores = ["heating"]

# creates a mesh that covers the geometry
mesh = openmc.RegularMesh()

mesh.dimension = [25, 5, 25]
   
mesh.lower_left = [-1.15, -0.6, -1.25]  # x,y,z coordinates start at 0 as this is a sector model
mesh.upper_right = [1.15, 0.6, 1.75]

# makes a mesh tally using the previously created mesh and records heating on the mesh
mesh_tally = openmc.Tally(name="heating_on_mesh")
mesh_filter = openmc.MeshFilter(mesh)
mesh_tally.filters = [mesh_filter]
mesh_tally.scores = ["heating"]

# groups the two tallies
tallies = openmc.Tallies([cell_tally, mesh_tally])
odd.just_in_time_library_generator(
    libraries='ENDFB-7.1-NNDC',
    materials=materials
)
# builds the openmc model
my_model = openmc.Model(
    materials=materials, geometry=geometry, settings=settings, tallies=tallies
)

# starts the simulation
my_model.run()
