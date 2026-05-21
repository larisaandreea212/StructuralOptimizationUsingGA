#pragma once

enum class FitnessType
{
	ProductHeadroom = 0,
	WeightedSum = 1,
	Penalty = 2
};

enum class SelectionType
{
	Roulette = 0,
	Tournament = 1
};

enum class CrossoverType
{
	SinglePoint = 0,
	Uniform = 1
};
