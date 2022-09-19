import json
import boto3
from tkinter import filedialog

iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')
oListaFuncLambda = {}
oListaRuntime = {0:'nodejs',1:'nodejs4.3',2:'nodejs6.10',3:'nodejs8.10',4:'nodejs10.x',5:'nodejs12.x',6:'nodejs14.x',7:'nodejs16.x',8:'java8',9:'java8.al2',
                 10:'java11',11:'python2.7',12:'python3.6',13:'python3.7',14:'python3.8',15:'python3.9',16:'dotnetcore1.0',17:'dotnetcore2.0',18:'dotnetcore2.1',
                 19:'dotnetcore3.1',20:'dotnet6',21:'nodejs4.3-edge',22:'go1.x',23:'ruby2.5',24:'ruby2.7',25:'provided',26:'provided.al2'}
def clearLambdaList():
    while len(oListaFuncLambda) > 0:
        oListaFuncLambda.popitem()
def getLambdaFunctions():
    clearLambdaList()
    oCont=0
    response = lambda_client.list_functions()
    oFunciones = response['Functions']
    for d in oFunciones:
        oListaFuncLambda[oCont]=d['FunctionName']
        oCont+=1
    if len(oListaFuncLambda) > 0:
        print('==== SUS FUNCIONES LAMBDAS SON: ')
        for d in oListaFuncLambda:
            print(oListaFuncLambda[d])
    else:
        print("==== NO CUENTA CON FUNCIONES LAMBDA ====")
def getZip():
    print('SELECCIONE EL ARCHIVO .ZIP CONTENEDOR DEL CODIGO')
    oPath = filedialog.askopenfilename(initialdir="/", title="Select a .zip", filetypes=[("zip files", "*.zip")])
    with open(oPath, 'rb') as f:
        zipped_code = f.read()
    return zipped_code
def displayMenu():
    print('==== Seleccione una accion ====')
    print('[1] Crear funcion lambda')
    print('[2] Crear un rol para lambda')
    print('[3] Detalles de una funcion lambda')
    print('[4] Probar una funcion lambda')
    print('[5] Actualizar una funcion lambda')
    print('[6] Eliminar una funcion lambda')
    print('[0] Finalizar programa')
def displayRuntime():
    oRuntime = ''
    print('==== RUNTIMES DISPONIBLES: ')
    for d in oListaRuntime:
        print('[', d, '] ', oListaRuntime[d])
    try:
        oInputNombre = int(input('Runtime seleccionado: '))
        try:
            oRuntime = oListaRuntime[oInputNombre]
        except Exception as ex:
            print('Seleccion invalida ', ex)
    except ValueError as ex:
        print('Seleccion invalida ', ex)
    return oRuntime
def createLambdaRol():
    role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    response = iam_client.create_role(
        RoleName='LambdaBasicExecution',
        AssumeRolePolicyDocument=json.dumps(role_policy),
    )

    oPrettyJson = json.dumps(response, indent=4)
    print(oPrettyJson)
def getRoles():
    oRoles = iam_client.list_roles()
    oListaRoles = oRoles['Roles']
    print('==== ROLES ACTUALES ====')
    for key in oListaRoles:
        print('Nombre: ',key['RoleName'])
        print('Arn: ',key['Arn'])
def createLambdaFunction():
    try:
        zipped_code = getZip()
        print('FAVOR DE INGRESAR LOS DATOS REQUERIDOS: ')
        oNombreFuncion = input('Ingrese el nombre de la funcion lambda: ')
        oRuntime = displayRuntime()
        oHandler = input('Ingrese nombre de la funcion principal a ejecutar (Handler): ')
        getRoles()
        oRole = input('Ingrese el nombre de rol a utilizar: ')
        role = iam_client.get_role(RoleName=oRole)

        response = lambda_client.create_function(
            FunctionName=oNombreFuncion,
            Runtime=oRuntime,
            Role=role['Role']['Arn'],
            Handler=oHandler,
            Code=dict(ZipFile=zipped_code),
            Timeout=300,  # Maximum allowable timeout
            # Set up Lambda function environment variables
            Environment={
                'Variables': {
                    'Name': oNombreFuncion,
                    'Environment': 'prod'
                }
            },
        )

        oPrettyJson = json.dumps(response, indent=4)
        print(oPrettyJson)
    except Exception as ex:
        print('Accion invalida: ',ex)
def deleteLambdaFunction(oNombreFuncion):
    try:
        response = lambda_client.delete_function(
            FunctionName=oNombreFuncion
        )
        oPrettyJson = json.dumps(response,indent=4)
        print(oPrettyJson)
    except Exception as ex:
        print('==== ',ex)
def getLambdaDescription(oNombreFuncion):
    try:
        response = lambda_client.get_function(
            FunctionName=oNombreFuncion
        )
        oPrettyJson = json.dumps(response, indent=4)
        print(oPrettyJson)
    except Exception as ex:
        print('==== ',ex)
def invokeLambdaFunction(oNombreFuncion):
    test_event = dict()
    try:
        response = lambda_client.invoke(
            FunctionName=oNombreFuncion,
            Payload=json.dumps(test_event),
        )
        print(response['Payload'])
        print(response['Payload'].read().decode("utf-8"))
    except Exception as ex:
        print('==== ',ex)
def updateLambdaFunction(oNombreFuncion):
    try:
        zipped_code = getZip()
        response = lambda_client.update_function_code(
            FunctionName=oNombreFuncion,
            ZipFile=zipped_code
        )

        oPrettyJson = json.dumps(response, indent=4)
        print(oPrettyJson)
    except Exception as ex:
        print('==== ',ex)
def selectLambdaFunction():
    oNombreLambda=''
    oCont=0
    if len(oListaFuncLambda) > 0:
        print('==== SUS FUNCIONES LAMBDAS SON: ')
        for d in oListaFuncLambda:
            print('[',d,'] ',oListaFuncLambda[d])
            oCont+=1
    else:
        print("==== NO CUENTA CON FUNCIONES LAMBDA ====")
    if oCont!= 0:
        try:
            oInputNombre = int(input('Lambda seleccionado: '))
            try:
                oNombreLambda = oListaFuncLambda[oInputNombre]
            except Exception as ex:
                print('Seleccion invalida ',ex)
        except ValueError as ex:
            print('Seleccion invalida ',ex)
    return oNombreLambda

if __name__ == '__main__':
    getLambdaFunctions()
    displayMenu()
    try:
        oInput = int(input('Accion seleccionada: '))
    except ValueError as ex:
        oInput = 999
    while oInput != 0:
        if oInput == 1:
            createLambdaFunction()
        elif oInput == 2:
            createLambdaRol()
        elif oInput == 3:
           oLambdaSeleccionado = selectLambdaFunction()
           getLambdaDescription(oLambdaSeleccionado)
        elif oInput == 4:
            oLambdaSeleccionado = selectLambdaFunction()
            invokeLambdaFunction(oLambdaSeleccionado)
        elif oInput == 5:
            oLambdaSeleccionado = selectLambdaFunction()
            updateLambdaFunction(oLambdaSeleccionado)
        elif oInput == 6:
            oLambdaSeleccionado = selectLambdaFunction()
            deleteLambdaFunction(oLambdaSeleccionado)
        else:
            print('Accion invalida')

        print()
        getLambdaFunctions()
        displayMenu()
        try:
            oInput = int(input('Accion seleccionada: '))
        except ValueError as ex:
            oInput = 999
    print('Finalizando programa . . .')
