import random, sys
random.seed(42)
from person import Person
from logger import Logger
from virus import Virus


class Simulation(object):
    ''' Main class that will run the herd immunity simulation program.
    Expects initialization parameters passed as command line arguments when file is run.

    Simulates the spread of a virus through a given population.  The percentage of the
    population that are vaccinated, the size of the population, and the amount of initially
    infected people in a population are all variables that can be set when the program is run.
    '''
    def __init__(self, pop_size, vacc_percentage, virus, mortality_rate, initial_infected=1):
        ''' Logger object logger records all events during the simulation.
        Population represents all Persons in the population.
        The next_person_id is the next available id for all created Persons,
        and should have a unique _id value.
        The vaccination percentage represents the total percentage of population
        vaccinated at the start of the simulation.
        You will need to keep track of the number of people currently infected with the disease.
        The total infected people is the running total that have been infected since the
        simulation began, including the currently infected people who died.
        You will also need to keep track of the number of people that have die as a result
        of the infection.

        All arguments will be passed as command-line arguments when the file is run.
        HINT: Look in the if __name__ == "__main__" function at the bottom.
        '''
        
        
        self.pop_size = pop_size # Int
        self.initial_infected = initial_infected # Int
        self.next_person_id = 0 # Int
        self.virus = virus # Virus object
        self.total_infected = 0 # Int
        self.vacc_percentage = vacc_percentage # float between 0 and 1
        self.total_dead = 0 # Int
        file_name = "{}_simulation_pop_{}_vp_{}_infected_{}.txt".format(
            virus_name, pop_size, vacc_percentage, initial_infected)
        self.logger = Logger(file_name)
        self.newly_infected = []
        self.mortality_rate = mortality_rate
        self.population = self._create_population() # List of Person objects

    def _create_population(self):
        '''This method will create the initial population.
            Args:
                initial_infected (int): The number of infected people that the simulation
                will begin with.

            Returns:
                list: A list of Person objects.

        '''
        
        
        population = []
        for uid in range(self.pop_size):
            # If we don't have enough infected people, set person to be infected
            if self.total_infected < self.initial_infected:
                population.append(Person(uid, False, self.virus))
                self.total_infected += 1
            # They are not infected
            else:
                # Randomly choose where or not they are vaccinated
                vaccinated = random.random() > self.vacc_percentage
                population.append(Person(uid, vaccinated, None))
            
        return population

            



            
            

    def _simulation_should_continue(self):
        ''' The simulation should only end if the entire population is dead
        or everyone is vaccinated.

            Returns:
                bool: True for simulation should continue, False if it should end.
        '''

        ##TIMO wrote this
        everyones_dead = True
        everyones_vaccinated = True
        noones_infected = True
        for person in self.population:
            if person.is_alive:
                everyones_dead = False
            if not person.is_vaccinated:
                everyones_vaccinated = False
            if person.infection != None:
                noones_infected = False

        return not (everyones_vaccinated or everyones_dead or noones_infected)
        


    def run(self):
        ''' This method should run the simulation until all requirements for ending
        the simulation are met.
        '''
        #peer programmed
        self.logger.write_metadata(self.pop_size, self.vacc_percentage, self.virus.name, self.mortality_rate, self.virus.repro_rate)
        time_step_counter = 1

        while self._simulation_should_continue():
            newly_infected, newly_killed = self.time_step()
            total_infected = len([p for p in self.population if p.infection is not None and p.is_alive])
            total_dead = len([p for p in self.population if not p.is_alive])
            self.logger.log_time_step(time_step_counter, newly_infected, newly_killed, total_infected, total_dead)
            time_step_counter += 1
        # round of this simulation.
        print('The simulation has ended after {} turns.'.format(time_step_counter))

    def time_step(self):
        ''' This method should contain all the logic for computing one time step
        in the simulation.

        This includes:
            1. 100 total interactions with a randon person for each infected person
                in the population
            2. If the person is dead, grab another random person from the population.
                Since we don't interact with dead people, this does not count as an interaction.
            3. Otherwise call simulation.interaction(person, random_person) and
                increment interaction counter by 1.
            '''
            ##Connor Wrote this 
        alive_people = [p for p in self.population if p.is_alive]
        infected_people = [p for p in alive_people if p.infection != None]
        newly_infected = 0
        for infectedPerson in infected_people:
            for _ in range(100):
                randomPerson = random.choice(alive_people)
                got_infected = self.interaction(infectedPerson, randomPerson)
                newly_infected += 1 if got_infected else 0
        newly_killed = 0
        for person in infected_people:
            did_die = not person.did_survive_infection(self.mortality_rate)
            newly_killed += 1 if did_die else 0
            self.logger.log_infection_survival(person, did_die)
        
        return newly_infected, newly_killed

    def interaction(self, person, random_person):
        '''This method should be called any time two living people are selected for an
        interaction. It assumes that only living people are passed in as parameters.

        Args:
            person1 (person): The initial infected person
            random_person (person): The person that person1 interacts with.
        '''
        ##connor wrote this
        assert person.is_alive == True
        assert random_person.is_alive == True

        if random_person.is_vaccinated:
            self.logger.log_interaction(person, random_person, False, True, False)
        elif random_person.infection is None:
            if random.random() <= self.virus.repro_rate:
                random_person.infection = person.infection
                self.logger.log_interaction(person, random_person, False, False, True)
                return True
            else:
                random_person.is_vaccinated = True
                self.logger.log_interaction(person, random_person, False, False, False)
        elif random_person.infection != None:
            self.logger.log_interaction(person, random_person, True, False, False)
        return False

        
        

    def _infect_newly_infected(self):
        ''' This method should iterate through the list of ._id stored in self.newly_infected
        and update each Person object with the disease. '''
        #CONNOR wrote this
        if len(self.newly_infected) > 0:
            for person in self.newly_infected:
                person.infection = self.virus
                
                self.total_infected += 1

        self.newly_infected = []



if __name__ == "__main__":
    params = sys.argv[1:]
    virus_name = str(params[0])
    repro_num = float(params[1])
    mortality_rate = float(params[2])

    pop_size = int(params[3])
    vacc_percentage = float(params[4])


    if len(params) == 6:
        initial_infected = int(params[5])
    else:
        initial_infected = 1

    virus = Virus(virus_name, repro_num, mortality_rate)
    sim = Simulation(pop_size, vacc_percentage, virus, mortality_rate, initial_infected)

    sim.run()
    
