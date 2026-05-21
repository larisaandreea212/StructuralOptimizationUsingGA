#include <cmath>

#include <GeneticAlgorithm/FitnessStrategy.h>
#include <GeneticAlgorithm/Individual.h>
#include <Services/constants.h>

double FitnessStrategy::Evaluate(Individual& individual, FitnessType type)
{
	switch (type)
	{
	case FitnessType::WeightedSum:
		return EvaluateWeightedSum(individual);
	case FitnessType::Penalty:
		return EvaluatePenalty(individual);
	case FitnessType::ProductHeadroom:
	default:
		return EvaluateProductHeadroom(individual);
	}
}

double FitnessStrategy::EvaluateProductHeadroom(Individual& individual)
{
	double maximStress = individual.SimulateAndGetMaximStress();

	if (maximStress >= individual.GetMaximStress() || maximStress < EPSILON_STRESS)
	{
		return MINIM_INDIVIDUAL_VALUE;
	}

	double stressHeadroom = individual.GetMaximStress() - maximStress;
	int removedElements = individual.GetNumberOfRemovedElements();

	return std::pow(removedElements + 1, 2) * stressHeadroom;
}

double FitnessStrategy::EvaluateWeightedSum(Individual& individual)
{
	double maximStress = individual.SimulateAndGetMaximStress();

	if (maximStress >= individual.GetMaximStress() || maximStress < EPSILON_STRESS)
	{
		return MINIM_INDIVIDUAL_VALUE;
	}

	const double wMass = 0.6;
	const double wSafety = 0.4;

	int totalGenes = individual.GetTotalGeneCount();
	int removedElements = individual.GetNumberOfRemovedElements();

	double massScore = static_cast<double>(removedElements) / static_cast<double>(totalGenes);
	double safetyScore = 1.0 - (maximStress / individual.GetMaximStress());

	return wMass * massScore + wSafety * safetyScore;
}

double FitnessStrategy::EvaluatePenalty(Individual& individual)
{
	double maximStress = individual.SimulateAndGetMaximStress();
	int removedElements = individual.GetNumberOfRemovedElements();

	const double penaltyLambda = 1e6;
	double baseFitness = static_cast<double>(removedElements);

	if (maximStress >= individual.GetMaximStress())
	{
		double violation = maximStress - individual.GetMaximStress();
		return (baseFitness - penaltyLambda * violation * violation) * 0.01;
	}

	if (maximStress < EPSILON_STRESS)
	{
		return MINIM_INDIVIDUAL_VALUE * 0.01;
	}

	return baseFitness * 0.01;
}
