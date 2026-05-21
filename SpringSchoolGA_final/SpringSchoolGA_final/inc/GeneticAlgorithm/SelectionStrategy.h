#pragma once

#include <map>
#include <memory>
#include <vector>

#include <GeneticAlgorithm/GATypes.h>
#include <GeneticAlgorithm/IIndividual.h>

struct SelectionContext
{
	std::vector<std::shared_ptr<IIndividual>>& workingPopulation;
	std::map<IIndividual*, double>& fitnessValues;
	size_t populationSize;
};

class SelectionStrategy
{
public:
	static void Selection(SelectionContext& context, SelectionType type);

private:
	static void SelectionRoulette(SelectionContext& context);
	static void SelectionTournament(SelectionContext& context, int tournamentSize = 3);
};
