import pandas as pd
from Data.Storage.Cache import SessionState
import pages.GUI.GUI_functions as GUI
from Data.DefaultData import default_FD_data
import streamlit as st

class DryGasAnalysis():
    def __init__(self, session_id:str, inputs:list = [], method:str = None, precision:str = None, field:str = 'No field chosen'):
        self.__parameters:list = inputs
        self.__method = method
        self.__precision = precision
        self.__field = field
        self.__session_id = session_id
        self.__result = pd.DataFrame()
        self.__state = SessionState.get(id=session_id, result=[], method=[], precision=[], field=[])      
    
    def updateFromDropdown(self, method, precision):
            self.__method, self.__precision = method, precision
    def updateField(self, fieldName):
         self.__field = fieldName  
    def get_current_field(self):
        return self.__field   
    def get_current_method(self):
        return self.__method
    def get_current_precision(self):
        return self.__precision
    def get_current_result(self):
        return self.__result

    def updateParameterListfromTable(self):
        list1 = ['Target Rate [sm3/d]', 'Initial Reservoir Pressure [bara]', 'Rate of Abandonment [sm3/d]', 'Reservoir Temperature [degree C]', 'Gas Molecular Weight [g/mol]', 'Inflow backpressure coefficient', 'Inflow backpressure exponent', 'Number of Templates', 'Number of Wells per Template', 'Uptime [days]', 'Tubing Flow Coefficient', 'Tubing Elevation Coefficient', 'Flowline Coefficient from Template-PLEM', 'Pipeline coefficient from PLEM-Shore', 'Seperator Pressure [bara]', 'Initial Gas in Place [sm3]', 'Build-up period [years]']
        self.__parameters = (GUI.display_FD_variables_table(list1=list1, list2=default_FD_data(), edible=True))
        def validate_parameters(list1 = self.__parameters):
            if list1[0] <= 0:
                st.error("Target Rate [sm3/d] must be greater than 0")
                st.stop()            
            if list1[1] <= 0:
                st.error("Initial Reservoir Pressure [bare] must be greater than 0")
                st.stop()
            if list1[2] <= 0:
                st.error('Rate of Abandonment [sm3/d] must be greater than 0')
                st.stop()
            if list1[3] < -273.15:
                st.error("'Reservoir Temperature can not be lower than -273.15 degree C'")
                st.stop()
            if list1[4] <= 0:
                st.error('Gas Molecular Weight [g/mol] must greater than 0')
                st.stop()  
            if list1[7] <= 0:
                st.error('Number of Templates must be greater than 0')
                st.stop()  
            if list1[8] <= 0:
                st.error('Number of Wells per Template must be greater than 0')
                st.stop()  
            if list1[9] <= 0:
                st.error('Uptime [days] must be greater than 0')
                st.stop()
            if list1[9] > 365:
                st.error('Uptime [days] must be less than or equal 365 days')
                st.stop()  
            if list1[14] <= 0:
                st.error('Seperator Pressure [Bara] must be greater than 0')
                st.stop() 
            if list1[15] <= 0:
                st.error('Initial Gas in Place [sm3] must be greater than 0]')
                st.stop()  
            if list1[16] <= 0:
                st.error('Build-up period [years] must be greater than 0')
                st.stop()
            if isinstance(list1[16], float):
                if list1[16].is_integer():
                    pass
                else:
                    st.error('Build-up period [years] must be a whole number')
                    st.stop()
            if isinstance(list1[7], float):
                if list1[7].is_integer():
                    pass
                else:
                    st.error('Number of Templates must be a whole number')
                    st.stop()
            if isinstance(list1[8], float):
                if list1[8].is_integer():
                    pass
                else:
                    st.error('Number of Wells per Template must be a whole number')
                    st.stop()  
            if isinstance(list1[9], float):
                if list1[9].is_integer():
                    pass
                else:
                    st.error('Uptime [days] must be a whole number')
                    st.stop()
        validate_parameters()

    def run(self):
        self.append_method(self.__method)
        self.append_precision(self.__precision)
        self.append_field(self.__field)
        self.append_parameters(self.__parameters)

        if self.__method == 'IPR':
            from Modules.FIELD_DEVELOPMENT.IPR.IPRAnalysis import IPRAnalysis
            df = IPRAnalysis(self.__precision, self.__parameters)
        else:
            from Modules.FIELD_DEVELOPMENT.Nodal.NodalAnalysis import NodalAnalysis
            df = NodalAnalysis(self.__precision, self.__parameters)
        self.__result = df
        return df
    
    def run_field(self, field):
        self.append_method(self.__method)
        self.append_precision(self.__precision)
        self.append_field(field)

        if self.__method == 'IPR':
            from Modules.FIELD_DEVELOPMENT.IPR.IPRAnalysis import IPRAnalysis
            df = IPRAnalysis(self.__precision, self.__parameters)
        else:
            from Modules.FIELD_DEVELOPMENT.Nodal.NodalAnalysis import NodalAnalysis
            df = NodalAnalysis(self.__precision, self.__parameters)
        import Data.dataProcessing as dP
        df = dP.addActualProdYtoDF(field, df)
        df = dP.addProducedYears(field, df)
        return df
    
    def plot(self, comp=False):
        import streamlit as st
        from pandas import DataFrame
        res = self.getResult()
        if comp == False:
            for i in reversed(range(len(res))):
                if isinstance(res[i], DataFrame):
                    field = self.getField()
                    method = self.getMethod()
                    prec = self.getPrecision()
                    st.header('Prod-profile: ' + str(i + 1), divider='red')
                    if field[i] != 'No field chosen':
                        st.write(method[i], prec[i], field[i])
                        GUI.multi_plot([res[i]], addProduced=True)
                    else:
                        st.write(method[i], prec[i])
                        GUI.multi_plot([res[i]], addAll=False)
        else:
            dfs = []
            for df in self.__state.result:
                reset_ind_df = df.reset_index(drop = True)
                dfs.append(reset_ind_df)
            st.header('Compared models', divider='red')
            GUI.multi_plot(dfs, addAll=False)
    
    def clear_output(self):
        from Data.Storage.Cache import SessionState
        SessionState.delete(id = 'DryGasAnalysis')
        self.__state = SessionState.get(self.__session_id, result=[], method=[], precision=[], field=[])
    
    def getMethod(self) -> str:
        session_state = self.__state.get(self.__session_id)
        return getattr(session_state, 'method', None)

    def getPrecision(self) -> str:
        session_state = self.__state.get(self.__session_id)
        return getattr(session_state, 'precision', None)

    def getResult(self) -> list:
        session_state = self.__state.get(self.__session_id)
        return getattr(session_state, 'result', [])

    def getParameters(self) -> pd.DataFrame:
        session_state = self.__state.get(self.__session_id)
        return getattr(session_state, 'parameters', pd.DataFrame())
    
    def getField(self) -> pd.DataFrame:
        session_state = self.__state.get(self.__session_id)
        return getattr(session_state, 'field', pd.DataFrame())

    def getState(self) -> SessionState:
        session_state = self.__state.get(self.__session_id)
        return session_state

    def get_production_profile(self, opt) -> list:
        Fr = self.getResult()[opt-1]['Field rates [sm3/d]'].to_list()
        return Fr
       
    def append_method(self, item) -> str:
        SessionState.append(id = self.__session_id, key = 'method', value = item)

    def append_precision(self, item) -> str:
        SessionState.append(id = self.__session_id, key = 'precision', value = item)

    def append_result(self, item) -> str:
        SessionState.append(id = self.__session_id, key = 'result', value = item)

    def append_parameters(self, item) -> str:
        SessionState.append(id = self.__session_id, key = 'parameters', value = item)
    
    def append_field(self, item) -> str:
        SessionState.append(id = self.__session_id, key = 'field', value = item)

class NPVAnalysis(DryGasAnalysis):
    from Modules.FIELD_DEVELOPMENT.Artificial_lift import artificial_lift_class
    def __init__(self, parent, Analysis, opt):
        self._Analysis = Analysis
        self._opt = opt
        self._CAPEX = []
        self._OPEX = []
        self._NPV_variables = []
        self._sheet = []
        self.parent  = parent
        self._data_For_NPV_sheet = []
        self._production_profile = Analysis.get_production_profile(opt = opt)
   
        #const_NPV_toggle = st.toggle("constant Gas Price and Discount rate ", value=True, label_visibility="visible")


        #self.__sheet.display_table_NPV_Sheet()
        #NPV_str = str("Final NPV: " + str(self.__sheet.get_final_NPV().round(1)) + ' 1E6 USD')
        #st.title(NPV_str)

class NPV_dry_gas(NPVAnalysis):
    def __init__(self, parent, Analysis, opt):
        super().__init__(parent, Analysis, opt)
              
    def NPV_gas_field_update_edible_tables(self):
        from Data.DefaultData import default_data_NPV, default_data_NPV_CAPEX, default_data_NPV_OPEX
        NPV = ['Gas Price', 'Discount Rate', 'Max Number of Wells Drilled per Year', 'CAPEX Period Prior to Production Startup']
        CAPEX = ["Well Cost", 'Pipeline & Umbilicals', 'Subsea Manifold Cost', 'LNG Plant (Default Scales with Rate)', 'LNG Vessels (Default Scales with Rate)']
        OPEX = ["OPEX"]
        NPV_units =['USD/Sm3', '%', '-', 'Years']
        CAPEX_units =['1E6 USD', '1E6 USD', '1E6 USD', '1E6 USD', '1E6 USD']
        OPEX_units = ['1E6 USD']


        col0, col1, col2 = st.columns(3)
        with col0:
            st.title("NPV variables")
            self.__NPV_variables = (GUI.display_table_NPV(list1=NPV, list2=default_data_NPV(), list3 = NPV_units, edible=True, key = 'df_table_editor_NPV'))
        with col1:
            st.title('CAPEX variables')
            self.__CAPEX = (GUI.display_table_NPV(list1=CAPEX, list2=default_data_NPV_CAPEX(plateau = (self._Analysis.getParameters())[self._opt][0], uptime=(self._Analysis.getParameters())[self._opt][9]), list3= CAPEX_units, edible=True, key = 'df_table_editor2_CAPEX'))
        with col2:
            st.title('OPEX variables')
            self.__OPEX = (GUI.display_table_NPV(list1=OPEX, list2=default_data_NPV_OPEX(), list3 = OPEX_units, edible=True, key = 'df_table_editor2_OPEX'))
        
        
        #self.__data_For_NPV_sheet = [self.__NPV_variables, self.__CAPEX, self.__OPEX]
        #self.__sheet = NPV_sheet(parent = NPVAnalysis, Analysis= self.__Analysis, opt = self.__opt)
        #self.__Analysis = Analysis
        #self.__opt = opt
        #self.__production_profile = Analysis.get_production_profile(opt = opt)

        #self.__NPV_variables = user_input[0]
        #self.__CAPEX = user_input[1]
        #self.__OPEX = user_input[2]
        #self.__sheet = self.display_table_NPV_Sheet(key)
            
    def dry_gas_NPV_calc_sheet(self, key='dry_gas_NPV_Sheet'):

        #field development parameters
        self._OPEX_cost = float(self.__OPEX[0])
        self._param = (self._Analysis.getParameters())[self._opt]
        self._N_temp = self._param[7]
        self._N_Wells_per_Temp = self._param[8]
        self._uptime = int(self._param[9])
        self._buildUp_length = int(self._param[16])

        #NPV table 

        self._Gas_Price = self.__NPV_variables[0]
        self._discount_rate = self.__NPV_variables[1]
        self._Max_Well_per_year_nr = int(self.__NPV_variables[2])
        if self._Max_Well_per_year_nr <= 0:
            st.error("Max Number of Wels Drilled per Year must be greater than 0")
            st.stop()
        self._CAPEX_period_prior = int(self.__NPV_variables[3])
        if self._CAPEX_period_prior < 1:
            st.error("CAPEX Period Prior to Production Startup must be greater than 0")
            st.stop()


        #CAPEX table 
        from Data.DefaultData import default_well_distribution, default_template_distribution
        self._end_prod = int(len(self._production_profile)+ (self._CAPEX_period_prior-1))

        self._def_well_list  = default_well_distribution(self._N_temp, self._N_Wells_per_Temp, self._end_prod, self._Max_Well_per_year_nr)
        self._templ_list = default_template_distribution(self._def_well_list, self._N_temp, self._N_Wells_per_Temp, self._end_prod)
        
        self._Well_Cost = self.__CAPEX[0]
        self._p_u = self.__CAPEX[1]
        self._p_u_list = [self._p_u, self._p_u]
        for i in range(2, self._end_prod):
            self._p_u_list.append(0)
        
        self._Mani = self.__CAPEX[2]
        self._LNG_plant = self.__CAPEX[3]
        self._LNG_vessels = self.__CAPEX[4]

        self._LNG_plant_list = [self._LNG_plant/2, self._LNG_plant/2]
        self._LNG_vessels_list = [self._LNG_vessels/2, self._LNG_vessels/2]
        for i in range(2, self._end_prod):
            self._LNG_plant_list.append(0)
            self._LNG_vessels_list.append(0)

        self._DRILLEX =[element * self._Well_Cost for element in self._def_well_list]
        my_list = []

        # if self.__buildUp_length != 0:
        #     self.__buildup_rate = self.__production_profile[0]/self.__buildUp_length
        #     for i in range(self.__buildUp_length):        
        #         my_list.append(i*self.__buildup_rate)
        #self.__daily_gas_offtake = my_list + (self.__production_profile)

        self._yearly_gas_offtake = [0 for i in range (self._CAPEX_period_prior-1)] + [element * self._uptime for element in self._production_profile]
        self.__NPV_prod_profile = [0 for i in range (self._CAPEX_period_prior-1)] + self._production_profile
        
        self._m_c_list = [element * self._Mani for element in self._templ_list]
        years = []         
        for i in range(self._end_prod):
            years.append(i)            

        self._total_CAPEX = [sum(x) for x in zip(self._DRILLEX, self._p_u_list, self._m_c_list, self._LNG_plant_list, self._LNG_vessels_list)]
        self._revenue = [offtake/(1000000) * self._Gas_Price for offtake in self._yearly_gas_offtake]
        self._OPEX_list = [0 for i in range (self._CAPEX_period_prior)] +  [self._OPEX_cost for i in range (int(len(self._production_profile)-1))]
        import numpy as np
        self._cash_flow = [sum(x) for x in zip(self._revenue, np.negative(self._total_CAPEX), np.negative(self._OPEX_list))]
        self._discounted_cash_flow = [self._cash_flow[i]/(1+self._discount_rate/100)**i for i in range(len(self._cash_flow))]
        self._NPV_list = [sum(self._discounted_cash_flow[0:(i+1)]) for i in range(self._end_prod)]


        df_table = pd.DataFrame({
            'Year': years,
            'Nr Wells': self._def_well_list,
            'Nr Manifolds': self._templ_list,
            'DRILLEX': self._DRILLEX,
            'Pipeline & Umbilicals': self._p_u_list,
            'Manifold & Compressors': self._m_c_list,
            'LNG Plant' : self._LNG_plant_list,
            'LNG Vessels' : self._LNG_vessels_list,
            'Other': [0 for element in years],
            'TOTAL CAPEX': self._total_CAPEX,
            'Gas Offtake per Day[sm3/d]':self.__NPV_prod_profile,
            'Yearly gas offtake [sm3]': self._yearly_gas_offtake,
            'Revenue [1E6 USD]': self._revenue,
            'OPEX': self._OPEX_list,
            'Cash Flow': self._cash_flow,
            'Discounted Cash Flow': self._discounted_cash_flow,
            'NPV': self._NPV_list,
        })
        def make_pretty(styler):
            styler.set_properties(**{'background-color': 'pink'})
            #styler.set_caption("Weather Conditions")
            #styler.background_gradient(axis=None, vmin=1, vmax=5, cmap="YlGnBu")
            #styler.set_table_styles([{'selector': 'tr:hover', 'props': 'background-color: yellow; font-size: 1em;'}])
            return styler
        #st.dataframe(df_table.style.pipe(make_pretty))

    #     st.dataframe(
    #        # df_table.style.set_properties(**{'background-color': 'pink'}),
    #        df_table.style.set_caption("Weather Conditions")

        # def highlight_max(x, color):
        #     return np.where(x != 100, f"color: {color};", None)
        # styled_df = st.dataframe(df_table.style.map(highlight_max, color='red'))
        edited_df = st.data_editor(df_table, key=key, use_container_width=True, height=500, hide_index=True)
        
        #return edited_df['Nr Wells'].to_list(), edited_df['DRILLEX'].to_list()

    def get_final_NPV(self):
        return round(self._NPV_list[-1], 1)


