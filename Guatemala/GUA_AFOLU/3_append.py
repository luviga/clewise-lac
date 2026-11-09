import pandas as pd

def archivo_resultados():
    ############
    sector = 'land'
    ############
    
    sce = ['BAU','NDC','LTS']
    
    dfacum= pd.DataFrame()
    
    for z in sce:
        data_output_name = './2_Model/'+z+'/data_'+sector+'_'+z+ '_Output.csv'
        df1 = pd.read_csv(data_output_name)
        dfacum=dfacum._append(df1)
    
    dfacum.to_csv( './2_Model/data_land_output.csv', index = None, header=True)
    

def archivo_entradas():
    ############
    sector = 'land'
    ############
    
    sce = ['BAU','NDC','LTS']
    
    dfacum= pd.DataFrame()
    
    for z in sce:
        data_output_name = './2_Model/'+z+'/data_'+sector+'_'+z+ '_Input.csv'
        df1 = pd.read_csv(data_output_name)
        dfacum=dfacum._append(df1)
    
    dfacum.to_csv( './2_Model/data_land_input.csv', index = None, header=True)


def main():
    print("******************************************")
    print("7. Creando resultados del sector AFOLU ...")
    print("******************************************")
    archivo_resultados()
    archivo_entradas()
    print("********************")
    print("El proceso finalizó.")
    print("********************")

if __name__== "__main__":
    main()