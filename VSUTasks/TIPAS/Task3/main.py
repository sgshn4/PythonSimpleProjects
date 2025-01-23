import matplotlib.pyplot as plt

# Parameters
# Refrigerator
min_temperature_refrigeration_compartment = -2
target_temperature_refrigeration_compartment = 3
cooling_rate_refrigeration_compartment = 0.5
heating_rate_refrigeration_compartment = 1
# Freezer
min_temperature_freezer_compartment = -20
target_temperature_freezer_compartment = -10
cooling_rate_freezer_compartment = 0.2
heating_rate_freezer_compartment = 1

# Other parameters
simulation_time = 240
time_step = 1

current_temperature_refrigeration_compartment = 20
current_temperature_freezer_compartment = 20
time = 0
temperatures_refrigeration = []
temperatures_freezer = []
time_points = []

# Simulation
while time <= simulation_time:
    # Refrigerator
    if current_temperature_refrigeration_compartment > target_temperature_refrigeration_compartment:
        current_temperature_refrigeration_compartment -= cooling_rate_refrigeration_compartment * time_step
    else:
        current_temperature_refrigeration_compartment += heating_rate_refrigeration_compartment * time_step

    if current_temperature_refrigeration_compartment < min_temperature_refrigeration_compartment:
        current_temperature_refrigeration_compartment = min_temperature_refrigeration_compartment

    temperatures_refrigeration.append(current_temperature_refrigeration_compartment)

    # Freezer
    if current_temperature_freezer_compartment > target_temperature_freezer_compartment:
        current_temperature_freezer_compartment -= cooling_rate_freezer_compartment * time_step
    else:
        current_temperature_freezer_compartment += heating_rate_freezer_compartment * time_step

    if cooling_rate_freezer_compartment < min_temperature_freezer_compartment:
        current_temperature_freezer_compartment = min_temperature_freezer_compartment

    temperatures_freezer.append(current_temperature_freezer_compartment)
    time_points.append(time)

    time += time_step

plt.subplot(2, 1, 1)
plt.plot(time_points, temperatures_refrigeration, label='Refrigerator')
plt.title("Refrigerator")
plt.xlabel("Time (m)")
plt.ylabel("Temp")
plt.grid()

plt.subplot(2, 1, 2)
plt.plot(time_points, temperatures_freezer, label='Freezer')
plt.title("Freezer")
plt.xlabel("Time (m)")
plt.ylabel("Temp")
plt.grid()
plt.show()
