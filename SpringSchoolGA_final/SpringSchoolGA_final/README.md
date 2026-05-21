# SpringSchool - ProjectChrono - GeneticAlgorithm

1. Create a folder named <b>"build"</b> inside the ChronoProject_GeneticAlgorithm folder.

2. Use CMake in order to build the application:
    - "Where is the source" -> select the path to the ChronoProject_GeneticAlgorithm folder (".../ChronoProject_GeneticAlgorithm")
    - "Where to build the binaries" -> select the path to the build folder created inside the ChronoProject_GeneticAlgorithm folder (".../ChronoProject_GeneticAlgorithm/build")
    - If Chrono_DIR was not found, edit the value of Chrono_DIR to .../chrono-build/cmake

3. Open <b>ChronoProject_GeneticAlgorithm.sln</b> (CMake will generate it).
4. In the Solution Explorer in Visual Studio, right click on ChronoProject_GeneticAlgorithm and then click on <b>"Set as Startup Project"</b>.
5. Build and compile the project. If some dll's are not found you need to copy them manually. You’ll find all of them in …/StructuralOptimizationUsingGA/chrono-build/bin, in Release and Debug directories. Just copy them in your project, in the corresponding Debug or Release folder.

## Python UI (experiment dashboard)

An interactive Python dashboard was added in `ui/` for:

- setting GA parameters
- running the C++ executable from UI
- comparing runs by fitness/selection/crossover labels
- viewing graphs for fitness evolution, method impact, and profiling

Quick start:

1. `pip install -r ui/requirements.txt`
2. `streamlit run ui/app.py`

More details: `ui/README.md`.
