import numpy
import matplotlib.pyplot as pyplot
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import OBE_Tools as OBE

## Calculate probe absorption as a function of both probe detuning and atomic 
## velocity for a 4-level system, then integrate over the Maxwell-Boltzmann 
## distribution to obtain the Doppler-averaged spectrum.

Omegas = [1,20,10] # 2pi MHz
Deltas = [0,0,0] # 2pi MHz
gammas = [0.1,0.1,0.1] # 2pi MHz
Gammas = [10,1,1] # 2pi MHz
lamdas = numpy.asarray([852, 1470, 843])*1e-9 #m
dirs = numpy.asarray([1,-1, -1]) #unitless direction vectors
ks = dirs/lamdas # 2pi m^-1

Delta_12s = numpy.linspace(-50,50,500)  #2pi MHz
velocities = numpy.linspace(-150, 150, 201) #m/s
probe_abs = numpy.zeros((len(velocities), len(Delta_12s)))
for i, v in enumerate(velocities):
    for j, p in enumerate(Delta_12s):
        Deltas[0] = p
        Deltas_eff = numpy.zeros(len(Deltas))
        for k in range(len(Deltas)):
            Deltas_eff[k] = Deltas[k]+(ks[k]*v)*1e-6 # to convert to MHz
        solution = OBE.fast_n_level(Omegas, Deltas_eff, Gammas, gammas = gammas)
        probe_abs[i,j] = -numpy.imag(solution)

int_manual = numpy.zeros(len(Delta_12s))
pdf = OBE.MBdist(velocities)
vel_step = velocities[-1] - velocities[-2]

#Integrate 'manually' (using rectangle rule)
for i in range(len(Delta_12s)):
    p_slice = probe_abs[:,i]
    weighted = p_slice*pdf*vel_step
    int_manual[i] = numpy.sum(weighted)

colours = ['k', 'w', 'lightgray']
fig, [ax1, ax2] = pyplot.subplots(2,1, figsize = (7,4), sharex = True)
thing = ax1.imshow(probe_abs, aspect = 'auto', origin = 'lower',
              extent = [Delta_12s[0], Delta_12s[-1], velocities[0], velocities[-1]])
for i in range(3):
    # Plot asymptotes
    ax1.plot(Delta_12s, -Delta_12s/(numpy.sum(ks[:i+1])*1e-6), ls = 'dotted', 
    c = colours[i], lw = 1, alpha = 0.9)
pyplot.subplots_adjust(top=0.95,
bottom=0.11,
left=0.11,
right=0.85,
hspace=0.1,
wspace=0.2)

box = ax1.get_position()
(x0, y0, width, height) = box.bounds
gap = 0.01
cax1 = pyplot.axes([x0+width+gap, y0, 0.02, height])
cbar = pyplot.colorbar(thing, cax = cax1, label = r'Probe absorption ($-\Im[\rho_{21}]$)')
ax1.set_ylabel(r'Velocity (m/s)')

ax2.plot(Delta_12s, int_manual)
ax2.plot(Delta_12s, probe_abs[len(velocities)//2,:])
ax2.set_xlabel(r'Probe detuning $\Delta_{12}$ (MHz)')
ax2.set_ylabel('Probe absorption\n' r'($-\Im[\rho_{21}]$)')

in_ax = inset_axes(ax2, width = 1.2, height = 0.95, loc=1)
in_ax.plot(Delta_12s, int_manual, c = 'C0')
in_ax.set_xlim(-45, 45)
in_ax.set_xlabel(r'$\Delta_{12}$')

pyplot.show()
