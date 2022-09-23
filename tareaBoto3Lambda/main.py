from Logica import Metodos
if __name__ == '__main__':
    Metodos.getLambdaFunctions()
    Metodos.displayMenu()
    try:
        oInput = int(input('Accion seleccionada: '))
    except ValueError as ex:
        oInput = 999
    while oInput != 0:
        if oInput == 1:
            Metodos.createLambdaFunction()
        elif oInput == 2:
            Metodos.createLambdaRol()
        elif oInput == 3:
            oLambdaSeleccionado = Metodos.selectLambdaFunction()
            Metodos.getLambdaDescription(oLambdaSeleccionado)
        elif oInput == 4:
            oLambdaSeleccionado = Metodos.selectLambdaFunction()
            Metodos.invokeLambdaFunction(oLambdaSeleccionado)
        elif oInput == 5:
            oLambdaSeleccionado = Metodos.selectLambdaFunction()
            Metodos.updateLambdaFunction(oLambdaSeleccionado)
        elif oInput == 6:
            oLambdaSeleccionado = Metodos.selectLambdaFunction()
            Metodos.deleteLambdaFunction(oLambdaSeleccionado)
        elif oInput == 7:
            oLambdaSeleccionado = Metodos.selectLambdaFunction()
            Metodos.asignBucket(oLambdaSeleccionado)
        else:
            print('Accion invalida')

        print()
        Metodos.getLambdaFunctions()
        Metodos.displayMenu()
        try:
            oInput = int(input('Accion seleccionada: '))
        except ValueError as ex:
            oInput = 999
    print('Finalizando programa . . .')
