#include <GeneticAlgorithm/CrossoverStrategy.h>
#include <GeneticAlgorithm/Individual.h>
#include <Services/RandomNumbersGenerator.h>
#include <Services/constants.h>

void CrossoverStrategy::Crossover(Individual& first, Individual& second, CrossoverType type)
{
	switch (type)
	{
	case CrossoverType::Uniform:
		CrossoverUniform(first, second);
		break;
	case CrossoverType::SinglePoint:
	default:
		CrossoverSinglePoint(first, second);
		break;
	}
}

void CrossoverStrategy::CrossoverSinglePoint(Individual& first, Individual& second)
{
	const auto& firstGenes = first.GetCubesExistence();
	size_t numberOfGenes = firstGenes.size();

	if (numberOfGenes < 2)
	{
		return;
	}

	int cutPoint = RandomNumbersGenerator::GenerateIntegerNumberInRange(1, static_cast<int>(numberOfGenes) - 1);

	std::vector<bool> newFirstGenes = firstGenes;
	std::vector<bool> newSecondGenes = second.GetCubesExistence();

	const auto& secondGenes = second.GetCubesExistence();
	for (size_t index = cutPoint; index < numberOfGenes; ++index)
	{
		newFirstGenes[index] = secondGenes[index];
		newSecondGenes[index] = firstGenes[index];
	}

	first.ApplyCubesExistence(newFirstGenes);
	second.ApplyCubesExistence(newSecondGenes);
}

void CrossoverStrategy::CrossoverUniform(Individual& first, Individual& second, double geneSwapProbability)
{
	std::vector<bool> firstGenes = first.GetCubesExistence();
	std::vector<bool> secondGenes = second.GetCubesExistence();
	size_t numberOfGenes = firstGenes.size();

	std::vector<double> randomNumbers = RandomNumbersGenerator::GenerateRealNumbers(
		LOWER_BOUND, UPPER_BOUND, numberOfGenes);

	for (size_t index = 0; index < numberOfGenes; ++index)
	{
		if (randomNumbers[index] < geneSwapProbability)
		{
			std::swap(firstGenes[index], secondGenes[index]);
		}
	}

	first.ApplyCubesExistence(firstGenes);
	second.ApplyCubesExistence(secondGenes);
}
