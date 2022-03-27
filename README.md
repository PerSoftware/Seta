# Seta
> A tool language which is used for mathematical and physical calculations

## What's Seta
Seta is a tool language, to calculate mathematical and physical expressions. Sure, it's our developers' aim. Now Seta is being developed, so the Seta source code is publish not for releasing, but for receiving suggestions. In order to make it better, please give us suggestions about the development of Seta if you are glad to.
In the future, the Seta releases will register 4 extensions, they are:
**.seta** Seta source files
**.setao** Seta operation instruction files
**.setac** Compiled Seta source files (operation code)
**.setad** Seta dynamic linking libraries
Seta now only uses one of the four, it's **.setao**. However, this type of file will be used less in the future because much more code than a normal source code. What's more, Seta's operations are also designing.
In the future, Seta's users may not include many software developers (because they or you can get the answer faster and easier by prgramming in other languages like Python, C/C++ or Java), but perhaps some people who do not have the ability to code will choose Seta, to avoid learning the syntax that is difficult or useless for calculating of other languages.

## Why Seta
Seta as a tool language, has a math-like and easy expression of calculations, but in other general programming calculations, it may be much more difficult.
For example, finding the integral of function $f(x)=3x+ln(x)$.
In **Seta 3.1** in the future:
```
symbol x, y;
f = 3*x+ln(x);
F = integrate(f, x)
display(F)
```

In **Python** (Python 3):
```python
import sympy
sympy.init_printing()
x = sympy.Symbol('x')
f = 3*x + sympy.ln(x)
F = sympy.integrate(f, x)
print(F)
```
> Note: to use Python for symbolic computation or advanced mathematical operations, you'd better use *sympy* library. Use tool *pip* to install it before running the script.

If you usually code in other languages such as C++ or Java, it is much more difficult. So Seta is really a perfect choice.

## Download & Install
Seta now has not been developed well yet, so no available version to download/install. However, you can download its source code to develop one to fit yourself, or give us some suggestions. If your suggestions are really very useful or important, we will express our gratitube to you by E-mail, and by showing your GitHub nickname if you allow us to show (we'll send you an E-mail to ask for permission).
### Debug Version Downloading
The debug version is uploaded to this GitHub project. You can downlaod it from GitHub.
### Release Version Downloading
Sorry, no release versions are published.
### Installations
Sorry, no release versions are published.
