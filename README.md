# auto-diff-edu
Simple automatic differentiation via operator overloading for educational purposes

Test math: <img alt="$x^2$" src="https://rawgit.com/parrt/auto-diff-edu/master/images/6177db6fc70d94fdb9dbe1907695fce6.svg?invert_in_darkmode" align=middle width="15.947580000000002pt" height="26.76201000000001pt"/>.

<p align="center"><img alt="$$&#10;\frac{\partial f}{\partial t_i}&#10;$$" src="https://rawgit.com/parrt/auto-diff-edu/master/images/45bcb54039e646e45cec0be94b284481.svg?invert_in_darkmode" align=middle width="21.049214999999997pt" height="36.27789pt"/></p>

or <img alt="$\pdv{f}{t_i}$" src="https://rawgit.com/parrt/auto-diff-edu/master/images/a1b874849f8b8aa121b207dbe8bdf3e7.svg?invert_in_darkmode" align=middle width="17.901014999999997pt" height="30.648420000000016pt"/> or <img alt="$\frac{\partial Q}{\partial t}$" src="https://rawgit.com/parrt/auto-diff-edu/master/images/31fcef5ad89935bf7afdd77634d19492.svg?invert_in_darkmode" align=middle width="18.08037pt" height="30.648420000000016pt"/>.

partial deriv op: <img alt="$\pderivative{x}$" src="https://rawgit.com/parrt/auto-diff-edu/master/images/5cda281458913c6ad3139bb18eaf69c5.svg?invert_in_darkmode" align=middle width="15.182144999999998pt" height="28.926479999999973pt"/>.

## Notes

Build README.md from README.tex.md via:

```bash
python -m readme2tex --username parrt --project auto-diff-edu \
  --rerender --svgdir images --usepackage physics \
  --output README.md README.tex.md
```