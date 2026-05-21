#pragma once

#include <vector>
#include <math.h>
#include <iostream>

#include <fea/ChMesh.h>

#include <GeneticAlgorithm/IIndividual.h>
#include <GeneticAlgorithm/GATypes.h>

#include <GraphicalObjects/Building.h>

#include <Services/constants.h>
#include <Services/AlgorithmSettings.h>
#include <Services/RandomNumbersGenerator.h>

#include <System/ConfigureSystem.h>

class Individual : public IIndividual
{
	friend class FitnessStrategy;

public:
	Individual(int sizeOx, int sizeOy, int sizeOz, double elementSize);
	Individual(int sizeOx, int sizeOy, int sizeOz, double elementSize, const std::vector<bool>& cubesExistence);

	Individual(const Individual& another);
	Individual(Individual&& another) noexcept;

	Individual& operator=(const Individual& another);
	Individual& operator=(Individual&& another) noexcept;

	~Individual() = default;

	void SetMaximStress(double maximStress);
	void SetFitnessType(FitnessType fitnessType);
	void SetCrossoverType(CrossoverType crossoverType);

	const std::shared_ptr<Building> GetBuilding() const;

	double Evaluate() override;

	void Crossover(IIndividual& other) override;
	void Mutation(double mutationProbability) override;

	bool operator==(const Individual& other) const;

	friend std::ostream& operator<<(std::ostream& out, const Individual& individual);

	static std::shared_ptr<Building> CreateBuildingFromDetails(int sizeOx, int sizeOy, int sizeOz,
		double elementSize, const std::vector<bool>& cubesExistence);

	double GetMaximStress() const;
	int GetNumberOfRemovedElements() const;
	int GetTotalGeneCount() const;
	const std::vector<bool>& GetCubesExistence() const;
	void ApplyCubesExistence(const std::vector<bool>& cubesExistence);

	double SimulateAndGetMaximStress();

private:
	bool IsOnTopLayer(size_t possition);

private:
	std::shared_ptr<Building> m_building;

	double m_maximStress;
	int m_sizeOx;
	int m_sizeOy;
	int m_sizeOz;
	double m_elementSize;

	FitnessType m_fitnessType;
	CrossoverType m_crossoverType;

	std::vector<bool> m_initialGenes;
};
