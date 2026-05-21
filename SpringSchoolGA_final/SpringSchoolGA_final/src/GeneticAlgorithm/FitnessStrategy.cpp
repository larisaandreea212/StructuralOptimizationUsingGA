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
	const double simulatedStress = individual.SimulateAndGetMaximStress();
	const double allowedMaxStress = individual.GetMaximStress();

	if (simulatedStress >= allowedMaxStress || simulatedStress < EPSILON_STRESS)
	{
		return MINIM_INDIVIDUAL_VALUE;
	}

	// fitness = (n_removed + 1)^2 * (sigma_max_allowed - sigma_simulated) / sigma_max_allowed
	const double stressHeadroom = allowedMaxStress - simulatedStress;
	const int removedElements = individual.GetNumberOfRemovedElements();
	const int totalGenes = individual.GetTotalGeneCount();

	const double massFactor = std::pow(
		static_cast<double>(removedElements + 1) / static_cast<double>(totalGenes + 1), 2);
	const double safetyFactor = stressHeadroom / allowedMaxStress;

	return 100.0 * massFactor * safetyFactor;
}

double FitnessStrategy::EvaluateWeightedSum(Individual& individual)
{
	const double simulatedStress = individual.SimulateAndGetMaximStress();
	const double allowedMaxStress = individual.GetMaximStress();

	if (simulatedStress >= allowedMaxStress || simulatedStress < EPSILON_STRESS)
	{
		return MINIM_INDIVIDUAL_VALUE;
	}

	const double wMass = 0.6;
	const double wSafety = 0.4;

	int totalGenes = individual.GetTotalGeneCount();
	int removedElements = individual.GetNumberOfRemovedElements();

	double massScore = static_cast<double>(removedElements) / static_cast<double>(totalGenes);
	double safetyScore = 1.0 - (simulatedStress / allowedMaxStress);

	return wMass * massScore + wSafety * safetyScore;
}

double FitnessStrategy::EvaluatePenalty(Individual& individual)
{
	const double simulatedStress = individual.SimulateAndGetMaximStress();
	const double allowedMaxStress = individual.GetMaximStress();

	if (simulatedStress < EPSILON_STRESS)
	{
		return MINIM_INDIVIDUAL_VALUE;
	}

	const size_t initialGeneCount = individual.m_initialGenes.size();
	if (initialGeneCount == 0)
	{
		return MINIM_INDIVIDUAL_VALUE;
	}

	double ratioRemoved = static_cast<double>(individual.GetNumberOfRemovedElements()) / static_cast<double>(initialGeneCount);
	double baseReward = 100.0 * ratioRemoved;
	double value;

	if (simulatedStress <= allowedMaxStress)
	{
		double ratioStress = (allowedMaxStress - simulatedStress) / allowedMaxStress;
		value = baseReward + (10.0 * ratioStress);
	}
	else
	{
		double violation = (simulatedStress - allowedMaxStress) / allowedMaxStress;
		value = baseReward - (200.0 * std::pow(violation, 2));
	}

	return (value < MINIM_INDIVIDUAL_VALUE) ? MINIM_INDIVIDUAL_VALUE : value;
}
