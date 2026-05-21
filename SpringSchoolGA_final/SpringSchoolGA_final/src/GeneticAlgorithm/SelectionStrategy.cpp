#include <limits>

#include <GeneticAlgorithm/SelectionStrategy.h>
#include <Services/RandomNumbersGenerator.h>
#include <Services/constants.h>

void SelectionStrategy::Selection(SelectionContext& context, SelectionType type)
{
	switch (type)
	{
	case SelectionType::Tournament:
		SelectionTournament(context, 3);
		break;
	case SelectionType::Roulette:
	default:
		SelectionRoulette(context);
		break;
	}
}

void SelectionStrategy::SelectionRoulette(SelectionContext& context)
{
	std::vector<std::shared_ptr<IIndividual>> newPopulation;
	newPopulation.reserve(context.populationSize);

	std::vector<double> cumulativeProbability(context.populationSize, 0.0);
	double fitnessSum = 0.0;

	for (const auto& individual : context.workingPopulation)
	{
		fitnessSum += context.fitnessValues[individual.get()];
	}

	if (fitnessSum <= 0.0)
	{
		context.workingPopulation = context.workingPopulation;
		return;
	}

	double accumulated = 0.0;
	for (size_t index = 0; index < context.populationSize; ++index)
	{
		accumulated += context.fitnessValues[context.workingPopulation[index].get()] / fitnessSum;
		cumulativeProbability[index] = accumulated;
	}

	std::vector<double> randomNumbers = RandomNumbersGenerator::GenerateRealNumbers(
		LOWER_BOUND, UPPER_BOUND, context.populationSize);

	for (const auto& randomNumber : randomNumbers)
	{
		for (size_t index = 0; index < context.populationSize; ++index)
		{
			if (randomNumber <= cumulativeProbability[index])
			{
				newPopulation.push_back(context.workingPopulation[index]);
				break;
			}
		}
	}

	context.workingPopulation = newPopulation;
}

void SelectionStrategy::SelectionTournament(SelectionContext& context, int tournamentSize)
{
	std::vector<std::shared_ptr<IIndividual>> newPopulation;
	newPopulation.reserve(context.populationSize);

	const int lastIndex = static_cast<int>(context.populationSize) - 1;

	for (size_t selectionIndex = 0; selectionIndex < context.populationSize; ++selectionIndex)
	{
		std::shared_ptr<IIndividual> bestIndividual = nullptr;
		double bestFitness = std::numeric_limits<double>::lowest();

		for (int tournamentIndex = 0; tournamentIndex < tournamentSize; ++tournamentIndex)
		{
			int candidateIndex = RandomNumbersGenerator::GenerateIntegerNumberInRange(0, lastIndex);
			const auto& candidate = context.workingPopulation[candidateIndex];
			double candidateFitness = context.fitnessValues[candidate.get()];

			if (candidateFitness > bestFitness)
			{
				bestFitness = candidateFitness;
				bestIndividual = candidate;
			}
		}

		if (bestIndividual)
		{
			newPopulation.push_back(bestIndividual);
		}
	}

	context.workingPopulation = newPopulation;
}
