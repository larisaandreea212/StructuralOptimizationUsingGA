#include <Services/AlgorithmSettings.h>

AlgorithmSettings* AlgorithmSettings::m_instance = NULL;

AlgorithmSettings* AlgorithmSettings::GetInstance()
{
	if (!m_instance)
		m_instance = new AlgorithmSettings();

	return m_instance;
}

const int AlgorithmSettings::GetNumberOfEpochs() const
{
	return m_numbeOfEpochs;
}

const int AlgorithmSettings::GetNumberOfIndividuals() const
{
	return m_numberOfIndividuals;
}

const int AlgorithmSettings::GetOxSize() const
{
	return m_oxSize;
}

const int AlgorithmSettings::GetOySize() const
{
	return m_oySize;
}

const int AlgorithmSettings::GetOzSize() const
{
	return m_ozSize;
}

const double AlgorithmSettings::GetElementSize() const
{
	return m_elementSize;
}

const double AlgorithmSettings::GetCrossoverProbability() const
{
	return m_crossoverProbability;
}

const double AlgorithmSettings::GetMutationProbability() const
{
	return m_mutationProbability;
}

const double AlgorithmSettings::GetMaximStressAllowed() const
{
	return m_maximumStress;
}

const double AlgorithmSettings::GetYoungModulus() const
{
	return m_youngModulus;
}

const double AlgorithmSettings::GetPoissonRatio() const
{
	return m_poissonRatio;
}

const double AlgorithmSettings::GetDensity() const
{
	return m_density;
}

FitnessType AlgorithmSettings::GetFitnessType() const
{
	switch (m_fitnessType)
	{
	case 1:
		return FitnessType::WeightedSum;
	case 2:
		return FitnessType::Penalty;
	case 0:
	default:
		return FitnessType::ProductHeadroom;
	}
}

SelectionType AlgorithmSettings::GetSelectionType() const
{
	switch (m_selectionType)
	{
	case 1:
		return SelectionType::Tournament;
	case 0:
	default:
		return SelectionType::Roulette;
	}
}

CrossoverType AlgorithmSettings::GetCrossoverType() const
{
	switch (m_crossoverType)
	{
	case 1:
		return CrossoverType::Uniform;
	case 0:
	default:
		return CrossoverType::SinglePoint;
	}
}

AlgorithmSettings::AlgorithmSettings() :
	m_numbeOfEpochs{ 5 },
	m_numberOfIndividuals{ 50 },
	m_oxSize{ 10 },
	m_oySize{ 5 },
	m_ozSize{ 3 },
	m_elementSize{ 0.1 },
	m_crossoverProbability{ 0.5 },
	m_mutationProbability{ 0.01 },
	m_maximumStress{ 4.5e8 },
	m_youngModulus{ 1e21 },
	m_poissonRatio{ 0.3 },
	m_density{ 7800.0 },
	m_fitnessType{ 0 },
	m_selectionType{ 0 },
	m_crossoverType{ 0 }
{
	std::ifstream file;

	file.open(FILE_NAME_ALGORITHM_SETTINGS, std::ios::in);
	if (file.is_open())
	{
		std::string line;
		while (getline(file, line))
		{
			line.erase(std::remove_if(line.begin(), line.end(), isspace), line.end());
			auto delimiterPos = line.find("=");
			auto variable = line.substr(0, delimiterPos);
			auto value = line.substr(delimiterPos + 1);

			if (variable == "NUMBER_OF_EPOCHS")
			{
				m_numbeOfEpochs = atoi(value.c_str());
			}
			else if (variable == "NUMBER_OF_INDIVIDUALS")
			{
				m_numberOfIndividuals = atoi(value.c_str());
			}
			else if (variable == "OX_SIZE")
			{
				m_oxSize = atoi(value.c_str());
			}
			else if (variable == "OY_SIZE")
			{
				m_oySize = atoi(value.c_str());
			}
			else if (variable == "OZ_SIZE")
			{
				m_ozSize = atoi(value.c_str());
			}
			else if (variable == "ELEMENT_SIZE")
			{
				m_elementSize = std::stod(value);
			}
			else if (variable == "CROSSOVER_PROBABILITY")
			{
				m_crossoverProbability = std::stod(value);
			}
			else if (variable == "MUTATION_PROBABILITY")
			{
				m_mutationProbability = std::stod(value);
			}
			else if (variable == "MAXIM_STRESS")
			{
				m_maximumStress = std::stod(value);
			}
			else if (variable == "YOUNG_MODULUS")
			{
				m_youngModulus = std::stod(value);
			}
			else if (variable == "POISSON_RATIO")
			{
				m_poissonRatio = std::stod(value);
			}
			else if (variable == "DENSITY")
			{
				m_density = std::stod(value);
			}
			else if (variable == "FITNESS_TYPE")
			{
				m_fitnessType = atoi(value.c_str());
			}
			else if (variable == "SELECTION_TYPE")
			{
				m_selectionType = atoi(value.c_str());
			}
			else if (variable == "CROSSOVER_TYPE")
			{
				m_crossoverType = atoi(value.c_str());
			}
		}
	}
	else
	{
		std::cerr << "Could not open " + FILE_NAME_ALGORITHM_SETTINGS + " file!";
	}
}
