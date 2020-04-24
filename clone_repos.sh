#!/bin/bash

set -e # abort upon error

declare -a paths=(
	# Mohamed und co
	"https://github.com/homalg-project/homalg_project"
	"https://github.com/homalg-project/AlgebraicThomas"
	"https://github.com/homalg-project/ArangoDBInterface"
	"https://github.com/homalg-project/Bialgebroids"
	"https://github.com/homalg-project/Blocks"
	"https://github.com/homalg-project/CategoryConstructor"
	"https://github.com/homalg-project/CategoriesWithAmbientObjects"
	"https://github.com/homalg-project/CatReps"
	"https://github.com/homalg-project/D-Modules"
	"https://github.com/homalg-project/HomalgProject.jl"
	"https://github.com/homalg-project/IntrinsicCategories"
	"https://github.com/homalg-project/IntrinsicModules"
	"https://github.com/homalg-project/InternalModules"
	"https://github.com/homalg-project/FunctorCategories"
	"https://github.com/homalg-project/GradedCategories"
	"https://github.com/homalg-project/LazyCategories"
	"https://github.com/homalg-project/LessGenerators"
	"https://github.com/homalg-project/LoopIntegrals"
	"https://github.com/homalg-project/Locales"
	"https://github.com/homalg-project/MatroidGeneration"
	"https://github.com/homalg-project/ParallelizedIterators"
	"https://github.com/homalg-project/PrimaryDecomposition"
	"https://github.com/homalg-project/Sheaves"
	"https://github.com/homalg-project/SingularForHomalg"
	"https://github.com/homalg-project/SubcategoriesForCAP"
	"https://github.com/homalg-project/Toposes"
	"https://github.com/homalg-project/ZariskiFrames"

	# Sebastian und co
	"https://github.com/homalg-project/CAP_project"
	"https://github.com/homalg-project/KnopCategoriesForCAP"

	# Kamal und co
	"https://github.com/homalg-project/QuotientCategories"
	"https://github.com/homalg-project/StableCategories"
	"https://github.com/homalg-project/FrobeniusCategories"
	"https://github.com/homalg-project/ComplexesCategories"
	"https://github.com/homalg-project/Bicomplexes"
	"https://github.com/homalg-project/HomotopyCategories"
	"https://github.com/homalg-project/DerivedCategories"
	"https://github.com/homalg-project/ModelCategories"
	"https://github.com/homalg-project/BBGG"
	"https://github.com/homalg-project/NConvex"
	#"https://github.com/homalg-project/CddInterface"
	"https://github.com/homalg-project/TriangulatedCategories"

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
