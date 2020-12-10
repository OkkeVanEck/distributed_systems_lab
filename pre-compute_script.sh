#!/usr/bin/env bash
set -e


case "$1" in
# Get data and setup KaHIP.
"setup_env")
    ./manage.sh get_data
    ./manage.sh extract_data
    ./manage.sh get_KaHIP
    ./manage.sh build_KaHIP
    ;;
# Get data and setup KaHIP.
"create_partitions")
    sizes=(3 5 9 17)

    for i in "${sizes[@]}"; do
        ./manage.sh create_partitions kgs "${i}" &
    done
    wait
    ;;
# Create jobs.
"create_jobs")
    # Stitching & Connectivity
    # Halted up 3 kgs 4 stitch=True, Conn=0.1, Ring=False
    ./manage.sh create_job sc_halted_3_4_true_false_01 halted_forest_fire.py 3 kgs 4 60 True False 0.1
    # Halted up 3 kgs 4 stitch=True, Conn=0.01, Ring=False
    ./manage.sh create_job sc_halted_3_4_true_false_001 halted_forest_fire.py 3 kgs 4 60 True False 0.01
    # Halted up 3 kgs 4 stitch=False, Conn=def, Ring=def
    ./manage.sh create_job sc_halted_3_4_false_false_0 halted_forest_fire.py 3 kgs 4 60

    # Scalability
    # Halted down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_04_3_true_true_01 halted_forest_fire.py 0.4 kgs 3 60 True True 0.1
    # Halted down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_04_5_true_true_01 halted_forest_fire.py 0.4 kgs 5 60 True True 0.1
    # Halted down 0.4 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_04_9_true_true_01 halted_forest_fire.py 0.4 kgs 9 120 True True 0.1
    # Halted down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_04_17_true_true_01 halted_forest_fire.py 0.4 kgs 17 120 True True 0.1

    # Wild down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_wild_04_3_true_true_01 wild_forest_fire.py 0.4 kgs 3 60 True True 0.1
    # Wild down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_wild_04_5_true_true_01 wild_forest_fire.py 0.4 kgs 5 60 True True 0.1
    # Wild down 0.4kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_wild_04_9_true_true_01 wild_forest_fire.py 0.4 kgs 9 120 True True 0.1
    # Wild down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_wild_04_17_true_true_01 wild_forest_fire.py 0.4 kgs 17 120 True True 0.1

    # Halted up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_2_3_true_true_01 halted_forest_fire.py 2 kgs 3 60 True True 0.1
    # Halted up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_2_5_true_true_01 halted_forest_fire.py 2 kgs 5 60 True True 0.1
    # Halted up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_2_9_true_true_01 halted_forest_fire.py 2 kgs 9 120 True True 0.1
    # Halted up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job scala_halted_2_17_true_true_01 halted_forest_fire.py 2 kgs 17 120 True True 0.1

    # Wild up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job wild_halted_2_3_true_true_01 wild_forest_fire.py 2 kgs 3 60 True True 0.1
    # Wild up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job wild_halted_2_5_true_true_01 wild_forest_fire.py 2 kgs 5 60 True True 0.1
    # Wild up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job wild_halted_2_9_true_true_01 wild_forest_fire.py 2 kgs 9 120 True True 0.1
    # Wild up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh create_job wild_halted_2_17_true_true_01 wild_forest_fire.py 2 kgs 17 120 True True 0.1
    ;;
# Create jobs.
"run_jobs")
    # Scalability
    # Halted down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_3_true_true_01
    # Halted down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_5_true_true_01
    sleep 10m
    # Halted down 0.4 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_9_true_true_01
    sleep 10m
    # Halted down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_17_true_true_01

    sleep 10m

    # Wild down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_3_true_true_01
    # Wild down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_5_true_true_01
    sleep 10m
    # Wild down 0.4kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_9_true_true_01
    sleep 10m
    # Wild down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_17_true_true_01

    sleep 10m

    # Halted up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_3_true_true_01
    # Halted up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_5_true_true_01
    sleep 10m
    # Halted up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_9_true_true_01
    sleep 10m
    # Halted up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_17_true_true_01

    sleep 10m

    # Wild up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_3_true_true_01
    # Wild up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_5_true_true_01
    sleep 10m
    # Wild up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_9_true_true_01
    sleep 10m
    # Wild up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_17_true_true_01

    sleep 10m

    # Stitching & Connectivity
    # Halted up 3 kgs 4 stitch=True, Conn=0.1, Ring=False
    ./manage.sh run_job sc_halted_3_4_true_false_01
    # Halted up 3 kgs 4 stitch=True, Conn=0.01, Ring=False
    ./manage.sh run_job sc_halted_3_4_true_false_001
    # Halted up 3 kgs 4 stitch=False, Conn=def, Ring=def
    ./manage.sh run_job sc_halted_3_4_false_false_0
    ;;
# Okke Jobs.
"run_okke")
    # Scalability
    # Halted down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_3_true_true_01
    # Halted down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_5_true_true_01
    sleep 10m
    # Halted down 0.4 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_9_true_true_01
    sleep 10m
    # Halted down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_17_true_true_01

    sleep 10m

    # Wild down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_3_true_true_01
    # Wild down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_5_true_true_01
    sleep 10m
    # Wild down 0.4kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_9_true_true_01
    sleep 10m
    # Wild down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_17_true_true_01

    sleep 10m

    # Halted up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_3_true_true_01
    # Halted up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_5_true_true_01
    sleep 10m
    # Halted up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_9_true_true_01
    sleep 10m
    # Halted up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_17_true_true_01

    sleep 10m

    # Wild up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_3_true_true_01
    # Wild up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_5_true_true_01
    sleep 10m
    # Wild up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_9_true_true_01
    sleep 10m
    # Wild up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_17_true_true_01

    sleep 10m

    # Stitching & Connectivity
    # Halted up 3 kgs 4 stitch=True, Conn=0.1, Ring=False
    ./manage.sh run_job sc_halted_3_4_true_false_01
    # Halted up 3 kgs 4 stitch=True, Conn=0.01, Ring=False
    ./manage.sh run_job sc_halted_3_4_true_false_001
    # Halted up 3 kgs 4 stitch=False, Conn=def, Ring=def
    ./manage.sh run_job sc_halted_3_4_false_false_0
    ;;
# Dennis Jobs.
"run_dennis")
    # Scalability
    # Halted down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_17_true_true_01
    sleep 10m
    # Halted down 0.4 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_9_true_true_01
    sleep 10m
    # Halted down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_5_true_true_01
    # Halted down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_04_3_true_true_01

    sleep 10m

    # Wild down 0.4 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_17_true_true_01
    sleep 10m
    # Wild down 0.4kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_9_true_true_01
    sleep 10m
    # Wild down 0.4 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_5_true_true_01
    # Wild down 0.4 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_wild_04_3_true_true_01

    sleep 10m

    # Halted up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_17_true_true_01
    sleep 10m
    # Halted up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_9_true_true_01
    sleep 10m
    # Halted up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_5_true_true_01
    # Halted up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job scala_halted_2_3_true_true_01

    sleep 10m

    # Wild up 2 kgs 17 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_17_true_true_01
    sleep 10m
    # Wild up 2 kgs 9 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_9_true_true_01
    sleep 10m
    # Wild up 2 kgs 5 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_5_true_true_01
    # Wild up 2 kgs 3 stitch=True, Conn=0.1, Ring=True
    ./manage.sh run_job wild_halted_2_3_true_true_01

    sleep 10m

    # Stitching & Connectivity
    # Halted up 3 kgs 4 stitch=True, Conn=0.1, Ring=False
    ./manage.sh run_job sc_halted_3_4_true_false_01
    # Halted up 3 kgs 4 stitch=True, Conn=0.01, Ring=False
    ./manage.sh run_job sc_halted_3_4_true_false_001
    # Halted up 3 kgs 4 stitch=False, Conn=def, Ring=def
    ./manage.sh run_job sc_halted_3_4_false_false_0
    ;;
# Catch all for parse errors.
*)
    echo "No command detected from first argument.."
    ;;
esac
