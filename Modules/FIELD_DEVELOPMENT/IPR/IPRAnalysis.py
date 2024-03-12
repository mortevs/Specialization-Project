from Data.DefaultData import default_FD_data

def IPRAnalysis(precision: str, parameters: list = default_FD_data()):
    if precision == 'EXPLICIT':
        from Modules.FIELD_DEVELOPMENT.IPR.dfIPRExplicit import IPROnly
    elif precision == 'IMPLICIT': 
        from Modules.FIELD_DEVELOPMENT.IPR.dfIPRImplicit import IPROnly
    else:
        import streamlit as st
        st.write("Precision is not explicit or implicit")
        st.write(precision)
        
    df = IPROnly(*parameters)
    df.columns=('QFieldTarget [sm3/d]', 'qWellTarget[sm3/d]', 'Reservoir pressure [bara]', 'Z-factor', ' Minimum bottomhole pressure [bara]', 'Potential rates per well [sm3/d]', 'Potential field rates [sm3/d]', 'Field rates [sm3/d]', 'Well production rates [sm3/d]', 'yearly gas offtake [sm3]', 'Cumulative gas offtake [sm3]', 'Recovery Factor', 'Bottomhole pressure [bara]')
    df = swapColumns(df, 'QFieldTarget [sm3/d]', 'Field rates [sm3/d]')
    return df

def swapColumns(df, col1, col2):
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df





      




      


