from scipy import optimize
from material_structure import *
import numpy as np
from data_structure import *
import matplotlib.pyplot as plt
import time
from tkinter import *
from material_model import *
from tkinter import ttk
import multiprocessing as mp


import functools


def plotScans(data, data_dict, sim_dict, scans):
    """
    Purpose: Plot the all the selected scans
    :param scans: An array containing the scans that you want to plot
    :param data: The two dimensional list that contains scan number and name
    :param data_dict: Data dictionary
    :param sim_dict: Simulation dictionary
    :return:
    """

    my_index = list()  # contains the indices of the appropriate scans
    # Finds the indices of each scan
    for s in scans:
        my_index.append((data[:, 0].astype(int).tolist().index(s)))

    my_scans = data[my_index] # gets all the appropriate scans

    # plot the sample model
    fig_idx = 1
    for s in my_scans:

        name = s[2]  # name of the scan
        scanType = s[1]  # scan type
        scan_num = s[0]  # scan number
        dat = data_dict[name]
        sim = sim_dict[name]
        pol = dat['Polarization']

        if scanType.upper() == 'REFLECTIVITY':
            qz = dat['Data'][0]  # momentum transfer
            R = dat['Data'][2]  # reflectivity
            Rsim = sim['Data'][2]
            plt.figure(fig_idx)
            plt.suptitle('Reflectivity Scan ' + str(scan_num) + ': ' + name)
            plt.plot(qz, R)  # data
            plt.plot(qz, Rsim)  # simulation

            # Change log scale for non-asymmetry scans
            if pol == 'S' or pol == 'P' or pol == 'LC' or pol == 'RC':
                plt.yscale('log')
                plt.ylabel('log(R)')
            else:
                plt.ylabel('A')
            plt.xlabel('Momentum Transfer, qz (A^{-1})')
            plt.legend(['Experiment', 'Simulation'])

        elif scanType.upper() == 'ENERGY':
            E = dat['Data'][3]  # Energy
            R = dat['Data'][2]  # Reflectivity
            Rsim = sim['Data'][2]
            plt.figure(fig_idx)
            plt.suptitle('Energy Scan' + str(scan_num) + ': ' + name)
            plt.plot(E, R)  # data
            plt.plot(E, Rsim)  # simulation

            # Changes the yscale depending on if scan is an asymmetry scan
            if pol == 'S' or pol == 'P' or pol == 'LC' or pol == 'RC':
                plt.yscale('log')
                plt.ylabel('log(R)')
            else:
                plt.ylabel('A')
            plt.xlabel('Energy, E (eV)')
            plt.legend(['Experiment', 'Simulation'])

        fig_idx = fig_idx + 1

    plt.show()
    return

def getScans(data, data_dict, sim_dict, queue):
    """
    Purpose: Asks user what scans they would like to see and use for global optimization.
    :param data: array containing scan number, scan type, and scan name
    :param data_dict: data dictionary
    :param sim_dict: simulation dictionary
    :param queue: multiprocessing queue used to store scans
    :return:
    """
    print('SCAN SELECTION FOR GLOBAL OPTIMIZATION \n')
    print('Select an option:')

    stage1 = {'1': 'Select Scan',
              '2': 'Exit/Finished'}

    stage2 = {'1': 'Use Scan',
              '2': 'Choose Different Scan',
              '3': 'Return',
              '4': 'Exit'}

    stage3 = {'1': 'Select Scan Boundaries',
              '2': 'Use Default Boundary and Weights',
              '3': 'Return',
              '4': 'Exit/Finish'}

    stage4 = {'1': 'Select Scan Boundary Weights',
              '2': 'Use Default Boundary Weights',
              '3': 'Return',
              '4': 'Exit'}


    scanNumberList = list(data[:,0])  # get the scan number list

    scans = list()
    boundaries = list()
    weights = list()

    cont = True

    stg1 = True   # stage 1
    stg2 = False  # stage 2
    stg3 = False  # stage 3
    stg4 = False  # weight selection

    scan = 0
    f = functools.partial(plotScans, data, data_dict, sim_dict)
    while cont:

        # Determines if user wants to select a scan
        if stg1:
            for key in stage1.keys():
                val = stage1[key]
                print('\t'+key+': ' + val)
            toggle = input("\n" + "-> ")
            print()
            if toggle != '1' and toggle != '2':
                while toggle != '1' and toggle != '2':
                    toggle = input('Please select one of the provided options: ')

            if toggle == '2':
                cont = False
            elif toggle == '1':
                stg1 = False
                stg2 = True

        # Determine which scans the user wants to use
        elif stg2:
            print('SCAN SELECTION' + '\n')
            scan = input('Please select scan you would like to view: ')
            while scan not in scanNumberList:
                scan = input('Scan number must be found between '+scanNumberList[0]+' and ' + scanNumberList[-1]+': ')
            while scan in scans:
                scan = input('Scan ' + scan + ' already selected! Choose another scan: ')
            print('\n Select an option: ')

            p = mp.Process(target=f, args=([int(scan)],))
            p.start()
            #p.join()
            for key in stage2.keys():
                val = stage2[key]
                print('\t' + key + ': ' + val)
            toggle = input("\n" + "-> ")
            print()
            if toggle != '1' and toggle != '2' and toggle != '3' and toggle != '4':
                while toggle != '1' and toggle != '2' and toggle != '3' and toggle != '4':
                    toggle = input('Please select one of the provided options: ')

            if toggle == '1':
                scans.append(scan)
                stg2 = False
                stg3 = True
            elif toggle == '2':
                pass
            elif toggle == '3':
                pass
                stg1 = True
                stg2 = False
            elif toggle == '4':
                cont = False

        # Selecting bounds
        elif stg3:
            scanNumber = data[int(scan) - 1][0]
            scanType = data[int(scan) - 1][1]
            scanName = data[int(scan) - 1][2]

            print('\n Choose boundary options:')
            for key in stage3.keys():
                val = stage3[key]
                print('\t' + key + ': ' + val)
            toggle = input("\n" + "-> ")
            print()

            if toggle != '1' and toggle != '2' and toggle != '3' and toggle != '4':
                while toggle != '1' and toggle != '2' and toggle != '3' and toggle != '4':
                    toggle = input('Please select one of the provided options: ')

            if toggle == '1':
                bound = []
                if scanType == 'Reflectivity':
                    qz_up = str(round(data_dict[scanName]['Data'][0][-1],2))
                    qz_lw = str(round(data_dict[scanName]['Data'][0][0],2))
                    bound = input('\n Enter the boundaries for scan ' + scan + ' in terms of qz (' + qz_lw + ', '+qz_up + '): ')

                elif scanType == 'Energy':
                    E_up = str(round(data_dict[scanName]['Data'][3][-1],2))
                    E_lw = str(round(data_dict[scanName]['Data'][3][0],2))
                    bound = input('\n Enter the boundaries for scan ' + scan + ' in terms of qz (' + E_lw + ', ' + E_up + '): ')

                bound = bound.split()
                bound = [ast.literal_eval(bd) for bd in bound]

                prev = 0
                tuple_eval = True
                limit_eval = True
                while tuple_eval or limit_eval:
                    tuple_eval = False
                    limit_eval = False
                    for bd in bound:

                        if type(bd) != tuple:
                            tuple_eval = True
                        elif bd[0] > bd[1] or prev > bd[0]:
                            limit_eval = True
                        prev = bd[1]
                    if tuple_eval:
                        bound = input('Enter the boundaries as tuples, each separated by spaces:')
                        bound = bound.split()
                        bound = [ast.literal_eval(bd) for bd in bound]
                    if limit_eval:
                        bound = input('Make sure boundary limits are in ascending order: ')
                        bound = bound.split()
                        bound = [ast.literal_eval(bd) for bd in bound]

                boundaries.append(bound)
                # go onto next step
                stg3 = False
                stg4 = True
            elif toggle == '2':
                bound = []
                if scanType == 'Reflectivity':
                    qz_up =data_dict[scanName]['Data'][0][-1]
                    qz_lw = data_dict[scanName]['Data'][0][0]
                    bound = [(qz_lw, qz_up)]


                elif scanType == 'Energy':
                    E_up = data_dict[scanName]['Data'][3][-1]
                    E_lw = data_dict[scanName]['Data'][3][0]
                    bound = [(E_lw, E_up)]

                boundaries.append(bound)
                weights.append([1])
                # set boundary and weights to default values
                stg3 = False
                stg1 = True
                p.terminate()
            elif toggle == '3':
                # remove previous selected scan
                scans.pop()
                stg2 = True
                stg3 = False
            elif toggle == '4':
                # set boundary and weights to default and exit
                cont = False

        elif stg4:
            for key in stage4.keys():
                val = stage4[key]
                print('\t' + key + ': ' + val)

            toggle = input("\n" + "-> ")
            print()

            if toggle != '1' and toggle != '2' and toggle != '3' and toggle != '4':
                while toggle != '1' and toggle != '2' and toggle != '3' and toggle != '4':
                    toggle = input('Please select one of the provided options: ')

            if toggle == '1':
                num_weights = len(boundaries[-1])
                weight = input('Input weights for the boundaries selected: ')
                weight = weight.split()
                while len(weight) != num_weights:
                    weight = input('Select '+ str(num_weights)+' weights, each separated by a space: ')
                    weight = weight.split()

                weight = [float(w) for w in weight]

                notFloat = True
                notBig = True
                while notFloat and notBig:
                    notFloat = False
                    notBig = False
                    for w in weight:
                        if type(w) != float:
                            notFloat = True
                        if w<0:
                            notBig = True
                    if notFloat:
                        weight = input('Make sure you enter weight as an integer or float: ')
                    elif notBig:
                        weight = input('Weight must be positive: ')

                weights.append(weight)
                # set weights
                stg1 = True
                stg4 = False


                p.terminate()
            elif toggle == '2':
                # set to default values
                num_weights = len(boundaries[-1])
                weight = [1 for n in range(num_weights)]
                weights.append(weight)
                stg1 = True
                stg4 = False


                p.terminate()
            elif toggle == '3':
                boundaries.pop()  # remove selected boundaries
                # return to previous section
                stg4 = False
                stg3 = True

            elif toggle == '4':
                # set weights to default value and exit
                cont = False

    scanBounds = dict()
    for idx in range(len(boundaries)):
        scanBounds[scans[idx]] = (boundaries[idx], weights[idx])

    queue.put([scans, scanBounds])
    return

def createTable(data):
    """
    Purpose: create a table that shows the scan number and it's info in a new window
    :param data: array containing scan number, scan type, and scan name
    :return:
    """
    # Create a tkinter tree
    ws = Tk()  # create a new window
    ws.title('Scan info')
    ws.geometry('700x250')  # geometry of the new window
    ws['bg'] = '#AC99F2'  # colour of the window

    data_frame = Frame(ws)  # creates a new data frame
    data_frame.pack()  # packs the new data frame

    # initializes the scrollbar
    data_scroll = Scrollbar(data_frame)
    data_scroll.pack(side=RIGHT, fill=Y)

    # sets the scrollbar configurations
    my_data = ttk.Treeview(data_frame, yscrollcommand=data_scroll.set, xscrollcommand=data_scroll.set)
    my_data.pack()
    data_scroll.config(command=my_data.xview)

    # define our column
    my_data['columns'] = ('Scan Number', 'Scan Type', 'Scan Name')

    # format our column
    my_data.column("#0", width=0, stretch=NO)
    my_data.column("Scan Number", anchor=CENTER, width=160)
    my_data.column("Scan Type", anchor=CENTER, width=160)
    my_data.column("Scan Name", anchor=CENTER, width=320)

    # Create Headings
    my_data.heading("#0", text="", anchor=CENTER)
    my_data.heading("Scan Number", text="Scan Number", anchor=CENTER)
    my_data.heading("Scan Type", text="Scan Type", anchor=CENTER)
    my_data.heading("Scan Name", text="Name", anchor=CENTER)

    # insert the data to the data frame
    for idx in range(len(data)):
        my_data.insert(parent='', index='end', iid=idx, text='',
                       values=(data[idx][0], data[idx][1], data[idx][2]))

    my_data.pack()  # pack all of this into the data frame
    ws.mainloop()  # begin an infinite loop that runs until the window is closed

def changeSampleParams(x, parameters, sample):
    """
    Purpose: Change the parameters for the input sample for x-values
    :param x: A list that contains the new parameters values
    :param parameters: A list that defines which parameter to change in the sample definition
    :param sample: A slab object class
    :return: The new sample
    """
    # Loop through each sample parameter
    for p in range(len(parameters)):
        params = parameters[p]

        if params[0] == "SCALING FACTOR":
            sample.scaling_factor = x[p]
        elif params[0] == "BACKGROUND SHIFT":
            sample.background_shift = x[p]
        elif params[0] == 'SCATTERING FACTOR':
            mode =params[1]
            element = params[2]
            dE = x[p]

            if mode == 'STRUCTURAL':
                FfEnergyShift(element, dE, opt=True)
            elif mode == 'MAGNETIC':
                FfmEnergyShift(element, dE, opt=True)
        else:
            layer = params[0]  # Determine which layer to change
            property = params[1]  # structural/polymorphous/magnetic
            if property == 'STRUCTURAL':
                mode = params[2]
                # Determine if user wants to use compound or element mode
                if mode == 'COMPOUND':
                    characteristic = params[3]  # thickness/density/roughness/linked roughness
                    for ele in list(sample.structure[layer].keys()):
                        if characteristic == 'THICKNESS':
                            sample.structure[layer][ele].thickness = x[p]
                        elif characteristic == 'DENSITY':
                            stoich = sample.structure[layer][ele].stoichiometry  # stoichiometry
                            molar_mass = sample.structure[layer][ele].molar_mass  # molar mass
                            sample.structure[layer][ele].density = x[p]*stoich/molar_mass  # set density
                        elif characteristic == 'ROUGHNESS':
                            sample.structure[layer][ele].roughness = x[p]
                        elif characteristic == 'LINKED ROUGHNESS':
                            sample.structure[layer][ele].linked_roughness = x[p]

                elif mode == 'ELEMENT':
                    element = params[3]  # determines the element to change
                    characteristic = params[4]  # thickness/density/roughness/linked roughness
                    if characteristic == 'THICKNESS':
                        sample.structure[layer][element].thickness = x[p]
                    elif characteristic == 'DENSITY':
                        sample.structure[layer][element].density = x[p]
                    elif characteristic == 'ROUGHNESS':
                        sample.structure[layer][element].roughness = x[p]
                    elif characteristic == 'LINKED ROUGHNESS':
                        sample.structure[layer][element].linked_roughness = x[p]


            elif property == 'POLYMORPHOUS':
                element = params[3]  # determines the element that contains the polymorph
                polymorph = params[4]  # determines the polymorph to change

                ratio = 1 - x[p]  # Assumes only two possible polymorphs for now and computes other polymorph ratio

                poly = np.where(sample.structure[layer][element].polymorph == polymorph)  # determines location of polymorph

                # sets poly_ratio value making sure sum equals to 1
                if poly == 0:
                    sample.structure[layer][element].poly_ratio[0] = x[p]
                    sample.structure[layer][element].poly_ratio[1] = ratio
                elif poly == 1:
                    sample.structure[layer][element].poly_ratio[1] = x[p]
                    sample.structure[layer][element].poly_ratio[0] = ratio

            elif property == 'MAGNETIC':
                element = params[3]  # determines the magnetic element to use

                # determines if magnetic element is polymorphous
                if len(params) == 3:
                    sample.structure[layer][element].mag_density[0] = x[p]  # non-polymorphous case
                else:
                    polymorph = params[4]  # polymorphous case
                    poly = np.where(sample.structure[layer][element].polymorph == polymorph)
                    sample.structure[layer][element].mag_density[poly] = x[p]

    return sample

def scanCompute(x, *args):

    chi2 = 0  # what we will use to determine some values

    sample = args[0]  # slab class
    scans = args[1]  # data info
    data = args[2]  # data dict
    sims = args[3]  # simulation dict
    parameters = args[4]  # defines which parameters to change
    scanBounds = args[5]  # defines the bounds of the scans

    sample = changeSampleParams(x, parameters, sample)



    for scan in scans:
        scan_number = int(scan[0])
        scanType = scan[1]
        name = scan[2]
        scanbounds = scanBounds[scan_number]
        xbound = scanbounds[0]
        weights = scanbounds[1]

        if scanType == 'Reflectivity':
            myDataScan = data[name]
            myData = myDataScan['Data']
            E = myDataScan['Energy']
            pol = myDataScan['Polarization']
            qz = np.array(myData[0])
            Rdat = np.log(np.array(myData[2]))
            qz, Rsim = sample.reflectivity(E, qz)
            Rsim = np.log10(Rsim[pol])*sample.scaling_factor + np.ones(len(Rsim[pol]))*sample.background_shift


            for b in range(len(xbound)):
                lw = xbound[b][0]
                up = xbound[b][1]

                w = weights[b]

                idx = [x for x in range(len(qz)) if qz[x] >= lw and qz[x] <= up]

                if len(idx) != 0:
                    chi2 = chi2 + sum((Rdat[idx]-Rsim[idx])**2/abs(Rsim[idx]))*w


            #chi2 = chi2 + sum((Rdat-Rsim)**2/abs(Rsim))

        elif scanType == 'Energy':
            myDataScan = data[name]
            myData = myDataScan['Data']
            Theta = myDataScan['Angle']
            E = np.array(myData[3])
            pol = myDataScan['Polarization']

            Rdat = np.log(np.array(myData[2]))
            Rsim = sample.energy_scan(Theta, E)
            Rsim = np.log(Rsim[pol])

            chi2 = chi2 + sum((Rdat-Rsim)**2/abs(Rsim))

    return chi2

def differential_evolution(fname,scan, parameters, bounds,scanBounds, strat = 'currenttobest1exp', mIter=25, tolerance=0.1, display=False):

    sample = ReadSampleHDF5(fname)  # import the sample information
    data_info, data, sims = ReadDataHDF5(fname)  # import the experimental data and simulated data

    # makes sure that scan is a list
    if type(scan) != list and type(scan) != np.ndarray:
        scan = [scan]

    scan = [s - 1 for s in scan]  # makes sure the indices are correct

    scans = data_info[scan]  # gets the appropriate scans

    params = [sample, scans, data, sims, parameters, scanBounds]  # required format for function scanCompute

    # This line will be used to select and use different global optimization algorithms
    ret = optimize.differential_evolution(scanCompute, bounds, args=params, strategy=strat,
                                          maxiter=mIter, tol=tolerance, disp=display)
    x = ret.x
    fun = ret.fun


    print('Chi: ' + str(fun))
    print('Fitting parameters: ', x)

    return x, fun

def shgo(fname, scan,parameters, bounds, N=64, iterations=3):
    sample = ReadSampleHDF5(fname)  # import the sample information

    f, data_info, data, sims = ReadDataHDF5(fname)  # import the experimental data and simulated data

    # makes sure that scan is a list
    if type(scan) != list or type(scan) != np.ndarray:
        scan = [scan]

    scan = [s - 1 for s in scan]  # makes sure the indices are correct
    scans = data_info[tuple(scan)]

    params = [sample, scans, data, sims, parameters]  # required format for function scanCompute

    ret = optimize.shgo(scanCompute, bounds, args=tuple(params), n=N, iters=iterations)
    x = ret.x
    fun = ret.fun

    print('Chi: ' + str(fun))
    print('Fitting parameters: ', x)

    f.close()
    return x, fun

def dual_annealing(fname, scan, parameters, bounds, mIter=300):
    sample = ReadSampleHDF5(fname)  # import the sample information

    f, data_info, data, sims = ReadDataHDF5(fname)  # import the experimental data and simulated data

    # makes sure that scan is a list
    if type(scan) != list or type(scan) != np.ndarray:
        scan = [scan]

    scan = [s - 1 for s in scan]  # makes sure the indices are correct
    scans = data_info[tuple(scan)]

    params = [sample, scans, data, sims, parameters]  # required format for function scanCompute


    ret = optimize.dual_annealing(scanCompute, bounds, args=params, maxiter=mIter)
    x = ret.x
    fun = ret.fun


    print('Chi: ' + str(fun))
    print('Fitting parameters: ', x)

    f.close()
    return x, fun


def selectOptimize(sample, queue):
    """
    Purpose: Ask the user the parameters they want to optimize
    :param sample:
    :param queue:
    :return:
    """

    # make sure that when element or compound is selected, that the characteristic is no longer available
    sample_params = list()
    upperbound = list()
    lowerbound = list()


    # ----------------------------------------- Parameter Selection -------------------------------------------------- #
    print()
    print('PARAMETER SELECTION')
    print()

    layer_formula = list()
    idx = 0
    for temp_layer in sample.structure:
        P = list()
        M = list()
        formula = ''
        for key in list(temp_layer.keys()):
            stoich = temp_layer[key].stoichiometry
            if stoich == 1:
                formula = formula + key
            else:
                formula = formula + key + str(stoich)
            if len(temp_layer[key].polymorph) > 0:
                P.append(key)
            if len(temp_layer[key].mag_density) > 0:
                M.append(key)

        layer_formula.append([idx, formula, P, M])
        idx = idx + 1

        # Sets up and prints scan table
    header = ['Layer', 'Formula', 'Polymorphs', 'Magnetic']
    tab = PrettyTable(header)
    tab.add_rows(layer_formula)
    print(tab)
    print()
    number_layers = len(sample.structure)

    cont = 'Y'
    while cont.upper() == 'Y':
        layer = input('Select layer you would like to optimize (0-'+str(number_layers-1)+"): ")
        if layer.upper() == 'EXIT':
            return
            #quit()
        while layer.upper() == 'SHOW':
            print(tab)
            print()
            layer = input('Select layer you would like to optimize (0-' + str(number_layers - 1) + "): ")
            if layer.upper() == 'EXIT':
                quit()

        while int(layer) < 0 or int(layer) > number_layers -1:
            layer = input('Select layer you would like to optimize (0-' + str(number_layers - 1) + "): ")
            if layer.upper() == 'EXIT':
                quit()
            while layer.upper() == 'SHOW':
                print(tab)
                print()
                layer = input('Select layer you would like to optimize (0-' + str(number_layers - 1) + "): ")
                if layer.upper() == 'EXIT':
                    quit()

        poly = list()
        mag = list()

        structural = True
        polymorphous = False
        magnetic = False

        layer = int(layer)
        elements = list(sample.structure[layer].keys())
        for ele in elements:
            if len(sample.structure[layer][ele].polymorph) > 0:
                poly.append(ele)
                polymorphous = True
            if len(sample.structure[layer][ele].mag_density) > 0:
                mag.append(ele)
                magnetic = True

        s = 'structural'
        if polymorphous:
            s = s + "/polymorphous"
        if magnetic:
            s = s + "/magnetic"

        prop = input('Select the property you would like to vary ('+ s + ') : ')
        if prop.upper() == 'EXIT':
            quit()
        while prop.upper() != 'STRUCTURAL' and prop.upper() != 'POLYMORPHOUS' and prop.upper() != 'MAGNETIC':
            prop = input('Please select one of the properties (' + s + ') : ')
            if prop.upper() == 'EXIT':
                quit()

        if prop.upper() == 'STRUCTURAL':
            mode = input('Select mode (element/compound): ')
            if mode.upper() == 'EXIT':
                quit()
            while mode.upper() != 'ELEMENT' and mode.upper() != 'COMPOUND':
                mode = input('Please select (element/compound): ')
                if mode.upper() == 'EXIT':
                    quit()

            if mode.upper() == 'COMPOUND':
                char_list = ['THICKNESS','DENSITY', 'ROUGHNESS', 'LINKED ROUGHNESS']
                val = 'y'
                while val.upper() == 'Y' and len(char_list) > 0:
                    characteristic = input('Select characteristic (' + '/'.join([char.lower() for char in char_list]) + '): ')
                    if characteristic.upper() == 'EXIT':
                        quit()
                    while characteristic.upper() != 'THICKNESS' and characteristic.upper() != 'DENSITY' and characteristic.upper() != 'ROUGHNESS' and characteristic.upper() != 'LINKED ROUGHNESS':
                        characteristic = input('Select characteristic (' + '/'.join([char.lower() for char in char_list]) + '): ')
                        if characteristic.upper() == 'EXIT':
                            quit()

                    if characteristic.upper() == 'THICKNESS' and 'THICKNESS' in char_list:
                        char_list.remove('THICKNESS')
                        lw = 1
                        up = 0
                        while float(lw) > float(up):
                            lw = input('Select lower bound in units of Angstrom: ')
                            if lw.upper() == 'EXIT':
                                quit()
                            up = input('Select upper bound in units of Angstrom: ')
                            if up.upper() == 'EXIT':
                                quit()

                        lowerbound.append(lw)
                        upperbound.append(up)
                    if characteristic.upper() == 'DENSITY' and 'DENSITY' in char_list:
                        char_list.remove('DENSITY')
                        lw = 1
                        up = 0
                        while float(lw) > float(up):
                            lw = input('Select lower bound in units of g/cm^3: ')
                            if lw.upper() == 'EXIT':
                                quit()
                            up = input('Select upper bound in units of g/cm^3: ')
                            if up.upper() == 'EXIT':
                                quit()
                        lowerbound.append(lw)
                        upperbound.append(up)
                    if characteristic.upper() == 'ROUGHNESS' and 'ROUGHNESS' in char_list:
                        char_list.remove('ROUGHNESS')
                        lw = 1
                        up = 0
                        while float(lw) > float(up):
                            lw = input('Select lower bound in units of Angstrom: ')
                            if lw.upper() == 'EXIT':
                                quit()
                            up = input('Select upper bound in units of Angstrom: ')
                            if up.upper() == 'EXIT':
                                quit()
                        lowerbound.append(lw)
                        upperbound.append(up)
                    if characteristic.upper() == 'LINKED ROUGHNESS' and 'LINKED ROUGHNESS' in char_list:
                        char_list.remove('LINKED ROUGHNESS')
                        lw = 1
                        up = 0
                        while float(lw) > float(up):
                            lw = input('Select lower bound in units of Angstrom: ')
                            if lw.upper() == 'EXIT':
                                quit()
                            up = input('Select upper bound in units of Angstrom: ')
                            if up.upper() == 'EXIT':
                                quit()
                        lowerbound.append(lw)
                        upperbound.append(up)

                    print()
                    sample_params.append([layer,prop.upper(),mode.upper(),characteristic.upper()])

                    if len(char_list) > 0:
                        val = input('Would you like to select another characteristic (y/n)?')
                    else:
                        val = 'N'


            elif mode.upper() == 'ELEMENT':
                char_list = ['THICKNESS','DENSITY', 'ROUGHNESS', 'LINKED ROUGHNESS']
                val = 'y'
                while val.upper() == 'Y':
                    element = input('Select element (' + str(elements) + ") : ")
                    while element not in elements:
                        element = input('Please select element in list (' + str(elements) + ") : ")

                    again = 'y'
                    while again.upper() == 'Y' and len(char_list)>0:
                        characteristic = input('Select characteristic (' + '/'.join([char.lower() for char in char_list]) + '): ')
                        while characteristic.upper() != 'THICKNESS' and characteristic.upper() != 'DENSITY' and characteristic.upper() != 'ROUGHNESS' and characteristic.upper() != 'LINKED ROUGHNESS':
                            characteristic = input('Select characteristic (' + '/'.join([char.lower() for char in char_list]) + '): ')

                        if characteristic.upper() == 'THICKNESS' and 'THICKNESS' in char_list:
                            char_list.remove('THICKNESS')
                            lw = 1
                            up = 0
                            while float(lw) > float(up):
                                lw = input('Select lower bound in units of Angstrom: ')
                                if lw.upper() == 'EXIT':
                                    quit()
                                up = input('Select upper bound in units of Angstrom: ')
                                if up.upper() == 'EXIT':
                                    quit()
                            lowerbound.append(lw)
                            upperbound.append(up)
                        if characteristic.upper() == 'DENSITY' and 'DENSITY' in char_list:
                            char_list.remove('DENSITY')
                            lw = 1
                            up = 0
                            while float(lw) > float(up):
                                lw = input('Select lower bound in units of mol/cm^3: ')
                                if lw.upper() == 'EXIT':
                                    quit()
                                up = input('Select upper bound in units of mol/cm^3: ')
                                if up.upper() == 'EXIT':
                                    quit()
                            lowerbound.append(lw)
                            upperbound.append(up)
                        if characteristic.upper() == 'ROUGHNESS' and 'ROUGHNESS' in char_list:
                            char_list.remove('ROUGHNESS')
                            lw = 1
                            up = 0
                            while float(lw) > float(up):
                                lw = input('Select lower bound in units of Angstrom: ')
                                if lw.upper() == 'EXIT':
                                    quit()
                                up = input('Select upper bound in units of Angstrom: ')
                                if up.upper() == 'EXIT':
                                    quit()
                            lowerbound.append(lw)
                            upperbound.append(up)
                        if characteristic.upper() == 'LINKED ROUGHNESS' and 'LINKED ROUGHNESS' in char_list:
                            char_list.remove('LINKED ROUGHNESS')
                            lw = 1
                            up = 0
                            while float(lw) > float(up):
                                lw = input('Select lower bound in units of Angstrom: ')
                                if lw.upper() == 'EXIT':
                                    quit()
                                up = input('Select upper bound in units of Angstrom: ')
                                if up.upper() == 'EXIT':
                                    quit()
                            lowerbound.append(lw)
                            upperbound.append(up)

                        print()
                        sample_params.append([layer,prop.upper(),mode.upper(),element, characteristic.upper()])
                        if len(char_list) > 0:
                            again = input('Would you liked to select another characteristic for '+ element+" (y/n): ")
                        else:
                            again = 'N'
                    val = input('Would you like to select another element (y/n)?')
        elif prop.upper() == "POLYMORPHOUS":
            b= []
            for ele in elements:
                if len(sample.structure[layer][ele].polymorph) > 0:
                    b.append(ele)
            poly_cont = 'Y'
            while poly_cont.upper() == 'Y' and len(b) > 0:
                poly_ele = input('Select the polymorph '+ str(b) +' you would liked to vary: ')
                if poly_ele.upper() == 'EXIT':
                    quit()

                num_poly = len(b)

                while poly_ele not in b:
                    poly_ele = input('Please select a polymorph ' + str(b) + ' : ')
                    if poly_ele.upper() == 'EXIT':
                        quit()


                polymorph = sample.structure[layer][poly_ele].polymorph
                whichPoly = input('Select polymorph (' + str(polymorph) + ') for which density you would like to vary?')
                if whichPoly.upper() == 'EXIT':
                    quit()
                while whichPoly not in polymorph:
                    whichPoly = input('Select polymorph (' + str(polymorph) + ') for which density you would like to vary?')
                    if whichPoly.upper() == 'EXIT':
                        quit()

                lw = input("Select the lower limit of the polymorph ratio (0-1): ")
                if lw.upper() == 'EXIT':
                    quit()
                up = input("Select the upper limit of the polymorph ratio (0-1): ")
                if up.upper() == 'EXIT':
                    quit()

                while(float(lw)>float(up) or float(lw)<0 or float(up) > 1):
                    if float(lw)>float(up):
                        lw = input("Make sure that your lower bound is smaller than the upper bound. Please select a new lower limit: ")
                        if lw.upper() == 'EXIT':
                            quit()
                        up = input("Please select a new upper bound: ")
                        if up.upper() == 'EXIT':
                            quit()
                    if float(lw) < 0:
                        lw = input("Please select a lower limit between 0 and 1: ")
                        if lw.upper() == 'EXIT':
                            quit()
                    if float(up) > 1:
                        up = input("Please select an upper limit between 0 and 1: ")
                        if up.upper() == 'EXIT':
                            quit()

                lowerbound.append(lw)
                upperbound.append(up)

                sample_params.append([layer, prop.upper(), poly_ele, whichPoly])
                # As of right now we will assume that we can have a maximum of 2 polymorphs
                print()
                if len(b) != 0:
                    b.remove(poly_ele)
                    poly_cont = input('Would you like to vary another polymorph in the same layer (y/n): ')
                    if poly_cont.upper() == 'EXIT':
                        quit()

        elif prop.upper() == 'MAGNETIC':
            my_mag = list()
            for ele in elements:
                if len(sample.structure[layer][ele].mag_density) > 0:
                    my_mag.append(ele)

            mag_ele = input('Select magnetic element you would like to vary (' + str(my_mag) + ': ')
            if mag_ele.upper() == 'EXIT':
                quit()
            while mag_ele not in my_mag:
                mag_ele = input('Please select an element element in (' + str(my_mag) + ': ')
                if mag_ele.upper() == 'EXIT':
                    quit()

            mag_poly = list(sample.structure[layer][mag_ele].polymorph)
            mag_cont = 'Y'
            while(mag_cont.upper() == 'Y' and len(my_mag)>0):
                if len(mag_poly) > 0:
                    mag_poly_cont = 'Y'
                    while(mag_poly_cont.upper() == 'Y' and len(mag_poly)>0):
                        whichMag = input('Select which polymorph ('+str(mag_poly)+') for which you would like to vary the magnetic density: ')
                        if whichMag.upper() == 'EXIT':
                            quit()
                        while whichMag not in mag_poly:
                            whichMag = input('Select which polymorph ('+str(mag_poly)+') for which you would like to vary the magnetic density: ')
                            if whichMag.upper() == 'EXIT':
                                quit()

                        lw = input('Enter the lower bound of the magnetic density of order mol/cm^3: ')
                        if lw.upper() == 'EXIT':
                            quit()
                        up = input('Enter the lower bound of the magnetic density of order mol.cm^3: ')
                        if up.upper() == 'EXIT':
                            quit()
                        while float(lw) > float(up):
                            lw = input('Make sure lower bound is smaller than upper bound. Enter lower bound again: ')
                            if lw.upper() == 'EXIT':
                                quit()
                            up = input('Enter upper bound: ')
                            if up.upper() == 'EXIT':
                                quit()
                        lowerbound.append(lw)
                        upperbound.append(up)

                        sample_params.append([layer, prop.upper(), mag_ele, whichMag])
                        print()
                        if len(mag_poly) != 0:
                            mag_poly_cont = input('Would you like to vary another polymorph magnetic density (y/n)?')
                            if mag_poly_cont.upper() == 'EXIT':
                                quit()
                            mag_poly.remove(whichMag)

                else:
                    lw = input('Enter the lower bound of the magnetic density of order mol/cm^3: ')
                    if lw.upper() == 'EXIT':
                        quit()
                    up = input('Enter the lower bound of the magnetic density of order mol.cm^3: ')
                    if up.upper() == 'EXIT':
                        quit()
                    while float(lw) > float(up):
                        lw = input('Make sure lower bound is smaller than upper bound. Enter lower bound again: ')
                        if lw.upper() == 'EXIT':
                            quit()
                        up = input('Enter upper bound: ')
                        if up.upper() == 'EXIT':
                            quit()
                    lowerbound.append(lw)
                    upperbound.append(up)
                    print()
                    sample_params.append([layer, prop.upper(), mag_ele])
                if len(my_mag) != 0:
                    my_mag.remove(mag_ele)
                    mag_cont = input('Would you like to select another magnetic element to vary (y/n)?')
                    if mag_cont.upper() == 'EXIT':
                        quit()

        cont = input('Would you liked to select another layer (y/n): ')


    # printing the chosen elements
    my_params = list()

    for sp in range(len(sample_params)):
        temp_list = list()
        params = sample_params[sp]
        lw = lowerbound[sp]
        up = upperbound[sp]

        temp_list.append(params[0])  # Layer info
        temp_list.append(params[1])  # Property

        if params[1] == 'STRUCTURAL':
            mode = params[2]  # mode
            if mode == 'COMPOUND':
                formula = layer_formula[sp][1]  # formula
                characteristic = params[3]
                temp_list.append(formula)
                temp_list.append(characteristic)
            else:
                element = params[3]
                characteristic = params[4]
                temp_list.append(element)
                temp_list.append(characteristic)
        elif params[1] == 'POLYMORPHOUS':
            temp_list.append(params[2])  # poly element
            temp_list.append(params[3])  # which poly
            temp_list.append('DENSITY RATIO')
        elif params[1] == 'MAGNETIC':
            if len(params) == 3:
                temp_list.append(params[2])  # element
                temp_list.append('MAGNETIC DENSITY')
            else:
                temp_list.append(params[2])  # poly element
                temp_list.append(params[3])  # polymorph
                temp_list.append('MAGNETIC DENSITY')

        temp_list.append(lw)
        temp_list.append(up)
        my_params.append(temp_list)



    header = ['Layer', 'Property', 'Element(s)', 'Polymorph', 'Characteristic', 'Upper Bound', 'Lower Bound']
    Ntab = PrettyTable(header)
    Ntab.add_rows(my_params)

    print(Ntab)
    bounds = list(zip(lowerbound, upperbound))
    queue.put([my_params,bounds])

def getGlobOptParams(fname):
    # Load in the sample information
    sample = ReadSampleHDF5(fname)

    # load in the data and simulation data
    data, data_dict, sim_dict = ReadDataHDF5(fname)  # file must remain open as we process the dataset

    # Running the two tasks at once
    f1 = functools.partial(createTable, data)
    queue = mp.Queue()

    p1 = mp.Process(target=f1)
    p1.start()

    p2 = mp.Process(target=getScans(data, data_dict, sim_dict, queue))
    p2.start()

    p2.join()
    p1.terminate()

    scans = queue.get()

    queue1 = mp.Queue()
    # show the current scans
    # scans = [1,2,3,4,5]

    f3 = functools.partial(plotScans, scans, data, data_dict, sim_dict)

    p4 = mp.Process(target=sample.showSampleParameters)
    p4.start()

    p3 = mp.Process(target=f3)
    p3.start()

    p5 = mp.Process(target=selectOptimize(sample, queue1))
    p5.start()

    p5.join()
    p3.terminate()
    p4.terminate()

    val = queue1.get()
    parameters = val[0]
    bounds = val[1]

    return scans, parameters, bounds

def createBoundsDatatype(fname, scans, sBounds, sWeights=None):

        scanBounds = dict()

        info, data_dict, sim_dict = ReadDataHDF5(fname)  # need for data info

        # make sure the number of bounds, number of weights, and scans are all the same
        ns = len(scans)
        nB = len(sBounds)
        if sWeights != None:
            nW = len(sWeights)
            if ns != nB or ns != nW:
                raise SyntaxError('Make sure that the number of bounds, scans, and weights all have the same length.')
        else:
            if ns != nB:
                raise SyntaxError('Make sure that the number of bounds and scans all have the same length.')

        for s in range(ns):
            scan = scans[s]
            scanType = info[scan-1][1]  # retrieve the scan type this
            bound = sBounds[s]  # retrieve the scan's proper bounds
            nb = len(bound)
            if sWeights != None:
                weight = sWeights[s]  # retrieve the scan's proper weights
                nw = len(weight)

                if nb != nw:
                    raise SyntaxError('Make sure every scan has the same number of bounds and weights.')

            else:
                weight = [1 for i in range(nb)]



            # check to make sure that the bounds are in the proper range
            for b in bound:
                up = b[0]
                low = b[1]
                if scanType == 'Reflectivity':

                    if up < 0 or up > 1:
                        raise ValueError('Scan ' + str(scan) + ': Upper bound momentum transfer bounds should be found between 0 and 1')
                    if low < 0 or low> 1:
                        raise ValueError('Scan ' + str(scan) + ': Lower bound momentum transfer bounds should be found between 0 and 1')

                elif scanType == 'Energy':
                    if up < 1 or low < 1:
                        raise ValueError('Bounds for energy scan appear to be set for a reflectivity scan ')

            scanBounds[scan] = (bound, weight)

        return scanBounds

def comparisonScanPlots(fname, x, parameters, scans):

    sample = ReadSampleHDF5(fname)  # get the previous sample version
    info, data_dict, sim_dict = ReadDataHDF5(fname)  # get the sample data and simulation data
    newSample = changeSampleParams(x, parameters, sample)  # change to globally optimized parameters

    scans = [s-1 for s in scans]
    info = info[scans]  # retrieve only the needed scans

    figNum = 1
    for idx in range(len(info)):
        scanNumber = info[idx][0]
        scanType = info[idx][1]
        scanName = info[idx][2]

        pol = data_dict[scanName]['Polarization']
        dat = data_dict[scanName]['Data']
        sim = sim_dict[scanName]['Data']
        if scanType == 'Reflectivity':

            E = data_dict[scanName]['Energy']

            qz = dat[0]
            R = dat[2]
            Rsim = sim[2]

            qz, Rnew = newSample.reflectivity(E,qz)
            Rnew = Rnew[pol]

            plt.figure(figNum)
            plt.suptitle('Reflectivity Scan: ' + scanName)
            plt.plot(qz, R)
            plt.plot(qz, Rsim)
            plt.plot(qz, Rnew)
            plt.legend(['Data', 'Current Model', 'Optimized Model'])
            plt.xlabel('Momentum Transfer, qz (A^{-1})')
            if pol == 'S' or pol == 'P' or pol=='LC' or pol=='RC':
                plt.yscale('log')
                plt.ylabel('log(R)')
            else:
                plt.ylabel('A')

        elif scanType == 'Energy':
            Theta = data_dict[scanName]['Angle']

            E = dat[3]
            R = dat[2]
            Rsim = sim[2]

            E, Rnew = newSample.energy_scan(Theta, E)
            Rnew = Rnew[pol]

            plt.figure(figNum)
            plt.suptitle('Energy Scan: ' + scanName)
            plt.plot(E, R)
            plt.plot(E, Rsim)
            plt.plot(E, Rnew)
            plt.legend(['Data', 'Current Model', 'Optimized Model'])
            plt.xlabel('Energy, E (eV)')
            if pol == 'S' or pol == 'P' or pol=='LC' or pol=='RC':
                plt.yscale('log')
                plt.ylabel('log(R)')
            else:
                plt.ylabel('A')
        figNum = figNum + 1

    plt.show()
    return

if __name__ == "__main__":
    sample = slab(8)

    sample.addlayer(0, 'SrTiO3', 50, density=[0.027904, 0.027904, 0.083712], roughness=[7.58207, False, 5.77093])
    sample.addlayer(1, 'SrTiO3', 6, density=[0, 0.027904, 0], roughness=[7.58207, 4.03102, 5.77093])

    sample.addlayer(2, 'LaMnO3', 4, density=[0.021798, 0.0209, 0.084], roughness=[3.77764, 2, 2],
                    linked_roughness=[False, 0.5, False])
    sample.polymorphous(2, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(2, ['Mn2+', 'Mn3+'], [0.025, 0], ['Co', 'Ni'])

    sample.addlayer(3, 'LaMnO3', 17.8, density=[0.021798, 0.0209, 0.084], roughness=[3.77764, 2, 2])
    sample.polymorphous(3, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(3, ['Mn2+', 'Mn3+'], [0.025, 0], ['Co', 'Ni'])

    sample.addlayer(4, 'LaMnO3', 9, density=[0.021798, 0.0209, 0.084], roughness=[3.77764, 2, 2])
    sample.polymorphous(4, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(4, ['Mn2+', 'Mn3+'], [0.016, 0], ['Co', 'Ni'])

    sample.addlayer(5, 'LaMnO3', 2.5, density=[0.025, 0.024, 0.05], roughness=[0.25, 0.25, 2])
    sample.polymorphous(5, 'Mn', ['Mn2+', 'Mn3+'], [1, 0], sf=['Mn', 'Fe'])
    sample.magnetization(5, ['Mn2+', 'Mn3+'], [0.016, 0], ['Co', 'Ni'])

    sample.addlayer(6, 'LaMnO3', 4.5, density=[0.025, 0.042, 0.04], roughness=[0.25, 0.25, 2])
    sample.polymorphous(6, 'Mn', ['Mn2+', 'Mn3+'], [0.4, 0.6], sf=['Mn', 'Fe'])
    sample.magnetization(6, ['Mn2+', 'Mn3+'], [0.0053, 0], ['Co', 'Ni'])

    sample.addlayer(7, 'CCO', 11.1, density=[0.05, 0.05, 0.01], roughness=2, linked_roughness=[3, 1.5, False])

    fname = 'Pim10uc.h5'

    #sample.plot_density_profile(1)
    #plt.show()
    #WriteSampleHDF5(fname, sample)
    #print(ReadDataHDF5(fname))
    queue = mp.Queue()
    data, data_dict, sim_dict = ReadDataHDF5(fname)
    getScans(data, data_dict, sim_dict, queue)
    print(queue.get())
    """
    parameters = [[1, 'STRUCTURAL', 'COMPOUND', 'THICKNESS'],
                  [2, 'STRUCTURAL', 'COMPOUND', 'THICKNESS'],
                  [3, 'STRUCTURAL', 'COMPOUND', 'THICKNESS'],
                  [4, 'STRUCTURAL', 'COMPOUND', 'THICKNESS']]


    lw = [3.5,3.5,17.3,8.5]
    up = [6.5,6.5,19.8,11.5]
    bounds = list(zip(lw, up))
    scans = [1,2,3,4,5,6]

    # determines the bounds for the scans
    sBounds = [[(0.1,0.8)],
               [(0.1,0.3),(0.3,0.5),(0.6,0.8)],
               [(0.1,0.6),(0.7,0.8)],
               [(0.1,0.5)],
               [(0.2,0.6),(0.6,0.8)],
               [(0.1,0.8)]]

    # Determines the weights you want to use for each bound
    sWeights = [[1],
                [1,0.2,0.5],
                [1,0.1],
                [0.5],
                [1,0.8],
                [0.7]]

    scanBounds = createBoundsDatatype(fname, scans, sBounds, sWeights=sWeights)
    start = time.time()
    x, fun = differential_evolution(fname, scans, parameters, bounds, scanBounds, mIter=10, display=True, tolerance=1e-6)
    end = time.time()
    print(end-start)
    
    comparisonScanPlots(fname, x, parameters, scans)
    """
