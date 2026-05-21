import csv
import json
import shutil
import subprocess
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
SETTINGS_PATH = BUILD_DIR / "algorithm_settings.txt"
OUTPUT_CSV = BUILD_DIR / "individual_values.csv"

DATA_DIR = PROJECT_ROOT / "ui" / "experiments"
REGISTRY_PATH = DATA_DIR / "registry.json"


DEFAULT_SETTINGS = {
    "NUMBER_OF_EPOCHS": 5,
    "NUMBER_OF_INDIVIDUALS": 50,
    "OX_SIZE": 10,
    "OY_SIZE": 5,
    "OZ_SIZE": 3,
    "ELEMENT_SIZE": 0.1,
    "CROSSOVER_PROBABILITY": 0.5,
    "MUTATION_PROBABILITY": 0.01,
    "MAXIM_STRESS": 4.5e8,
    "YOUNG_MODULUS": 1e21,
    "POISSON_RATIO": 0.3,
    "DENSITY": 7800.0,
    "FITNESS_TYPE": 0,
    "SELECTION_TYPE": 0,
    "CROSSOVER_TYPE": 0,
}

FITNESS_OPTIONS = {
    "ProductHeadroom": 0,
    "WeightedSum": 1,
    "Penalty": 2,
}

SELECTION_OPTIONS = {
    "Roulette": 0,
    "Tournament": 1,
}

CROSSOVER_OPTIONS = {
    "SinglePoint": 0,
    "Uniform": 1,
}

SETTINGS_ORDER = [
    "NUMBER_OF_EPOCHS",
    "NUMBER_OF_INDIVIDUALS",
    "OX_SIZE",
    "OY_SIZE",
    "OZ_SIZE",
    "ELEMENT_SIZE",
    "CROSSOVER_PROBABILITY",
    "MUTATION_PROBABILITY",
    "MAXIM_STRESS",
    "YOUNG_MODULUS",
    "POISSON_RATIO",
    "DENSITY",
    "FITNESS_TYPE",
    "SELECTION_TYPE",
    "CROSSOVER_TYPE",
]


@dataclass
class Experiment:
    experiment_id: str
    name: str
    created_at: str
    source: str
    fitness_function: str
    selection_method: str
    crossover_method: str
    impact_notes: str
    ga_csv_path: str
    profiling_csv_path: str
    runtime_seconds: float


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        REGISTRY_PATH.write_text("[]", encoding="utf-8")


def load_settings(path: Path) -> Dict[str, float]:
    if not path.exists():
        return DEFAULT_SETTINGS.copy()

    parsed: Dict[str, float] = DEFAULT_SETTINGS.copy()
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if key not in parsed:
                continue
            if key in {
                "NUMBER_OF_EPOCHS",
                "NUMBER_OF_INDIVIDUALS",
                "OX_SIZE",
                "OY_SIZE",
                "OZ_SIZE",
                "FITNESS_TYPE",
                "SELECTION_TYPE",
                "CROSSOVER_TYPE",
            }:
                parsed[key] = int(float(value))
            else:
                parsed[key] = float(value)
    return parsed


def write_settings(path: Path, settings: Dict[str, float]) -> None:
    lines = []
    for key in SETTINGS_ORDER:
        lines.append(f"{key}={settings[key]}")
    path.write_text("\n".join(lines), encoding="utf-8")


def load_registry() -> List[Experiment]:
    ensure_data_dir()
    raw = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return [Experiment(**item) for item in raw]


def save_registry(experiments: List[Experiment]) -> None:
    ensure_data_dir()
    payload = [asdict(exp) for exp in experiments]
    REGISTRY_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def next_experiment_id(experiments: List[Experiment]) -> str:
    return f"exp-{len(experiments) + 1:03d}"


def read_ga_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["EPOCH", "VALUE"])
    data = pd.read_csv(path)
    if "EPOCH" not in data.columns or "VALUE" not in data.columns:
        return pd.DataFrame(columns=["EPOCH", "VALUE"])
    data["EPOCH"] = pd.to_numeric(data["EPOCH"], errors="coerce")
    data["VALUE"] = pd.to_numeric(data["VALUE"], errors="coerce")
    return data.dropna()


def run_ga(executable_path: Path, working_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(executable_path)],
        cwd=str(working_dir),
        capture_output=True,
        text=True,
        check=False,
    )


def copy_into_data(source_path: Path, target_name: str) -> Path:
    ensure_data_dir()
    target_path = DATA_DIR / target_name
    shutil.copy2(source_path, target_path)
    return target_path


def save_uploaded_file(uploaded_file, target_name: str) -> Path:
    ensure_data_dir()
    target_path = DATA_DIR / target_name
    with target_path.open("wb") as file:
        file.write(uploaded_file.getbuffer())
    return target_path


def read_profiling_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        profile = pd.read_csv(path)
    except Exception:
        return pd.DataFrame()
    return profile


def sidebar_settings_form(current_settings: Dict[str, float]) -> Dict[str, float]:
    st.sidebar.header("GA Settings")
    updated = {}
    updated["NUMBER_OF_EPOCHS"] = st.sidebar.number_input(
        "Number of epochs", min_value=1, value=int(current_settings["NUMBER_OF_EPOCHS"]), step=1
    )
    updated["NUMBER_OF_INDIVIDUALS"] = st.sidebar.number_input(
        "Number of individuals", min_value=2, value=int(current_settings["NUMBER_OF_INDIVIDUALS"]), step=1
    )
    updated["OX_SIZE"] = st.sidebar.number_input("OX size", min_value=1, value=int(current_settings["OX_SIZE"]), step=1)
    updated["OY_SIZE"] = st.sidebar.number_input("OY size", min_value=1, value=int(current_settings["OY_SIZE"]), step=1)
    updated["OZ_SIZE"] = st.sidebar.number_input("OZ size", min_value=1, value=int(current_settings["OZ_SIZE"]), step=1)
    updated["ELEMENT_SIZE"] = st.sidebar.number_input(
        "Element size", min_value=0.001, value=float(current_settings["ELEMENT_SIZE"]), step=0.01, format="%.4f"
    )
    updated["CROSSOVER_PROBABILITY"] = st.sidebar.slider(
        "Crossover probability", min_value=0.0, max_value=1.0, value=float(current_settings["CROSSOVER_PROBABILITY"])
    )
    updated["MUTATION_PROBABILITY"] = st.sidebar.slider(
        "Mutation probability", min_value=0.0, max_value=1.0, value=float(current_settings["MUTATION_PROBABILITY"])
    )
    updated["MAXIM_STRESS"] = st.sidebar.number_input(
        "Max allowed stress", min_value=1.0, value=float(current_settings["MAXIM_STRESS"]), format="%.2e"
    )
    updated["YOUNG_MODULUS"] = st.sidebar.number_input(
        "Young modulus", min_value=1.0, value=float(current_settings["YOUNG_MODULUS"]), format="%.2e"
    )
    updated["POISSON_RATIO"] = st.sidebar.number_input(
        "Poisson ratio", min_value=0.0, max_value=0.5, value=float(current_settings["POISSON_RATIO"]), step=0.01
    )
    updated["DENSITY"] = st.sidebar.number_input(
        "Density", min_value=1.0, value=float(current_settings["DENSITY"]), step=1.0
    )

    fitness_label = next(
        (label for label, value in FITNESS_OPTIONS.items() if value == int(current_settings["FITNESS_TYPE"])),
        "ProductHeadroom",
    )
    selection_label = next(
        (label for label, value in SELECTION_OPTIONS.items() if value == int(current_settings["SELECTION_TYPE"])),
        "Roulette",
    )
    crossover_label = next(
        (label for label, value in CROSSOVER_OPTIONS.items() if value == int(current_settings["CROSSOVER_TYPE"])),
        "SinglePoint",
    )

    updated["FITNESS_TYPE"] = FITNESS_OPTIONS[
        st.sidebar.selectbox("Fitness function", list(FITNESS_OPTIONS.keys()), index=list(FITNESS_OPTIONS.keys()).index(fitness_label))
    ]
    updated["SELECTION_TYPE"] = SELECTION_OPTIONS[
        st.sidebar.selectbox("Selection method", list(SELECTION_OPTIONS.keys()), index=list(SELECTION_OPTIONS.keys()).index(selection_label))
    ]
    updated["CROSSOVER_TYPE"] = CROSSOVER_OPTIONS[
        st.sidebar.selectbox("Crossover method", list(CROSSOVER_OPTIONS.keys()), index=list(CROSSOVER_OPTIONS.keys()).index(crossover_label))
    ]

    return updated


def normalize_to_group_max(series: pd.Series) -> pd.Series:
    """Map values to [0, 1] as ratio of the group maximum (0.78 vs 0.84 max => 0.93 vs 1.0)."""
    vmax = series.max()
    if vmax <= 0:
        return pd.Series(0.0, index=series.index)
    return series / vmax


def add_normalized_fitness_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Display-only: scale by max VALUE within each fitness_function (not per-experiment min-max)."""
    if df.empty:
        return df

    plot_df = df.copy()
    plot_df["VALUE_RAW"] = plot_df["VALUE"]
    plot_df["VALUE_NORM"] = plot_df.groupby("fitness_function")["VALUE"].transform(normalize_to_group_max)
    plot_df["VALUE_PCT_OF_GROUP_MAX"] = plot_df["VALUE_NORM"] * 100.0
    return plot_df


def add_normalized_final_fitness(latest_df: pd.DataFrame) -> pd.DataFrame:
    """Display-only: final fitness as ratio of max within each fitness_function group."""
    if latest_df.empty:
        return latest_df

    plot_df = latest_df.copy()
    plot_df["VALUE_RAW"] = plot_df["VALUE"]
    plot_df["VALUE_NORM"] = plot_df.groupby("fitness_function")["VALUE"].transform(normalize_to_group_max)
    plot_df["VALUE_PCT_OF_GROUP_MAX"] = plot_df["VALUE_NORM"] * 100.0
    return plot_df


def render_ga_comparison(experiments_df: pd.DataFrame) -> None:
    st.subheader("Fitness Evolution Across Experiments")
    if experiments_df.empty:
        st.info("No experiments saved yet.")
        return

    plot_df = add_normalized_fitness_columns(experiments_df)
    st.caption(
        "Curves: VALUE / max within same fitness function (0.78 vs max 0.84 → 0.93, not forced to 1.0). "
        "Hover: VALUE_RAW and VALUE_PCT_OF_GROUP_MAX."
    )

    fig = px.line(
        plot_df,
        x="EPOCH",
        y="VALUE_NORM",
        color="name",
        markers=True,
        hover_data=[
            "fitness_function",
            "selection_method",
            "crossover_method",
            "VALUE_RAW",
            "VALUE_PCT_OF_GROUP_MAX",
        ],
        labels={"VALUE_NORM": "Ratio to group max (0-1)", "EPOCH": "Epoch"},
        title="Fitness per Epoch (ratio to group max)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_method_impact(experiments_df: pd.DataFrame) -> None:
    st.subheader("Method Impact Summary")
    if experiments_df.empty:
        st.info("Run or import at least one experiment.")
        return

    latest_per_exp = experiments_df.sort_values("EPOCH").groupby("name", as_index=False).tail(1)
    latest_per_exp = add_normalized_final_fitness(latest_per_exp)

    st.caption(
        "Bars: VALUE / max in same fitness function (e.g. 0.78 → 93% if group max is 0.84). "
        "Only the true group maximum reaches 1.0."
    )

    c1, c2 = st.columns(2)
    with c1:
        fig_fitness = px.bar(
            latest_per_exp,
            x="fitness_function",
            y="VALUE_NORM",
            color="name",
            barmode="group",
            hover_data=["VALUE_RAW", "VALUE_PCT_OF_GROUP_MAX", "selection_method", "crossover_method"],
            labels={"VALUE_NORM": "Normalized vs group max (0-1)"},
            title="Final Fitness by Fitness Function (normalized per type)",
        )
        st.plotly_chart(fig_fitness, use_container_width=True)
    with c2:
        latest_per_exp["selection_crossover"] = (
            latest_per_exp["selection_method"] + " + " + latest_per_exp["crossover_method"]
        )
        fig_combo = px.bar(
            latest_per_exp,
            x="selection_crossover",
            y="VALUE_NORM",
            color="name",
            barmode="group",
            hover_data=["VALUE_RAW", "VALUE_PCT_OF_GROUP_MAX", "fitness_function"],
            labels={"VALUE_NORM": "Normalized vs group max (0-1)"},
            title="Final Fitness by Selection/Crossover (normalized per fitness type)",
        )
        st.plotly_chart(fig_combo, use_container_width=True)


def render_profiling(experiments: List[Experiment]) -> None:
    st.subheader("Profiling Comparison")
    profiling_frames = []
    runtime_rows = []

    for exp in experiments:
        runtime_rows.append({"Experiment": exp.name, "Metric": "RuntimeSeconds", "Value": exp.runtime_seconds})
        if exp.profiling_csv_path:
            profile_path = PROJECT_ROOT / exp.profiling_csv_path
            profile_df = read_profiling_csv(profile_path)
            if not profile_df.empty:
                profile_df = profile_df.copy()
                profile_df["Experiment"] = exp.name
                profiling_frames.append(profile_df)

    runtime_df = pd.DataFrame(runtime_rows)
    if not runtime_df.empty:
        fig_runtime = px.bar(runtime_df, x="Experiment", y="Value", title="Total Runtime per Experiment (seconds)")
        st.plotly_chart(fig_runtime, use_container_width=True)

    if profiling_frames:
        merged = pd.concat(profiling_frames, ignore_index=True)
        expected_columns = {"stage", "seconds"}
        if expected_columns.issubset(set(merged.columns)):
            fig_stage = px.bar(
                merged,
                x="stage",
                y="seconds",
                color="Experiment",
                barmode="group",
                title="Stage Profiling (expects columns: stage,seconds)",
            )
            st.plotly_chart(fig_stage, use_container_width=True)
        else:
            st.warning(
                "Profiling CSV files were loaded, but expected columns `stage` and `seconds` were not found."
            )
            st.dataframe(merged.head(50), use_container_width=True)
    else:
        st.info("Attach profiling CSV when creating an experiment to populate profiling charts.")


def build_experiments_dataframe(experiments: List[Experiment]) -> pd.DataFrame:
    rows = []
    for exp in experiments:
        csv_path = PROJECT_ROOT / exp.ga_csv_path
        df = read_ga_csv(csv_path)
        if df.empty:
            continue
        df["name"] = exp.name
        df["fitness_function"] = exp.fitness_function
        df["selection_method"] = exp.selection_method
        df["crossover_method"] = exp.crossover_method
        rows.append(df)

    if not rows:
        return pd.DataFrame(columns=["EPOCH", "VALUE", "name", "fitness_function", "selection_method", "crossover_method"])
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    st.set_page_config(page_title="GA Experiment Dashboard", layout="wide")
    ensure_data_dir()

    st.title("Genetic Algorithm UI and Experiment Dashboard")
    st.caption(
        "Configure parameters, run the C++ GA executable, and compare fitness/crossover/selection/profiling impact."
    )

    settings = load_settings(SETTINGS_PATH)
    updated_settings = sidebar_settings_form(settings)
    experiments = load_registry()

    st.markdown("### 1) Run New Experiment")
    col_a, col_b = st.columns(2)

    with col_a:
        experiment_name = st.text_input("Experiment name", value=f"Experiment {len(experiments) + 1}")
        executable_default = str(BUILD_DIR / "Release" / "ChronoProject_FinalGA.exe")
        executable_path_raw = st.text_input("GA executable path", value=executable_default)
        fitness_function = st.selectbox(
            "Fitness function label",
            list(FITNESS_OPTIONS.keys()),
            index=int(updated_settings.get("FITNESS_TYPE", 0)),
        )
    with col_b:
        selection_method = st.selectbox(
            "Selection method label",
            list(SELECTION_OPTIONS.keys()),
            index=int(updated_settings.get("SELECTION_TYPE", 0)),
        )
        crossover_method = st.selectbox(
            "Crossover method label",
            list(CROSSOVER_OPTIONS.keys()),
            index=int(updated_settings.get("CROSSOVER_TYPE", 0)),
        )
        impact_notes = st.text_area("Impact notes", placeholder="Why this variant should improve performance/results.")

    profiling_upload = st.file_uploader("Optional profiling CSV (columns: stage,seconds)", type=["csv"])
    run_clicked = st.button("Run GA and Save Experiment", type="primary")

    if run_clicked:
        run_settings = updated_settings.copy()
        run_settings["FITNESS_TYPE"] = FITNESS_OPTIONS[fitness_function]
        run_settings["SELECTION_TYPE"] = SELECTION_OPTIONS[selection_method]
        run_settings["CROSSOVER_TYPE"] = CROSSOVER_OPTIONS[crossover_method]
        write_settings(SETTINGS_PATH, run_settings)
        executable_path = Path(executable_path_raw)

        if not executable_path.exists():
            st.error(
                "Executable not found. Build the C++ project first or set a valid executable path."
            )
        else:
            with st.spinner("Running GA executable..."):
                started = time.perf_counter()
                process = run_ga(executable_path, BUILD_DIR)
                elapsed = time.perf_counter() - started

            if process.returncode != 0:
                st.error(f"GA run failed (exit code {process.returncode}).")
                st.code(process.stderr if process.stderr else process.stdout)
            else:
                if not OUTPUT_CSV.exists():
                    st.error("GA finished but individual_values.csv was not found.")
                else:
                    exp_id = next_experiment_id(experiments)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ga_filename = f"{exp_id}_{timestamp}_individual_values.csv"
                    saved_ga_path = copy_into_data(OUTPUT_CSV, ga_filename)

                    profiling_relative = ""
                    if profiling_upload is not None:
                        profiling_filename = f"{exp_id}_{timestamp}_profiling.csv"
                        saved_profile_path = save_uploaded_file(profiling_upload, profiling_filename)
                        profiling_relative = str(saved_profile_path.relative_to(PROJECT_ROOT))

                    new_experiment = Experiment(
                        experiment_id=exp_id,
                        name=experiment_name.strip() or exp_id,
                        created_at=datetime.now().isoformat(timespec="seconds"),
                        source="run",
                        fitness_function=fitness_function,
                        selection_method=selection_method,
                        crossover_method=crossover_method,
                        impact_notes=impact_notes.strip(),
                        ga_csv_path=str(saved_ga_path.relative_to(PROJECT_ROOT)),
                        profiling_csv_path=profiling_relative,
                        runtime_seconds=round(elapsed, 4),
                    )
                    experiments.append(new_experiment)
                    save_registry(experiments)

                    st.success(f"Experiment saved: {new_experiment.name}")
                    if process.stdout:
                        st.text_area("Run output", process.stdout, height=130)

    st.markdown("### 2) Import Existing Experiment CSV")
    imp_col1, imp_col2, imp_col3 = st.columns(3)
    with imp_col1:
        import_name = st.text_input("Imported experiment name", value="")
        import_fitness = st.selectbox("Imported fitness label", list(FITNESS_OPTIONS.keys()), key="imp_fit")
    with imp_col2:
        import_selection = st.selectbox("Imported selection label", list(SELECTION_OPTIONS.keys()), key="imp_sel")
        import_crossover = st.selectbox("Imported crossover label", list(CROSSOVER_OPTIONS.keys()), key="imp_cross")
    with imp_col3:
        imported_ga_file = st.file_uploader("Upload GA values CSV", type=["csv"], key="ga_upload")
        imported_profile_file = st.file_uploader("Upload profiling CSV (optional)", type=["csv"], key="profile_upload")

    if st.button("Save Imported Experiment"):
        if imported_ga_file is None:
            st.error("Please upload a GA values CSV first.")
        else:
            exp_id = next_experiment_id(experiments)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ga_filename = f"{exp_id}_{timestamp}_imported_values.csv"
            ga_path = save_uploaded_file(imported_ga_file, ga_filename)

            profiling_relative = ""
            if imported_profile_file is not None:
                profile_filename = f"{exp_id}_{timestamp}_imported_profile.csv"
                profile_path = save_uploaded_file(imported_profile_file, profile_filename)
                profiling_relative = str(profile_path.relative_to(PROJECT_ROOT))

            new_experiment = Experiment(
                experiment_id=exp_id,
                name=import_name.strip() or f"Imported {exp_id}",
                created_at=datetime.now().isoformat(timespec="seconds"),
                source="import",
                fitness_function=import_fitness,
                selection_method=import_selection,
                crossover_method=import_crossover,
                impact_notes="Imported data.",
                ga_csv_path=str(ga_path.relative_to(PROJECT_ROOT)),
                profiling_csv_path=profiling_relative,
                runtime_seconds=0.0,
            )
            experiments.append(new_experiment)
            save_registry(experiments)
            st.success(f"Imported experiment saved: {new_experiment.name}")

    st.markdown("### 3) Graphs")
    st.caption(
        "Charts: ratio to group max per fitness function (display only). "
        "Re-run GA after ProductHeadroom change for new C++ scale (~0–100)."
    )
    df = build_experiments_dataframe(experiments)
    render_ga_comparison(df)
    render_method_impact(df)
    render_profiling(experiments)

    if experiments:
        st.markdown("### 4) Experiment Registry")
        display_df = pd.DataFrame([asdict(exp) for exp in experiments]).sort_values("created_at", ascending=False)
        st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
