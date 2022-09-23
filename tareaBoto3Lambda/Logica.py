import json
import boto3
from tkinter import filedialog
iam_client = boto3.client('iam')
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
oListaFuncLambda = {}
oListaS3 = {}
oListaRuntime = {0: 'nodejs', 1: 'nodejs4.3', 2: 'nodejs6.10', 3: 'nodejs8.10', 4: 'nodejs10.x', 5: 'nodejs12.x',
                 6: 'nodejs14.x', 7: 'nodejs16.x', 8: 'java8', 9: 'java8.al2',
                 10: 'java11', 11: 'python2.7', 12: 'python3.6', 13: 'python3.7', 14: 'python3.8', 15: 'python3.9',
                 16: 'dotnetcore1.0', 17: 'dotnetcore2.0', 18: 'dotnetcore2.1',
                 19: 'dotnetcore3.1', 20: 'dotnet6', 21: 'nodejs4.3-edge', 22: 'go1.x', 23: 'ruby2.5',
                 24: 'ruby2.7', 25: 'provided', 26: 'provided.al2'}
class Metodos:
    @staticmethod
    def clearLambdaList():
        while len(oListaFuncLambda) > 0:
            oListaFuncLambda.popitem()

    @staticmethod
    def getLambdaFunctions():
        Metodos.clearLambdaList()
        oCont = 0
        response = lambda_client.list_functions()
        oFunciones = response['Functions']
        for d in oFunciones:
            oListaFuncLambda[oCont] = d['FunctionName']
            oCont += 1
        if len(oListaFuncLambda) > 0:
            print('==== SUS FUNCIONES LAMBDAS SON: ')
            for d in oListaFuncLambda:
                print(oListaFuncLambda[d])
        else:
            print("==== NO CUENTA CON FUNCIONES LAMBDA ====")

    @staticmethod
    def getS3List():
        oCont = 0
        response = s3_client.list_buckets()
        oS3 = response['Buckets']
        for d in oS3:
            oListaS3[oCont] = d['Name']
            oCont += 1
        if len(oListaS3) > 0:
            print('==== SUS BUCKETS SON: ')
            for d in oListaS3:
                print(oListaS3[d])
        else:
            print("==== NO CUENTA BUCKETS LAMBDA ====")

    @staticmethod
    def getZip():
        print('SELECCIONE EL ARCHIVO .ZIP CONTENEDOR DEL CODIGO')
        oPath = filedialog.askopenfilename(initialdir="/", title="Select a .zip", filetypes=[("zip files", "*.zip")])
        with open(oPath, 'rb') as f:
            zipped_code = f.read()
        return zipped_code

    def asignBucket(oNombreFuncion):

        try:
            Metodos.getS3List()
            oS3 = Metodos.selectS3()
            oLambdaARN = Metodos.getArnLambda(oNombreFuncion)
            oStatementID = input('Ingresar StatementID nuevo: ')
            response = lambda_client.add_permission(
                StatementId=oStatementID,
                FunctionName=oNombreFuncion,
                Action='lambda:InvokeFunction',
                Principal='s3.amazonaws.com',
                SourceArn='arn:aws:s3:::' + oS3,
            )

            oPrettyJson = json.dumps(response, indent=4)
            print(oPrettyJson)
            responseBucket = s3_client.put_bucket_notification_configuration(
                Bucket=oS3,
                NotificationConfiguration={'LambdaFunctionConfigurations': [
                    {'LambdaFunctionArn': oLambdaARN, 'Events': ['s3:ObjectCreated:*']}]})
            oPrettyJsonBucket = json.dumps(responseBucket, indent=4)
            print(oPrettyJsonBucket)
        except Exception as ex:
            print('Accion invalida: ', ex)

    @staticmethod
    def displayMenu():
        print('==== Seleccione una accion ====')
        print('[1] Crear funcion lambda')
        print('[2] Crear un rol para lambda')
        print('[3] Detalles de una funcion lambda')
        print('[4] Probar una funcion lambda')
        print('[5] Actualizar una funcion lambda')
        print('[6] Eliminar una funcion lambda')
        print('[7] Asignar Bucket a funcion lambda')
        print('[0] Finalizar programa')

    @staticmethod
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

    @staticmethod
    def createLambdaRol():
        try:
            oNombreRol = input('Ingrese el nombre del nuevo rol: ')
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
                RoleName=oNombreRol,
                AssumeRolePolicyDocument=json.dumps(role_policy),
            )

            oPrettyJson = json.dumps(response, indent=4)
            print(oPrettyJson)
        except Exception as ex:
            print('==== ', ex)

    @staticmethod
    def getRoles():
        oRoles = iam_client.list_roles()
        oListaRoles = oRoles['Roles']
        print('==== ROLES ACTUALES ====')
        for key in oListaRoles:
            print('Nombre: ', key['RoleName'])
            print('Arn: ', key['Arn'])

    @staticmethod
    def createLambdaFunction():
        try:
            zipped_code = Metodos.getZip()
            print('FAVOR DE INGRESAR LOS DATOS REQUERIDOS: ')
            oNombreFuncion = input('Ingrese el nombre de la funcion lambda: ')
            oRuntime = Metodos.displayRuntime()
            oHandler = input('Ingrese nombre de la funcion principal a ejecutar (Handler): ')
            Metodos.getRoles()
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
            print('Accion invalida: ', ex)

    def deleteLambdaFunction(oNombreFuncion):
        try:
            response = lambda_client.delete_function(
                FunctionName=oNombreFuncion
            )
            oPrettyJson = json.dumps(response, indent=4)
            print(oPrettyJson)
        except Exception as ex:
            print('==== ', ex)

    def getLambdaDescription(oNombreFuncion):
        try:
            response = lambda_client.get_function(
                FunctionName=oNombreFuncion
            )
            oPrettyJson = json.dumps(response, indent=4)
            print(oPrettyJson)
        except Exception as ex:
            print('==== ', ex)

    def getArnLambda(oNombreFuncion):
        try:
            response = lambda_client.get_function(
                FunctionName=oNombreFuncion
            )
            oFuncion = response['Configuration']
            return oFuncion['FunctionArn']
        except Exception as ex:
            print('==== ', ex)

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
            print('==== ', ex)

    def updateLambdaFunction(oNombreFuncion):
        try:
            zipped_code = Metodos.getZip()
            response = lambda_client.update_function_code(
                FunctionName=oNombreFuncion,
                ZipFile=zipped_code
            )

            oPrettyJson = json.dumps(response, indent=4)
            print(oPrettyJson)
        except Exception as ex:
            print('==== ', ex)

    @staticmethod
    def selectLambdaFunction():
        oNombreLambda = ''
        oCont = 0
        if len(oListaFuncLambda) > 0:
            print('==== SUS FUNCIONES LAMBDAS SON: ')
            for d in oListaFuncLambda:
                print('[', d, '] ', oListaFuncLambda[d])
                oCont += 1
        else:
            print("==== NO CUENTA CON FUNCIONES LAMBDA ====")
        if oCont != 0:
            try:
                oInputNombre = int(input('Lambda seleccionado: '))
                try:
                    oNombreLambda = oListaFuncLambda[oInputNombre]
                except Exception as ex:
                    print('Seleccion invalida ', ex)
            except ValueError as ex:
                print('Seleccion invalida ', ex)
        return oNombreLambda

    @staticmethod
    def selectS3():
        oNombreS3 = ''
        oCont = 0
        if len(oListaS3) > 0:
            print('==== SUS BUCKETS SON: ')
            for d in oListaS3:
                print('[', d, '] ', oListaS3[d])
                oCont += 1
        else:
            print("==== NO CUENTA CON BUCKETS ====")
        if oCont != 0:
            try:
                oInputNombre = int(input('Bucket seleccionado: '))
                try:
                    oNombreS3 = oListaS3[oInputNombre]
                except Exception as ex:
                    print('Seleccion invalida ', ex)
            except ValueError as ex:
                print('Seleccion invalida ', ex)
        return oNombreS3