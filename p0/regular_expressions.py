"""
Esta es la expresion regular para el ejercicio 0, que se facilita
a modo de ejemplo:
"""
RE0 = "[ab]*a"

"""
Completa a continuacion las expresiones regulares para los
ejercicios 1-5:
"""
RE1 = "[abc]*(a[abc]*b|b[abc]*a)[abc]*"
RE2 = "0[.]?|-?([1-9][0-9]*[.]?[0-9]*|0?[.][0-9]+)"
RE3 = "(www.uam.es|moodle.uam.es)[/]([a-z]+[/]?)*"
RE4 = "([1-9][0-9]*[-+*/])*[1-9][0-9]*"
RE5 = "(({}|[(]{}[)])[-+*/])*({}|[(]{}[)])".format(RE4, RE4, RE4, RE4)

"""
Recuerda que puedes usar el fichero test_p0.py para probar tus
expresiones regulares.
"""

