#!/usr/bin/env bash
set -e
#
# test-runner.sh runs a the entire ARTIC field bioinformatics pipeline using a small set
# of data (the Mayinga barcode from an Ebola amplicon library sequenced on a flongle).
#
# full data available: http://artic.s3.climb.ac.uk/run-folders/EBOV_Amplicons_flongle.tar.gz
#
# usage:
#       bash run_1.sh [medaka|nanopolish]
#
#   specify either medaka or nanopolish to run the respective workflow of the pipeline
#
###########################################################################################
# Setup the data, commands and the testing function.

# data
inputData="/home/ngs/MinIon_runs/210727SARS-C0V-2_Exp_10/no_sample/20210727_1555_MN33730_FAP84922_0ad686b7/fastq_pass/barcode12"
#inputData="/home/nanopore/fieldbioinformatics/test-data/fastq_pass/barcode06"
outputData="/home/ngs/MinIon_runs/210727SARS-C0V-2_Exp_10/no_sample/20210727_1555_MN33730_FAP84922_0ad686b7/fastq_pass/barcode12"
primerSchemes="/home/ngs/fieldbioinformatics/primer-schemes"
primerScheme="nCoV-2019/V1200"
prefix="NC"
barcode="12"
threads=5
#downloadCmd="wget http://artic.s3.climb.ac.uk/run-folders/EBOV_Amplicons_flongle.tar.gz"
#extractCmd="tar -vxzf EBOV_Amplicons_flongle.tar.gz"

# pipeline commands
## nanopolish workflow specific
gatherCmd_n="artic gather \
        --min-length 400 \
        --max-length 1200 \
        --prefix ${prefix} \
        --directory ${inputData} \
        --fast5-directory ${inputData}/fastq_pass"

demuxCmd_n="artic demultiplex \
            --threads ${threads} \
            ${prefix}_fastq_pass.fastq"

minionCmd_n="artic minion \
                --normalise 200 \
                --threads ${threads} \
                --scheme-directory ${primerSchemes} \
                --read-file ${prefix}_fastq_pass-barcode${barcode}.fastq \
                --fast5-directory ${inputData}/fast5_pass \
                --sequencing-summary ${inputData}/sequencing_summary_FAP33325_ac8ca151.txt \
                ${primerScheme} \
                ${prefix}"

## medaka workflow specific
gatherCmd_m="artic gather \
        --min-length 400 \
        --max-length 1200 \
        --prefix ${prefix} \
        --directory ${inputData} \
        --no-fast5s"

demuxCmd_m="artic demultiplex \
            --threads ${threads} \
            ${prefix}_fastq_pass.fastq"

guppyplexCmd_m="artic guppyplex \
        --min-length 400 \
        --max-length 1200 \
        --prefix ${prefix} \
        --directory ./ \
        --output ${prefix}_guppyplex_fastq_pass-barcode${barcode}.fastq"

minionCmd_m="artic minion \
            --normalise 200 \
            --threads ${threads} \
            --scheme-directory ${primerSchemes} \
            --read-file ${prefix}_guppyplex_fastq_pass-barcode${barcode}.fastq \
            --medaka \
            --medaka-model r941_min_high_g351 \
            ${primerScheme} \
            ${prefix}"

# colours
NC='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'

# cmdTester is function to run a command and check for failure
function cmdTester {
    echo "###########################################################################################"
    echo -e "${BLUE}Running:${NC} $*"
    echo
    "$@"
    echo
    local status=$?
    if [ $status -ne 0 ]
    then
        echo -e "${RED}FAIL${NC}" >&2
        exit $status
    else
        echo -e "${GREEN}PASS${NC}" >&2
    fi
    echo
    return
}

###########################################################################################
# Run the tests.

# check that nanopolish or medaka is specified
if [ "$1" == "nanopolish" ] || [ "$1" == "medaka" ]; then
    echo -e "${BLUE}Starting tests...${NC}"
    echo -e "${BLUE} - using the $1 workflow${NC}"
    echo
else
    echo "please specify medaka or nanopolish"
    echo "./run.sh [medaka|nanopolish]"
    exit 1
fi

# setup a tmp directory to work in
#mkdir  ${inputData}/${prefix} && cd ${inputData}/${prefix} || exit
mkdir  ${outputData}/${prefix} && cd ${outputData}/${prefix} || exit
# download the data
#echo "downloading the test data..."
#cmdTester $downloadCmd
#cmdTester $extractCmd

# run the correct workflow
echo "running the pipeline..."
if [ "$1" == "nanopolish" ]
then

    # collect the reads
    cmdTester $gatherCmd_n

    # demultiplex
    cmdTester $demuxCmd_n

    # run the core pipeline with nanopolish
    cmdTester $minionCmd_n
else

    # collect the reads
    cmdTester $gatherCmd_m

    # demultiplex
    cmdTester $demuxCmd_m

    # guppyplex
    cmdTester $guppyplexCmd_m

    # run the core pipeline with medaka
    cmdTester $minionCmd_m
fi

###########################################################################################
# Check the output and clean up.

# check output created
echo -e "${BLUE}Checking output...${NC}"
if test -f "${prefix}.consensus.fasta"
then
    echo -e "${GREEN} - consensus found${NC}"
else
    echo -e "${RED} - no consensus found${NC}"
    exit 1
fi

# cleanup
#cd .. && rm -r tmp
echo -e "${BLUE}Done.${NC}"
