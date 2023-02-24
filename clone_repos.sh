#!/bin/bash

set -e # abort upon error

declare -a paths=(
	# Mohamed und co
	"https://github.com/homalg-project/homalg_project"
	"https://github.com/homalg-project/CategoricalTowers"
	"https://github.com/homalg-project/CapAndHomalg.jl"
	"https://github.com/homalg-project/HomalgProject.jl"
	"https://github.com/homalg-project/AlgebraicThomas"
	"https://github.com/homalg-project/ArangoDBInterface"
	"https://github.com/homalg-project/Blocks"
	"https://github.com/homalg-project/D-Modules"
	"https://github.com/homalg-project/HeckeCategories"
	"https://github.com/homalg-project/LessGenerators"
	"https://github.com/homalg-project/LoopIntegrals"
	"https://github.com/homalg-project/MatroidGeneration"
	"https://github.com/homalg-project/OscarForHomalg"
	"https://github.com/homalg-project/ParallelizedIterators"
	"https://github.com/homalg-project/PrimaryDecomposition"
	"https://github.com/homalg-project/Sheaves"
	"https://github.com/homalg-project/SingularForHomalg"

	# Sebastian und co
	"https://github.com/homalg-project/CAP_project"
	"https://github.com/homalg-project/KnopCategoriesForCAP"

	# Kamal und co
	"https://github.com/homalg-project/HigherHomologicalAlgebra"
	"https://github.com/homalg-project/NConvex"
	#"https://github.com/homalg-project/CddInterface"

	# Fabian und co
	"https://github.com/homalg-project/FinSetsForCAP"
	"https://github.com/homalg-project/FinGSetsForCAP"
)

mkdir -p repos
cd repos

for rep_path in "${paths[@]}"
do
	rep_name=$(echo $rep_path| cut -d'/' -f 5)

	if [ -d ${rep_name} ]; then
		echo "${rep_name} already exists, pulling"
		cd ${rep_name}
		git fetch
		git reset --hard origin/master
		cd ..
	else
		echo "Cloning $rep_path"
		git clone ${rep_path}
	fi
done
