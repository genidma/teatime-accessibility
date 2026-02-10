#!/usr/bin/env bash
set -euo pipefail

interval=1
duration=120
topn=20
match="teatime|KCResonance|kcresonance"
outdir=""

usage() {
  cat <<'EOF'
Usage: debug/kcresonance_cpu_probe.sh [options]

Options:
  -i <seconds>   Sample interval (default: 1)
  -d <seconds>   Total duration (default: 120)
  -n <count>     Top N processes/threads per sample (default: 20)
  -m <regex>     Regex to match target process (default: teatime|KCResonance|kcresonance)
  -o <dir>       Output directory (default: debug/cpu-probe-YYYYmmdd-HHMMSS)

Example:
  debug/kcresonance_cpu_probe.sh -d 300 -i 1 -m 'teatime|KCResonance'
EOF
}

while getopts ":i:d:n:m:o:h" opt; do
  case "$opt" in
    i) interval="$OPTARG" ;;
    d) duration="$OPTARG" ;;
    n) topn="$OPTARG" ;;
    m) match="$OPTARG" ;;
    o) outdir="$OPTARG" ;;
    h) usage; exit 0 ;;
    *) usage; exit 1 ;;
  esac
done

if [ -z "$outdir" ]; then
  ts="$(date +%Y%m%d-%H%M%S)"
  outdir="debug/cpu-probe-$ts"
fi

mkdir -p "$outdir"

sysinfo="$outdir/system.txt"
{
  echo "timestamp: $(date --iso-8601=seconds)"
  echo "hostname: $(hostname)"
  echo "kernel: $(uname -a)"
  echo "cpu_count: $(getconf _NPROCESSORS_ONLN)"
  command -v lscpu >/dev/null 2>&1 && lscpu
  command -v free >/dev/null 2>&1 && free -h
  command -v git >/dev/null 2>&1 && git rev-parse --abbrev-ref HEAD || true
  command -v git >/dev/null 2>&1 && git rev-parse HEAD || true
} > "$sysinfo"

samples_csv="$outdir/top_processes.csv"
threads_txt="$outdir/threads.txt"
targets_csv="$outdir/targets.csv"

printf "timestamp,pid,ppid,pcpu,pmem,etimes,comm,args\n" > "$samples_csv"
printf "timestamp,pid,ppid,pcpu,pmem,etimes,comm,args\n" > "$targets_csv"

end=$((SECONDS + duration))

while [ $SECONDS -lt $end ]; do
  ts="$(date --iso-8601=seconds)"

  # Top processes overall
  ps -eo pid,ppid,pcpu,pmem,etimes,comm,args --sort=-pcpu \
    | head -n $((topn + 1)) \
    | tail -n +2 \
    | awk -v ts="$ts" 'BEGIN{OFS=","} {pid=$1; ppid=$2; pcpu=$3; pmem=$4; et=$5; comm=$6; $1=$2=$3=$4=$5=$6=""; sub(/^ +/,""); print ts,pid,ppid,pcpu,pmem,et,comm,$0}' \
    >> "$samples_csv"

  # Target process snapshots
  mapfile -t pids < <(pgrep -f "$match" | sort -n | uniq || true)
  for pid in "${pids[@]:-}"; do
    ps -p "$pid" -o pid=,ppid=,pcpu=,pmem=,etimes=,comm=,args= \
      | awk -v ts="$ts" 'BEGIN{OFS=","} {pid=$1; ppid=$2; pcpu=$3; pmem=$4; et=$5; comm=$6; $1=$2=$3=$4=$5=$6=""; sub(/^ +/,""); print ts,pid,ppid,pcpu,pmem,et,comm,$0}' \
      >> "$targets_csv"

    {
      echo "[$ts] pid=$pid"
      ps -L -p "$pid" -o pid,tid,pcpu,comm --sort=-pcpu | head -n $((topn + 1))
      echo
    } >> "$threads_txt"
  done

  sleep "$interval"
done

cat <<EOF
Done. Output written to: $outdir
Key files:
  $samples_csv
  $targets_csv
  $threads_txt
  $sysinfo
EOF
