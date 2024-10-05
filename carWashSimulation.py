import simpy
import random
import matplotlib.pyplot as plt

# Parameters (MINUTES)
minArrivalInterval = 1  # Minimum time for a customer to arrive
maxArrivalInterval = 5  # Maximum time for a customer to arrive
carWashDuration = 3  # How long it takes to wash a car
simulationTime = 50  # How long will the system be simulated
dataCollectionInterval = 1  # Collect data every 1 minute

# Data and statistics collection
carArrivalIntervals = []
queueLengths = []
waitTimes = []
carWashLaneUtilization = []

def car(env, name, carWash): # Process for a single car
    
    arrivalTime = env.now
    print(f'{name} arrived at minute {arrivalTime:.2f}.')

    # Request the car wash if available, otherwise the car will wait in line)
    with carWash.request() as request:
        yield request
        startTime = env.now
        waitTimes.append(startTime - arrivalTime)  # Record wait time
        print(f'{name} enters car wash lane at minute {startTime:.2f} (waited {startTime - arrivalTime:.2f} minutes).')
        
        # Simulate the car wash process (3 minutes)
        yield env.timeout(carWashDuration)
        print(f'{name} left the car wash lane at minute {env.now:.2f}.')

def car_arrivals(env, carWash):  # Generate cars arriving at the car wash
    carCount = 0
    lastArrivalTime = 0  # Variable to keep track of the previous car's arrival time
    while True:
        carCount += 1
        # Cars arrive randomly between 1 to 5 minutes
        arrival_interval = random.uniform(minArrivalInterval, maxArrivalInterval)
        carArrivalIntervals.append(arrival_interval)  # Store the arrival interval
        yield env.timeout(arrival_interval)
        env.process(car(env, f'Car {carCount}', carWash))

def collect_data(env, carWash):  # Collects car wash data every minute
    while True:
        queueLengths.append(len(carWash.queue))  # Record queue length
        carWashLaneUtilization.append(1 if carWash.count == 1 else 0)  # Record utilization
        yield env.timeout(dataCollectionInterval) 

env = simpy.Environment()  # Create the simulation environment
carWash = simpy.Resource(env, capacity=1)  # Create a single car wash lane with a capacity of 1 

# Start the car arrival and data collection processes
env.process(car_arrivals(env, carWash))
env.process(collect_data(env, carWash))

env.run(until=simulationTime)  # Run the simulation for the specified time

### Analysis and Output ###
average_wait_time = sum(waitTimes) / len(waitTimes) if waitTimes else 0
average_queue_length = sum(queueLengths) / len(queueLengths) if queueLengths else 0
utilization_rate = sum(carWashLaneUtilization) / len(carWashLaneUtilization) if carWashLaneUtilization else 0
average_arrival_interval = sum(carArrivalIntervals) / len(carArrivalIntervals) if carArrivalIntervals else 0

print("\n")
print(f'Average arrival interval: {average_arrival_interval:.2f} minutes.')
print(f'Average queue length: {average_queue_length:.2f} cars.')
print(f'Average wait time: {average_wait_time:.2f} minutes.')
print(f'Car wash utilization rate: {utilization_rate * 100:.2f}%.')


# Plot results
plt.figure(figsize=(12, 8))

# Average arrival interval plot
plt.subplot(4, 1, 1)
plt.plot(range(1, len(carArrivalIntervals) + 1), carArrivalIntervals, label='Arrival Intervals')
plt.axhline(y=average_arrival_interval, color='r', linestyle='--', label='Average Arrival Interval')
plt.title('Arrival Intervals Over Time')
plt.xlabel('Car Number')
plt.ylabel('Arrival Interval (minutes)')
plt.xticks(range(0, len(carArrivalIntervals) + 1, 1))  # X-axis ticks every 1 car
plt.yticks(range(0, int(max(carArrivalIntervals)) + 1, 1))  # Y-axis ticks every 1 minute
plt.legend()

# Queue length plot
plt.subplot(4, 1, 2)
plt.plot(range(simulationTime), queueLengths)
plt.title('Queue Length Over Time')
plt.xlabel('Time (minutes)')
plt.ylabel('Queue Length')
plt.xticks(range(0, simulationTime + 1, 1))  # X-axis ticks every 1 minute
plt.yticks(range(0, max(queueLengths) + 1, 1))  # Y-axis ticks every 1 car

# Wait time histogram
plt.subplot(4, 1, 3)
plt.hist(waitTimes, bins=10)
plt.title('Wait Time Distribution')
plt.xlabel('Wait Time (minutes)')
plt.ylabel('Number of Cars')
plt.xticks(range(0, int(max(waitTimes)) + 1, 1))  # X-axis ticks every 1 minute

# Car wash lane utilization plot
plt.subplot(4, 1, 4)
plt.plot(range(simulationTime), carWashLaneUtilization)
plt.title('Car Wash Lane Utilization Over Time')
plt.xlabel('Time (minutes)')
plt.ylabel('Utilization')
plt.xticks(range(0, simulationTime + 1, 1))  # X-axis ticks every 1 minutes

plt.tight_layout()
plt.show()
