def default_FD_data() -> list:
    qFieldTarget = 20e6 #target rate sm3/d
    PRi = 276 #reservoir pressure bara
    IGIP = 270e9 #Initial gas in place
    abandonmentRate = 5e6 
    TR = 92 #reservoir temperature [C]
    gasMolecularWeight = 16 #[g/mol]
    C_t = 40288.1959178652#Ct, Tubing flow coefficient (2100 MDx0.15 ID  m)
    S = 0.155#tubing elevation coefficient
    C_FL = 283126.866184114#flowline coefficient from template-PLEM (5000x0.355  ID m)
    C_PL = 275064.392725841#CPL Pipeline coefficient from PLEM-Shore (158600x0.68  ID m)
    P_sep =30 #seperator pressure in bara
    N_temp = 3 #number of templates
    NWellsPerTemplate = 3 #number of wells per template
    C_R = 1000 #inflow backpressure coefficient
    n = 1 #Inflow backpressure exponent
    upTime = 365
    buildup_period = 3 #years
    list = [qFieldTarget, PRi, abandonmentRate, TR, gasMolecularWeight, C_R, n, N_temp, NWellsPerTemplate, upTime, C_t, S, C_FL, C_PL, P_sep, IGIP, buildup_period]
    return list

def defaultData_RP() -> list:
    PRi = 276 #reservoir pressure bara
    IGIP = 270e9 #Initial gas in place   
    TR = 92 #reservoir temperature [C]
    gasMolecularWeight = 16 #[g/mol]
    list = [PRi, TR, gasMolecularWeight, IGIP]
    return list

def default_data_NPV() -> list:
    GAS_Price = 0.1 #uds/Sm^3
    Discount_Rate = 5 #%
    nr_wells_per_year = 4
    CAPEX_period = 5
    list = [GAS_Price, Discount_Rate, nr_wells_per_year, CAPEX_period]
    return list

def default_data_NPV_CAPEX() -> list:
    well_cost = 100 #MUSD
    p_u = 500 #MUSD, Pipeline and umbilicals
    Mani = 20 #MUSD , Cost Per Subsea Manifold  
    LNG_unit_cost = 160 #usd/ Sm^3/d
    LNG_carrier_cost= 200 #1E6 USD
    list = [well_cost, p_u, Mani, LNG_unit_cost, LNG_carrier_cost]
    return list

def default_data_NPV_OPEX() -> list:
    well_cost = 200 #1E06 USD
    list = [well_cost]
    return list

def default_well_distribution(NWellsPerTemplate, N_temp, prod_stop, Max_Number_Wells) -> list:
    def_well_list = [0 for _ in range(prod_stop)]
    
    nr_wells = NWellsPerTemplate * N_temp

    if nr_wells % Max_Number_Wells == 0:
        well_count = 0
        for i in range(prod_stop):
            def_well_list[i] = Max_Number_Wells
            well_count += Max_Number_Wells
            if well_count == nr_wells:
                break
    else:
        well_count = 0
        for i in range(prod_stop):
            if well_count + Max_Number_Wells <= nr_wells:
                def_well_list[i] = Max_Number_Wells
                well_count += Max_Number_Wells
            else:
                def_well_list[i] = nr_wells - well_count
                well_count = nr_wells
            if well_count == nr_wells:
                break
    return def_well_list

def default_template_distribution(def_well_list, N_temp, NWellsPerTemp, prod_stop):
    def_temp_list = [0] * prod_stop
    temp_count = sum(def_temp_list)

    free_slots = 0
    for i in range(prod_stop):
        while def_temp_list[i]*NWellsPerTemp < (def_well_list[i]-free_slots) and temp_count < N_temp:
            def_temp_list[i] += 1
            temp_count +=1
        free_slots += def_temp_list[i]*NWellsPerTemp-def_well_list[i]
        if temp_count == N_temp:
            break
    return def_temp_list

def default_MC():
    list1 = ['Gas Price [USD/Sm3]', 'IGIP [Sm3]', 'LNG Plant [USD/Sm3/d]']    
    list2 = [0.05,250000000000, 100] 
    list3 = [0.5,300000000000, 220]
    return list1, list2, list3 

