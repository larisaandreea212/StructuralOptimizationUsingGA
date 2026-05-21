#pragma once

#include <GeneticAlgorithm/GATypes.h>

class Individual;

class FitnessStrategy
{
public:
	static double Evaluate(Individual& individual, FitnessType type);

private:
	static double EvaluateProductHeadroom(Individual& individual);
	static double EvaluateWeightedSum(Individual& individual);
	static double EvaluatePenalty(Individual& individual);
};
