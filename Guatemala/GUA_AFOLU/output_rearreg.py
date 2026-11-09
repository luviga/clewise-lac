import pandas as pd
import numpy as np
import Auxiliares as AUX

def discount_costs(discount_year, discount_rate, data_output1,nombre_salida):
    df1 = pd.read_csv(data_output1)
 
    #print(list(df1.columns))
    
    if 'Capex'+str(discount_year) not in list(df1.columns):
        col_aux=list()
        for i in range(len(df1)):
            try:
                col_aux.append(df1.iloc[i]['CapitalInvestment']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year)))
            except:
                col_aux.append(np.NaN)
        df1.insert(len(df1.columns),'Capex'+str(discount_year), col_aux)
    else:
        for i in range(len(df1)):
            try:
                df1.iloc[i]['Capex'+str(discount_year)]=df1.iloc[i]['CapitalInvestment']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year))
            except:
                df1.iloc[i]['Capex'+str(discount_year)]=np.NaN     
    
    if 'FixedOpex'+str(discount_year) not in list(df1.columns):    
        col_aux=list()
        for i in range(len(df1)):
            try:
                col_aux.append(df1.iloc[i]['AnnualFixedOperatingCost']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year)))
            except:
                col_aux.append(np.NaN)
        df1.insert(len(df1.columns),'FixedOpex'+str(discount_year), col_aux)
    else:
        for i in range(len(df1)):
            try:
                df1.iloc[i]['FixedOpex'+str(discount_year)]=df1.iloc[i]['AnnualFixedOperatingCost']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year))
            except:
                df1.iloc[i]['FixedOpex'+str(discount_year)]=np.NaN          
    
    if 'VarOpex'+str(discount_year) not in list(df1.columns):     
        col_aux=list()
        for i in range(len(df1)):
            try:
                col_aux.append(df1.iloc[i]['AnnualVariableOperatingCost']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year)))
            except:
                col_aux.append(np.NaN)
        df1.insert(len(df1.columns),'VarOpex'+str(discount_year), col_aux)
    else:
        for i in range(len(df1)):
            try:
                df1.iloc[i]['VarOpex'+str(discount_year)]=df1.iloc[i]['AnnualVariableOperatingCost']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year))
            except:
                df1.iloc[i]['VarOpex'+str(discount_year)]=np.NaN          
    
    if 'Opex'+str(discount_year) not in list(df1.columns):     
        col_aux=list()
        for i in range(len(df1)):
            try:
                col_aux.append(df1.iloc[i]['OperatingCost']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year)))
            except:
                col_aux.append(np.NaN)
        df1.insert(len(df1.columns),'Opex'+str(discount_year), col_aux)
    else:
        for i in range(len(df1)):
            try:
                df1.iloc[i]['Opex'+str(discount_year)]=df1.iloc[i]['OperatingCost']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year))
            except:
                df1.iloc[i]['Opex'+str(discount_year)]=np.NaN              
    
    if 'Externalities'+str(discount_year) not in list(df1.columns):     
        col_aux=list()
        for i in range(len(df1)):
            try:
                col_aux.append(df1.iloc[i]['AnnualTechnologyEmissionPenaltyByEmission']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year)))
            except:
                col_aux.append(np.NaN)
        df1.insert(len(df1.columns),'Externalities'+str(discount_year), col_aux)
    else:
        for i in range(len(df1)):
            try:
                df1.iloc[i]['Externalities'+str(discount_year)]=df1.iloc[i]['AnnualTechnologyEmissionPenaltyByEmission']/((1+discount_rate)**(int(df1.iloc[i]['Year'])-discount_year))
            except:
                df1.iloc[i]['Externalities'+str(discount_year)]=np.NaN
    
    df1=df1.assign(Capex_GDP=np.NaN)
    df1=df1.assign(FixedOpex_GDP=np.NaN)
    df1=df1.assign(VarOpex_GDP=np.NaN)
    df1=df1.assign(Opex_GDP=np.NaN)
    df1=df1.assign(Externalities_GDP=np.NaN)            
    
    df1.to_csv(nombre_salida, index = None, header=True)
    
    

def main():
    # Leer parametros para descontar costos
    discount_book=AUX.LeerExcel('../Code/DiscountCostsParameters.xlsx')
    discount_book_sheets=AUX.ListaHojas(discount_book)
    discount_book_sheet=AUX.LeerHoja2(discount_book,discount_book_sheets[0],0)
    header_sheet_discount=AUX.LeerHeaders(discount_book_sheet)
    discount_year=AUX.LeerCol(discount_book_sheet, header_sheet_discount[0])[0]
    discount_rate=AUX.LeerCol(discount_book_sheet, header_sheet_discount[1])[0]
    
    print("******************************************")
    print("8. Descontando costos del sector AFOLU ...")
    print("******************************************")
    discount_costs(discount_year, discount_rate,'./2_Model/data_land_output.csv','./2_Model/data_land_output.csv')
    discount_costs(discount_year, discount_rate,'./2_Model/BAU/data_land_BAU_Output.csv','./2_Model/BAU/EXP/BAU_0_Output.csv')
    discount_costs(discount_year, discount_rate,'./2_Model/NDP/data_land_NDP_Output.csv','./2_Model/NDP/EXP/NDP_0_Output.csv')
    print("********************")
    print("El proceso finalizó.")
    print("********************")

if __name__== "__main__":
    main()