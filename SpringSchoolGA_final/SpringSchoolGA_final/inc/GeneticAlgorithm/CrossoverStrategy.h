#pragma once

#include <GeneticAlgorithm/GATypes.h>

class Individual;

class CrossoverStrategy
{
public:
	static void Crossover(Individual& first, Individual& second, CrossoverType type);

private:
	static void CrossoverSinglePoint(Individual& first, Individual& second);
	static void CrossoverUniform(Individual& first, Individual& second, double geneSwapProbability = 0.5);
};
