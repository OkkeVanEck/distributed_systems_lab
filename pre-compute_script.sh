#!/usr/bin/env bash
set -e

DATASETS=("kgs" "wiki-Talk" "cit-Patents")


case "$1" in
# Get data and setup KaHIP.
"setup_env")
    ./manage.sh get_data
    ./manage.sh extract_data
    ./manage.sh get_KaHIP
    ./manage.sh build_KaHIP
    ;;
# Get data.
"get_data")
    ./manage.sh get_data
    ./manage.sh extract_data
    ;;
# Get data and setup KaHIP.
"create_partitions")
    sizes=(2 4 8 16)

    for ds in "${DATASETS[@]}"; do
        echo "Creating partitions for ${ds}.."
        for i in "${sizes[@]}"; do
            ./manage.sh create_partitions "${ds}" "${i}" &
        done
    done
    wait
    ;;
# Create jobs.
"create_jobs")
    for ds in "${DATASETS[@]}"; do
        echo "Creating jobs for ${ds}.."

        # Scalability jobs.
        # Halted down 0.4
        ./manage.sh create_job "${ds}_scala_halted_04_3_true_true_01" halted_forest_fire.py 0.4 "${ds}" 3 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_halted_04_5_true_true_01" halted_forest_fire.py 0.4 "${ds}" 5 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_halted_04_9_true_true_01" halted_forest_fire.py 0.4 "${ds}" 9 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_halted_04_17_true_true_01" halted_forest_fire.py 0.4 "${ds}" 17 120 True True 0.1

        # Wild down 0.4
        ./manage.sh create_job "${ds}_scala_wild_04_3_true_true_01" wild_forest_fire.py 0.4 "${ds}" 3 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_wild_04_5_true_true_01" wild_forest_fire.py 0.4 "${ds}" 5 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_wild_04_9_true_true_01" wild_forest_fire.py 0.4 "${ds}" 9 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_wild_04_17_true_true_01" wild_forest_fire.py 0.4 "${ds}" 17 120 True True 0.1

        # Halted up 2
        ./manage.sh create_job "${ds}_scala_halted_2_3_true_true_01" halted_forest_fire.py 2 "${ds}" 3 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_halted_2_5_true_true_01" halted_forest_fire.py 2 "${ds}" 5 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_halted_2_9_true_true_01" halted_forest_fire.py 2 "${ds}" 9 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_halted_2_17_true_true_01" halted_forest_fire.py 2 "${ds}" 17 120 True True 0.1

        # Wild up 2
        ./manage.sh create_job "${ds}_scala_wild_2_3_true_true_01" wild_forest_fire.py 2 "${ds}" 3 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_wild_2_5_true_true_01" wild_forest_fire.py 2 "${ds}" 5 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_wild_2_9_true_true_01" wild_forest_fire.py 2 "${ds}" 9 120 True True 0.1
        ./manage.sh create_job "${ds}_scala_wild_2_17_true_true_01" wild_forest_fire.py 2 "${ds}" 17 120 True True 0.1

        # Stitching & Connectivity
        # Connectivity changes.
        ./manage.sh create_job "${ds}_sc_halted_3_5_true_false_01" halted_forest_fire.py 3 "${ds}" 5 120 True False 0.1
        ./manage.sh create_job "${ds}_sc_halted_3_5_true_false_001" halted_forest_fire.py 3 "${ds}" 5 120 True False 0.01
        ./manage.sh create_job "${ds}_sc_halted_3_5_false_false_0" halted_forest_fire.py 3 "${ds}" 5 120

        # Stitching topology changes.
        ./manage.sh create_job "${ds}_sc_halted_3_5_true_true_01" halted_forest_fire.py 3 "${ds}" 5 120 True True 0.1
        ./manage.sh create_job "${ds}_sc_wild_3_5_false_false_0" wild_forest_fire.py 3 "${ds}" 5 120 False False 0.0
        ./manage.sh create_job "${ds}_sc_wild_3_5_true_true_01" wild_forest_fire.py 3 "${ds}" 5 120 True True 0.1
        ./manage.sh create_job "${ds}_sc_wild_3_5_true_false_01" wild_forest_fire.py 3 "${ds}" 5 120 True False 0.1
    done
    ;;
# Run all jobs.
"run_jobs")
    for ds in "${DATASETS[@]}"; do
        echo "Running jobs for ${ds}.."

        # Scalability jobs.
        # Halted down 0.4
        ./manage.sh run_job "${ds}_scala_halted_04_3_true_true_01"
        ./manage.sh run_job "${ds}_scala_halted_04_5_true_true_01"
        ./manage.sh run_job "${ds}_scala_halted_04_9_true_true_01"
        ./manage.sh run_job "${ds}_scala_halted_04_17_true_true_01"

        # Wild down 0.4
        ./manage.sh run_job "${ds}_scala_wild_04_3_true_true_01"
        ./manage.sh run_job "${ds}_scala_wild_04_5_true_true_01"
        ./manage.sh run_job "${ds}_scala_wild_04_9_true_true_01"
        ./manage.sh run_job "${ds}_scala_wild_04_17_true_true_01"

        # Halted up 2
        ./manage.sh run_job "${ds}_scala_halted_2_3_true_true_01"
        ./manage.sh run_job "${ds}_scala_halted_2_5_true_true_01"
        ./manage.sh run_job "${ds}_scala_halted_2_9_true_true_01"
        ./manage.sh run_job "${ds}_scala_halted_2_17_true_true_01"

        # Wild up 2
        ./manage.sh run_job "${ds}_scala_wild_2_3_true_true_01"
        ./manage.sh run_job "${ds}_scala_wild_2_5_true_true_01"
        ./manage.sh run_job "${ds}_scala_wild_2_9_true_true_01"
        ./manage.sh run_job "${ds}_scala_wild_2_17_true_true_01"

        # Stitching & Connectivity
        # Connectivity changes.
        ./manage.sh run_job "${ds}_sc_halted_3_5_true_false_01"
        ./manage.sh run_job "${ds}_sc_halted_3_5_true_false_001"
        ./manage.sh run_job "${ds}_sc_halted_3_5_false_false_0"

        # Stitching topology changes.
        ./manage.sh run_job "${ds}_sc_halted_3_5_true_true_01"
        ./manage.sh run_job "${ds}_sc_wild_3_5_false_false_0"
        ./manage.sh run_job "${ds}_sc_wild_3_5_true_true_01"
        ./manage.sh run_job "${ds}_sc_wild_3_5_true_false_01"
    done
    ;;
# Create jobs.
"compute_properties")
    for ds in "${DATASETS[@]}"; do
        echo "Computing properties for ${ds}.."

        # Scalability jobs.
        # Halted down 0.4
        ./manage.sh compute_properties "${ds}_scala_halted_04_3_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_halted_04_5_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_halted_04_9_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_halted_04_17_true_true_01" &

        # Wild down 0.4
        ./manage.sh compute_properties "${ds}_scala_wild_04_3_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_wild_04_5_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_wild_04_9_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_wild_04_17_true_true_01" &

        # Halted up 2
        ./manage.sh compute_properties "${ds}_scala_halted_2_3_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_halted_2_5_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_halted_2_9_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_halted_2_17_true_true_01" &

        # Wild up 2
        ./manage.sh compute_properties "${ds}_scala_wild_2_3_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_wild_2_5_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_wild_2_9_true_true_01" &
        ./manage.sh compute_properties "${ds}_scala_wild_2_17_true_true_01" &

        # Stitching & Connectivity
        # Connectivity changes.
        ./manage.sh compute_properties "${ds}_sc_halted_3_5_true_false_01" &
        ./manage.sh compute_properties "${ds}_sc_halted_3_5_true_false_001" &
        ./manage.sh compute_properties "${ds}_sc_halted_3_5_false_false_0" &

        # Stitching topology changes.
        ./manage.sh compute_properties "${ds}_sc_halted_3_5_true_true_01" &
        ./manage.sh compute_properties "${ds}_sc_wild_3_5_false_false_0" &
        ./manage.sh compute_properties "${ds}_sc_wild_3_5_true_true_01" &
        ./manage.sh compute_properties "${ds}_sc_wild_3_5_true_false_01" &
        wait
    done
    ;;
# Catch all for parse errors.
*)
    echo "No command detected from first argument.."
    ;;
esac
